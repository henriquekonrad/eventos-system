# services/checkin_service.py
"""
Service de Check-in: Contém toda a lógica de negócio.
Padrão Service Layer: Separa lógica de negócio da apresentação.
"""
from typing import Optional, Dict, Tuple
from repositories.checkin_repository import CheckinRepository
from repositories.inscrito_repository import InscritoRepository
from repositories.pending_repository import PendingRepository
from services.api_service import APIService
from config.settings import APIConfig, APIKeys
import uuid

class CheckinService:
    """
    Gerencia toda a lógica de check-in.
    Padrão Facade: Simplifica interface complexa de múltiplos repositórios.
    """
    
    def __init__(self):
        self.checkin_repo = CheckinRepository()
        self.inscrito_repo = InscritoRepository()
        self.pending_repo = PendingRepository()
        self.api_service = APIService()
    
    def verificar_checkin_existente(self, inscricao_id: str) -> Optional[Dict]:
        """
        Verifica se check-in já existe.
        Retorna status ou None
        """
        return self.checkin_repo.exists_by_inscricao(inscricao_id)
    
    def verificar_checkin_por_cpf(self, cpf: str, evento_id: str) -> Optional[Dict]:
        """
        Verifica se check-in existe por CPF em um evento.
        Útil para check-in rápido.
        """
        # Busca inscrição por CPF
        inscrito = self.inscrito_repo.find_by_cpf(cpf, evento_id)
        
        if not inscrito:
            return None
        
        # Verifica se tem check-in
        checkin_status = self.checkin_repo.exists_by_inscricao(inscrito['inscricao_id'])
        
        if not checkin_status:
            return None
        
        return {
            "existe": True,
            "sincronizado": checkin_status['sincronizado'],
            "inscricao_id": inscrito['inscricao_id']
        }
    
    def registrar_checkin_normal(
        self, 
        inscricao_id: str, 
        evento_id: str,
        nome: str,
        cpf: str,
        email: str
    ) -> Tuple[bool, str]:
        """
        Registra check-in para inscrição existente.
        Retorna (sucesso, mensagem)
        """
        # Verifica se já tem check-in
        checkin_status = self.checkin_repo.exists_by_inscricao(inscricao_id)
        
        if checkin_status:
            if checkin_status['sincronizado']:
                return (False, "✓ CHECK-IN JÁ REGISTRADO NO SERVIDOR\n→ PODE ENTRAR")
            else:
                return (False, "⚠️ CHECK-IN JÁ REGISTRADO (LOCALMENTE)\n→ PODE ENTRAR")
        
        # Tenta buscar IDs reais se estiver online
        ingresso_id = None
        usuario_id = None
        
        if self.api_service.is_online():
            try:
                # Busca ingresso
                ingresso_data = self.api_service.buscar_ingresso(inscricao_id)
                if ingresso_data:
                    ingresso_id = ingresso_data.get("id") or ingresso_data.get("ingresso_id")
                
                # Busca usuário
                usuario_data = self.api_service.buscar_usuario_por_email(email)
                if usuario_data:
                    usuario_id = usuario_data.get("id") or usuario_data.get("usuario_id")
            except Exception as e:
                print(f"[SERVICE] Erro ao buscar dados: {e}")
        
        # Monta URL apropriada
        if ingresso_id and usuario_id:
            # Tem dados completos - usa endpoint normal
            url = f"{APIConfig.CHECKINS}/?inscricao_id={inscricao_id}&ingresso_id={ingresso_id}&usuario_id={usuario_id}"
        else:
            # Fallback para endpoint rápido
            url = f"{APIConfig.CHECKINS}/rapido?evento_id={evento_id}&nome={nome}&cpf={cpf}&email={email}"
        
        # Prepara headers
        headers = self.api_service.get_auth_headers()
        headers["x-api-key"] = APIKeys.CHECKINS
        
        # Adiciona à fila
        self.pending_repo.create(
            method="POST",
            url=url,
            body={},
            headers=headers,
            related_inscricao_id=inscricao_id,
            related_cpf=cpf
        )
        
        # Registra localmente
        self.checkin_repo.create(
            inscricao_id=inscricao_id,
            ingresso_id=ingresso_id,
            usuario_id=usuario_id,
            evento_id=evento_id,
            tipo="normal",
            sincronizado=0
        )
        
        return (True, "✓ CHECK-IN REGISTRADO\n→ PESSOA PODE ENTRAR NO EVENTO")
    
    def registrar_checkin_rapido(
        self,
        evento_id: str,
        nome: str,
        cpf: str,
        email: str
    ) -> Tuple[bool, str]:
        """
        Registra check-in rápido (pessoa sem cadastro).
        Retorna (sucesso, mensagem)
        """
        # Verifica se já existe check-in por CPF
        checkin_status = self.verificar_checkin_por_cpf(cpf, evento_id)
        
        if checkin_status:
            if checkin_status['sincronizado']:
                return (False, "✓ CHECK-IN JÁ REGISTRADO NO SERVIDOR\n→ PODE ENTRAR")
            else:
                return (False, "⚠️ CHECK-IN JÁ REGISTRADO (LOCALMENTE)\n→ PODE ENTRAR")
        
        # VERIFICA SE CPF JÁ TEM CADASTRO (bloqueio crítico!)
        inscrito = self.inscrito_repo.find_by_cpf(cpf, evento_id)
        if inscrito and inscrito['sincronizado'] == 1:
            msg = f"""❌ NÃO É POSSÍVEL USAR INSCRIÇÃO RÁPIDA

CPF: {cpf}
Nome no sistema: {inscrito['nome']}

Este CPF JÁ TEM CADASTRO!
Use o check-in normal (botão verde)."""
            return (False, msg)
        
        # Cria ID local temporário
        local_id = str(uuid.uuid4())
        
        # Salva inscrito local
        self.inscrito_repo.create(
            inscricao_id=local_id,
            evento_id=evento_id,
            nome=nome,
            cpf=cpf,
            email=email,
            sincronizado=0
        )
        
        # Prepara requisição para endpoint /rapido
        url = f"{APIConfig.CHECKINS}/rapido?evento_id={evento_id}&nome={nome}&cpf={cpf}&email={email}"
        headers = self.api_service.get_auth_headers()
        headers["x-api-key"] = APIKeys.CHECKINS
        
        # Adiciona à fila
        self.pending_repo.create(
            method="POST",
            url=url,
            body={},
            headers=headers,
            related_inscricao_id=local_id,
            related_cpf=cpf
        )
        
        # Registra check-in local
        self.checkin_repo.create(
            inscricao_id=local_id,
            ingresso_id=None,
            usuario_id=None,
            evento_id=evento_id,
            tipo="rapida",
            sincronizado=0
        )
        
        return (True, f"""✓ INSCRIÇÃO RÁPIDA + CHECK-IN REGISTRADOS

🟠 USUÁRIO TEMPORÁRIO CRIADO
Nome: {nome}
CPF: {cpf}

→ PESSOA PODE ENTRAR NO EVENTO

Os dados serão sincronizados com o servidor.""")
    
    def remover_checkin_e_pendencias(self, inscricao_id: str) -> Tuple[bool, str]:
        """
        Remove check-in local e pendências relacionadas.
        Usado quando atendente cancela operação.
        """
        # Remove check-in
        self.checkin_repo.delete_by_inscricao(inscricao_id)
        
        # Verifica se deve remover inscrito (se for local/rápido)
        inscrito = self.inscrito_repo.find_by_id(inscricao_id)
        if inscrito and inscrito['sincronizado'] == 0:
            self.inscrito_repo.delete(inscricao_id)
        
        return (True, "✓ Check-in e dados locais removidos")