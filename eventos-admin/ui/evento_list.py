import customtkinter as ctk
import sqlite3
from db import DB_PATH

class EventoListFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.listbox = ctk.CTkTextbox(self, width=240, height=500)
        self.listbox.pack(padx=10, pady=10)
        self.atualizar_lista()

    def atualizar_lista(self):
        self.listbox.delete("1.0", "end")
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id, nome, data_inicio FROM eventos ORDER BY data_inicio")
        for ev_id, nome, data_inicio in c.fetchall():
            self.listbox.insert("end", f"{nome} ({data_inicio})\n")
        conn.close()
