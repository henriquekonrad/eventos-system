# views/main_view.py
"""
Janela Principal do Sistema.
Coordena todas as views.
"""
import customtkinter as ctk
from config.settings import UIConfig
from views.evento_list_view import EventoListView
from views.checkin_view import CheckinView
from services.sync_service import SyncService

class MainView(ctk.CTk):
    """
    Janela principal da aplicação.
    Padrão Mediator: Coordena comunicação entre views.
    """
    
    def __init__(self):
        super().__init__()
        
        # Configuração da janela
        self.title("Sistema de Eventos - Atendente")
        self.geometry(UIConfig.MAIN_WINDOW_SIZE)
        
        # Services
        self.sync_service = SyncService()
        
        # Configuração de grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Cria views
        self._setup_views()
        
        # Sincronização inicial
        self.after(500, self._sync_inicial)
    
    def _setup_views(self):
        """Configura as views"""
        # View de check-in (direita) - criada primeiro para passar referência
        self.checkin_view = CheckinView(self)
        self.checkin_view.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)
        
        # View de eventos (esquerda)
        self.evento_list_view = EventoListView(
            self,
            on_evento_select=self._on_evento_selected,
            width=300
        )
        self.evento_list_view.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
    
    def _on_evento_selected(self, evento_id: str, evento_nome: str, sync_sucesso: bool):
        """
        Callback: Evento foi selecionado.
        Padrão Mediator: Coordena comunicação entre EventoListView e CheckinView.
        """
        print(f"[MAIN] Evento selecionado: {evento_nome}")
        
        # Atualiza CheckinView
        self.checkin_view.set_evento(evento_id, evento_nome)
        
        # Mensagem sobre sincronização de inscritos
        if sync_sucesso:
            self.checkin_view._update_info(
                f"✓ Evento selecionado: {evento_nome}\n\n"
                f"Inscritos sincronizados!\n"
                f"Você pode buscar por CPF ou fazer inscrição rápida."
            )
        else:
            self.checkin_view._update_info(
                f"⚠️ Evento selecionado: {evento_nome}\n\n"
                f"Não foi possível sincronizar inscritos.\n"
                f"Verifique se está online ou se o endpoint está disponível."
            )
    
    def _sync_inicial(self):
        """Sincronização inicial de eventos"""
        print("[MAIN] Sincronizando eventos inicial...")
        self.sync_service.sincronizar_eventos()
        self.evento_list_view.atualizar_lista()