# ui/evento_list.py
import customtkinter as ctk
import tkinter as tk
import sqlite3
from db import DB_PATH
from sync_manager import sync_inscritos_evento

class EventoListFrame(ctk.CTkFrame):
    def __init__(self, master, checkin_frame=None, **kwargs):
        super().__init__(master, **kwargs)
        self.checkin_frame = checkin_frame
        self.eventos_data = []  # Armazena (id, nome, data)
        
        # Título
        title = ctk.CTkLabel(self, text="📅 Eventos", font=("Arial", 16, "bold"))
        title.pack(pady=(10,5))
        
        # Listbox
        self.listbox = tk.Listbox(self, width=35, height=20)
        self.listbox.pack(padx=10, pady=(5,10), fill="both", expand=True)
        self.listbox.bind("<<ListboxSelect>>", self.on_select)
        
        # Botão de sincronização
        self.sync_btn = ctk.CTkButton(
            self, 
            text="🔄 Sincronizar Eventos", 
            command=self.trigger_sync
        )
        self.sync_btn.pack(pady=(0,10), padx=10, fill="x")
        
        self.atualizar_lista()

    def on_select(self, event):
        """Quando um evento é selecionado na lista"""
        selection = self.listbox.curselection()
        if not selection or not self.checkin_frame:
            return
        
        idx = selection[0]
        if idx >= len(self.eventos_data):
            return
        
        evento_id, nome, data = self.eventos_data[idx]
        
        # Avisa o checkin_frame qual evento foi selecionado
        self.checkin_frame.set_evento(evento_id, nome)
        
        # Sincroniza inscritos desse evento
        print(f"[EVENTO_LIST] Sincronizando inscritos do evento: {nome}")
        sucesso = sync_inscritos_evento(evento_id)
        
        if sucesso:
            self.checkin_frame.update_info(
                f"✓ Evento selecionado: {nome}\n\n"
                f"Inscritos sincronizados!\n"
                f"Você pode buscar por CPF ou fazer inscrição rápida."
            )
        else:
            self.checkin_frame.update_info(
                f"⚠️ Evento selecionado: {nome}\n\n"
                f"Não foi possível sincronizar inscritos.\n"
                f"Verifique se há endpoint na API ou se está online."
            )

    def atualizar_lista(self):
        """Atualiza lista de eventos do banco local"""
        self.listbox.delete(0, tk.END)
        self.eventos_data = []
        
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT id, nome, data_inicio FROM eventos ORDER BY data_inicio")
            
            for ev_id, nome, data_inicio in c.fetchall():
                # Formata data para exibição
                data_str = data_inicio[:10] if data_inicio else "Sem data"
                display = f"{nome} ({data_str})"
                
                self.listbox.insert(tk.END, display)
                self.eventos_data.append((ev_id, nome, data_inicio))
            
            conn.close()
            
            if not self.eventos_data:
                self.listbox.insert(tk.END, "Nenhum evento encontrado")
                self.listbox.insert(tk.END, "Clique em 'Sincronizar Eventos'")
                
        except Exception as e:
            print(f"[EVENTO_LIST] Erro ao carregar eventos: {e}")
            self.listbox.insert(tk.END, f"Erro: {e}")

    def trigger_sync(self):
        """Botão para forçar sincronização de eventos"""
        from sync_manager import sync_eventos
        sync_eventos()
        self.atualizar_lista()