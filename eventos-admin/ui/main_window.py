import customtkinter as ctk
from ui.evento_list import EventoListFrame
from ui.checkin_frame import CheckinFrame
from sync_manager import sync_eventos

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Atendente - Sistema de Eventos (Offline)")
        self.geometry("900x600")
        self.grid_columnconfigure(1, weight=1)

        # frames
        self.left_frame = EventoListFrame(self, width=260)
        self.left_frame.grid(row=0, column=0, sticky="ns")

        self.right_frame = CheckinFrame(self)
        self.right_frame.grid(row=0, column=1, sticky="nsew")

        # botão de sincronização manual
        self.sync_btn = ctk.CTkButton(self.left_frame, text="Sincronizar Eventos", command=self.sync)
        self.sync_btn.pack(pady=10)

        # sincroniza ao iniciar
        self.sync()

    def sync(self):
        sync_eventos()
        self.left_frame.atualizar_lista()  # lê do SQLite e atualiza interface
