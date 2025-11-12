# ui/main_window.py
import customtkinter as ctk
from ui.evento_list import EventoListFrame
from ui.checkin_frame import CheckinFrame
from sync_manager import sync_eventos

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Eventos - Atendente")
        self.geometry("1100x650")
        
        # Configuração de grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Frame direito (checkin) precisa ser criado primeiro
        # para passar referência ao frame esquerdo (eventos)
        self.right_frame = CheckinFrame(self)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=(0,10), pady=10)
        
        # Frame esquerdo (eventos) com referência ao checkin_frame
        self.left_frame = EventoListFrame(self, checkin_frame=self.right_frame, width=300)
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=(10,5), pady=10)
        
        # Sincroniza eventos ao iniciar
        self.after(500, self.sync_inicial)  # Delay para UI carregar

    def sync_inicial(self):
        """Sincronização inicial de eventos"""
        print("[MAIN] Sincronizando eventos inicial...")
        sync_eventos()
        self.left_frame.atualizar_lista()