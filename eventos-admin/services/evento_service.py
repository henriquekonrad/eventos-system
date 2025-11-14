from typing import List, Dict, Optional
from repositories.evento_repository import EventoRepository
from services.api_service import APIService
from services.sync_service import SyncService

class EventoService:
    """
    Gerencia operações relacionadas a eventos.
    """
    
    def __init__(self):
        self.evento_repo = EventoRepository()
        self.api_service = APIService()
        self.sync_service = SyncService()
    
    def listar_eventos_locais(self) -> List[Dict]:
        """Lista eventos do banco local"""
        return self.evento_repo.find_all()
    
    def buscar_evento(self, evento_id: str) -> Optional[Dict]:
        """Busca evento por ID"""
        return self.evento_repo.find_by_id(evento_id)
    
    def sincronizar_eventos(self) -> bool:
        """Sincroniza eventos da API"""
        return self.sync_service.sincronizar_eventos()
    
    def sincronizar_inscritos(self, evento_id: str) -> bool:
        """Sincroniza inscritos de um evento"""
        return self.sync_service.sincronizar_inscritos_evento(evento_id)
    
    def contar_eventos(self) -> int:
        """Conta total de eventos"""
        return self.evento_repo.count()