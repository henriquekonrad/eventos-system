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
    """
    
    def __init__(self):
        self.checkin_repo = CheckinRepository()
        self.inscrito_repo = InscritoRepository()
        self.pending_repo = PendingRepository()
        self.api_service = APIService()
    
    def verificar_checkin_existente(self, inscricao_id: str) -> Optional[Dict]:
        """
        Verifica se check-in já existe.
        """
        return self.checkin_repo.exists_by_inscricao(inscricao_id)
    
    def verificar_checkin_por_cpf(self, cpf: str, evento_id: str) -> Optional[Dict]:
        """
        Verifica se check-in existe por CPF em um evento.
        """
        inscrito = self.inscrito_repo.find_by_cpf(cpf, evento_id)
        
        if not inscrito:
            return None
        
        checkin_status = self.checkin_repo.exists_by_inscricao(inscrito['inscricao_id'])
        
        if not checkin_status:
            return None
        
        return {
            "existe": True,
            "sincronizado": checkin_status['sincronizado'],
            "inscricao_id": inscrito['inscricao_id']
        }
    
    def verificar_inscricao_cancelada(self, inscricao_id: str, evento_id: str) -> bool:
        """
        Verifica se inscrição está cancelada (localmente).
        Retorna True se cancelada.
        """
        inscrito = self.inscrito_repo.find_by_id(inscricao_id)
        if inscrito and inscrito.get('status') == 'cancelada':
            return True
        return False
    
    def registrar_checkin_normal(
        self, 
        inscricao_id: str, 
        evento_id: str,
        nome: str,
        cpf: str,
        email: str,
        status: str = "ativa" 
    ) -> Tuple[bool, str]:
        """
        Registra check-in para inscrição existente.
        """

        if status == "cancelada":
            return (False, f"""❌ INSCRIÇÃO CANCELADA

CPF: {cpf}
Nome: {nome}

Esta inscrição foi CANCELADA.
A pessoa precisa se inscrever novamente pelo site.""")
        
        # Verifica se já tem check-in
        checkin_status = self.checkin_repo.exists_by_inscricao(inscricao_id)
        
        if checkin_status:
            if checkin_status['sincronizado']:
                return (False, "✓ CHECK-IN JÁ REGISTRADO NO SERVIDOR\n→ PODE ENTRAR")
            else:
                return (False, "⚠️ CHECK-IN JÁ REGISTRADO (LOCALMENTE)\n→ PODE ENTRAR")
        
        ingresso_id = None
        usuario_id = None
        
        if self.api_service.is_online():
            try:
                ingresso_data = self.api_service.buscar_ingresso(inscricao_id)
                if ingresso_data:
                    ingresso_id = ingresso_data.get("id") or ingresso_data.get("ingresso_id")
                
                usuario_data = self.api_service.buscar_usuario_por_email(email)
                if usuario_data:
                    usuario_id = usuario_data.get("id") or usuario_data.get("usuario_id")
            except Exception as e:
                print(f"[SERVICE] Erro ao buscar dados: {e}")
        
        if ingresso_id and usuario_id:
            url = f"{APIConfig.CHECKINS}/?inscricao_id={inscricao_id}&ingresso_id={ingresso_id}&usuario_id={usuario_id}"
        else:
            url = f"{APIConfig.CHECKINS}/rapido?evento_id={evento_id}&nome={nome}&cpf={cpf}&email={email}"
        
        headers = self.api_service.get_auth_headers()
        headers["x-api-key"] = APIKeys.CHECKINS
        
        self.pending_repo.create(
            method="POST",
            url=url,
            body={},
            headers=headers,
            related_inscricao_id=inscricao_id,
            related_cpf=cpf
        )
        
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
        """
        checkin_status = self.verificar_checkin_por_cpf(cpf, evento_id)
        
        if checkin_status:
            if checkin_status['sincronizado']:
                return (False, "✓ CHECK-IN JÁ REGISTRADO NO SERVIDOR\n→ PODE ENTRAR")
            else:
                return (False, "CHECK-IN JÁ REGISTRADO (LOCALMENTE)\n→ PODE ENTRAR")
        
        # VERIFICA SE CPF JÁ TEM CADASTRO
        inscrito = self.inscrito_repo.find_by_cpf(cpf, evento_id)
        if inscrito and inscrito.get('sincronizado') == 1:
            if inscrito.get('status') == 'cancelada':
                msg = f"""❌ INSCRIÇÃO CANCELADA

CPF: {cpf}
Nome no sistema: {inscrito['nome']}

Esta pessoa tinha inscrição, mas CANCELOU.
Ela precisa se inscrever novamente pelo site."""
                return (False, msg)
            
            msg = f"""❌ NÃO É POSSÍVEL USAR INSCRIÇÃO RÁPIDA

CPF: {cpf}
Nome no sistema: {inscrito['nome']}

Este CPF JÁ TEM CADASTRO!
Use o check-in normal (botão verde)."""
            return (False, msg)
        
        local_id = str(uuid.uuid4())
        
        self.inscrito_repo.create(
            inscricao_id=local_id,
            evento_id=evento_id,
            nome=nome,
            cpf=cpf,
            email=email,
            sincronizado=0
        )
        
        url = f"{APIConfig.CHECKINS}/rapido?evento_id={evento_id}&nome={nome}&cpf={cpf}&email={email}"
        headers = self.api_service.get_auth_headers()
        headers["x-api-key"] = APIKeys.CHECKINS
        
        self.pending_repo.create(
            method="POST",
            url=url,
            body={},
            headers=headers,
            related_inscricao_id=local_id,
            related_cpf=cpf
        )
        
        self.checkin_repo.create(
            inscricao_id=local_id,
            ingresso_id=None,
            usuario_id=None,
            evento_id=evento_id,
            tipo="rapida",
            sincronizado=0
        )
        
        return (True, f"""✓ INSCRIÇÃO RÁPIDA + CHECK-IN REGISTRADOS

USUÁRIO TEMPORÁRIO CRIADO
Nome: {nome}
CPF: {cpf}

→ PESSOA PODE ENTRAR NO EVENTO

Os dados serão sincronizados com o servidor.""")
    
    def remover_checkin_e_pendencias(self, inscricao_id: str) -> Tuple[bool, str]:
        """
        Remove check-in local e pendências relacionadas.
        """
        self.checkin_repo.delete_by_inscricao(inscricao_id)
        
        inscrito = self.inscrito_repo.find_by_id(inscricao_id)
        if inscrito and inscrito['sincronizado'] == 0:
            self.inscrito_repo.delete(inscricao_id)
        
        return (True, "✓ Check-in e dados locais removidos")