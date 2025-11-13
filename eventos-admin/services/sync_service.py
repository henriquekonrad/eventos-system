# services/sync_service.py
"""
Service de Sincronização.
Gerencia sincronização de eventos, inscritos e requisições pendentes.
"""
import requests
import json
from typing import Dict
from repositories.evento_repository import EventoRepository
from repositories.inscrito_repository import InscritoRepository
from repositories.pending_repository import PendingRepository
from repositories.checkin_repository import CheckinRepository
from services.api_service import APIService
from config.settings import APIKeys

class SyncService:
    """
    Gerencia todas as operações de sincronização.
    Padrão Facade: Simplifica sincronização complexa.
    """
    
    def __init__(self):
        self.evento_repo = EventoRepository()
        self.inscrito_repo = InscritoRepository()
        self.pending_repo = PendingRepository()
        self.checkin_repo = CheckinRepository()
        self.api_service = APIService()
    
    # ========== SINCRONIZAÇÃO DE EVENTOS ==========
    
    def sincronizar_eventos(self) -> bool:
        """Sincroniza eventos da API para banco local"""
        if not self.api_service.is_online():
            print("[SYNC] Offline: não é possível sincronizar eventos")
            return False
        
        try:
            eventos = self.api_service.listar_eventos_publicos()
            
            if not eventos:
                print("[SYNC] Nenhum evento retornado da API")
                return False
            
            for evento in eventos:
                self.evento_repo.create_or_update(
                    evento_id=evento["id"],
                    nome=evento.get("titulo", ""),
                    data_inicio=evento.get("inicio_em", "")
                )
            
            print(f"[SYNC] ✓ Sincronizados {len(eventos)} eventos")
            return True
            
        except Exception as e:
            print(f"[SYNC] ✗ Erro ao sincronizar eventos: {e}")
            return False
    
    # ========== SINCRONIZAÇÃO DE INSCRITOS ==========
    
    def sincronizar_inscritos_evento(self, evento_id: str) -> bool:
        """Sincroniza inscritos de um evento específico"""
        if not self.api_service.is_online():
            print("[SYNC] Offline: não é possível sincronizar inscritos")
            return False
        
        try:
            inscritos = self.api_service.listar_inscritos_evento(evento_id)
            
            if inscritos is None:
                print("[SYNC] ✗ Erro ao buscar inscritos da API")
                return False
            
            # Limpa inscritos antigos (apenas sincronizados)
            self.inscrito_repo.delete_by_evento_synced(evento_id)
            
            # Salva novos inscritos
            for inscrito in inscritos:
                self.inscrito_repo.create(
                    inscricao_id=inscrito.get("id") or inscrito.get("inscricao_id"),
                    evento_id=evento_id,
                    nome=inscrito.get("nome", ""),
                    cpf=inscrito.get("cpf", ""),
                    email=inscrito.get("email", ""),
                    sincronizado=1  # Veio do servidor
                )
            
            print(f"[SYNC] ✓ Sincronizados {len(inscritos)} inscritos do evento")
            return True
            
        except Exception as e:
            print(f"[SYNC] ✗ Erro ao sincronizar inscritos: {e}")
            return False
    
    # ========== SINCRONIZAÇÃO DE PENDENTES ==========
    
    def processar_pendentes(self) -> Dict:
        """
        Processa requisições pendentes com tratamento inteligente.
        Retorna estatísticas: {sucesso, falhas, ja_feito, removidos, total_pendentes}
        """
        if not self.api_service.is_online():
            print("[SYNC] Ainda offline")
            return {"sucesso": 0, "falhas": 0, "ja_feito": 0, "removidos": 0, "total_pendentes": 0}
        
        pendentes = self.pending_repo.find_all()
        
        if not pendentes:
            print("[SYNC] Nenhuma requisição pendente")
            return {"sucesso": 0, "falhas": 0, "ja_feito": 0, "removidos": 0, "total_pendentes": 0}
        
        print(f"[SYNC] Processando {len(pendentes)} requisições pendentes...")
        
        sucesso = 0
        falhas = 0
        ja_feito = 0
        removidos = 0
        
        for pendente in pendentes:
            resultado = self._processar_pendente(pendente)
            
            if resultado == "sucesso":
                sucesso += 1
            elif resultado == "ja_feito":
                ja_feito += 1
            elif resultado == "removido":
                removidos += 1
            else:
                falhas += 1
        
        # Conta quantos ainda restam
        total_pendentes = self.pending_repo.count()
        
        print(f"[SYNC] Resultado: {sucesso} sucesso, {falhas} falhas, "
              f"{ja_feito} já feitos, {removidos} removidos")
        
        return {
            "sucesso": sucesso,
            "falhas": falhas,
            "ja_feito": ja_feito,
            "removidos": removidos,
            "total_pendentes": total_pendentes
        }
    
    def _processar_pendente(self, pendente: Dict) -> str:
        """
        Processa uma requisição pendente.
        Retorna: 'sucesso', 'ja_feito', 'removido', 'falha'
        """
        try:
            # Parse headers e body
            headers = json.loads(pendente.get("headers", "{}"))
            body = json.loads(pendente["body"]) if pendente["body"] else None
            
            # Adiciona API key apropriada
            if "8004" in pendente["url"]:
                headers["x-api-key"] = APIKeys.INSCRICOES
            elif "8006" in pendente["url"]:
                headers["x-api-key"] = APIKeys.CHECKINS
            
            print(f"[SYNC] Processando: {pendente['method']} {pendente['url']}")
            
            # Faz requisição
            response = requests.request(
                pendente["method"],
                pendente["url"],
                json=body,
                headers=headers,
                timeout=6
            )
            
            print(f"[SYNC] Status: {response.status_code}")
            
            # SUCESSO (2xx)
            if 200 <= response.status_code < 300:
                # Marca check-in como sincronizado
                if pendente.get('related_inscricao_id'):
                    self.checkin_repo.mark_as_synced(pendente['related_inscricao_id'])
                
                self.pending_repo.delete(pendente["id"])
                print(f"[SYNC] ✓ Sucesso")
                return "sucesso"
            
            # ERROS 4xx - Analisar
            if 400 <= response.status_code < 500:
                return self._handle_4xx_error(response, pendente)
            
            # ERROS 5xx - Analisar
            if response.status_code >= 500:
                return self._handle_5xx_error(response, pendente)
            
            # Outros casos
            print(f"[SYNC] ⚠️ Status desconhecido - MANTENDO na fila")
            return "falha"
            
        except requests.Timeout:
            print(f"[SYNC] ⏱️ Timeout - MANTENDO na fila")
            return "falha"
        except requests.ConnectionError:
            print(f"[SYNC] 🔌 Erro de conexão - MANTENDO na fila")
            return "falha"
        except Exception as e:
            print(f"[SYNC] ✗ Erro inesperado: {e}")
            return "falha"
    
    def _handle_4xx_error(self, response, pendente: Dict) -> str:
        """Trata erros 4xx"""
        response_text = response.text.lower()
        
        # Check-in já realizado
        if "já foi realizado" in response_text or "já registrado" in response_text:
            print(f"[SYNC] ℹ️ Check-in já realizado - REMOVENDO")
            if pendente.get('related_inscricao_id'):
                self.checkin_repo.mark_as_synced(pendente['related_inscricao_id'])
            self.pending_repo.delete(pendente["id"])
            return "ja_feito"
        
        # Inscrição já existe
        if "já inscrito" in response_text:
            print(f"[SYNC] ℹ️ Inscrição já existe - REMOVENDO")
            self.pending_repo.delete(pendente["id"])
            return "ja_feito"
        
        # 404 - Não encontrado
        if response.status_code == 404:
            print(f"[SYNC] ⚠️ Recurso não encontrado (404) - REMOVENDO")
            self.pending_repo.delete(pendente["id"])
            return "removido"
        
        # 400/409 - Erro de dados
        if response.status_code in [400, 409]:
            print(f"[SYNC] ⚠️ Erro de dados ({response.status_code}) - REMOVENDO")
            self.pending_repo.delete(pendente["id"])
            return "removido"
        
        # Outros 4xx - mantém
        print(f"[SYNC] ✗ Erro {response.status_code} - MANTENDO")
        return "falha"
    
    def _handle_5xx_error(self, response, pendente: Dict) -> str:
        """Trata erros 5xx"""
        response_text = response.text.lower()
        
        # CPF/Email duplicado (erro de validação que retorna 500)
        if "duplicate key" in response_text and ("cpf" in response_text or "email" in response_text):
            print(f"[SYNC] ⚠️ CPF/Email duplicado - REMOVENDO")
            self.pending_repo.delete(pendente["id"])
            return "removido"
        
        # Outros 500 - erro temporário do servidor
        print(f"[SYNC] ✗ Erro do servidor ({response.status_code}) - MANTENDO")
        return "falha"