import customtkinter as ctk
import tkinter as tk
from typing import Optional, Callable
from services.evento_service import EventoService

class EventoListView(ctk.CTkFrame):
    def __init__(
        self, 
        master,
        on_evento_select: Optional[Callable[[str, str], None]] = None,
        **kwargs
    ):
        super().__init__(master, **kwargs)
        self.evento_service = EventoService()

        self.on_evento_select = on_evento_select

        self.eventos_data = []
        
        self._setup_ui()
        self.atualizar_lista()
    
    def _setup_ui(self):
        """Configura interface"""
        # Título
        title = ctk.CTkLabel(
            self,
            text="Eventos",
            font=("Arial", 16, "bold")
        )
        title.pack(pady=(10, 5))
        
        # Listbox
        self.listbox = tk.Listbox(self, width=50, height=20,
                                  bg="#1a1a1a",
                                    fg="white",
                                    selectbackground="#3273A8",
                                    selectforeground="white",
                                    highlightbackground="#2a3658",
                                    highlightcolor="#2a2a2a",
                                    borderwidth=0,)
        self.listbox.pack(padx=10, pady=(5, 10), fill="both", expand=True)
        self.listbox.bind("<<ListboxSelect>>", self._on_select)
        
        # Botão sincronizar
        self.sync_btn = ctk.CTkButton(
            self,
            text="Sincronizar Eventos",
            command=self._on_sync_click
        )
        self.sync_btn.pack(pady=(0, 10), padx=10, fill="x")
    
    def _on_select(self, event):
        """Ativado ao selecionar evento"""
        selection = self.listbox.curselection()
        
        if not selection:
            return
        
        idx = selection[0]
        
        if idx >= len(self.eventos_data):
            return
        
        evento_id, nome, data = self.eventos_data[idx]
        
        print(f"Evento selecionado: {nome}")
        
        # Sincroniza inscritos do evento
        sucesso = self.evento_service.sincronizar_inscritos(evento_id)
        
        # Notifica
        if self.on_evento_select:
            self.on_evento_select(evento_id, nome, sucesso)
    
    def _on_sync_click(self):
        """Sincroniza Eventos"""
        print("Sincronizando eventos...")
        self.evento_service.sincronizar_eventos()
        self.atualizar_lista()
    
    def atualizar_lista(self):
        """Atualiza lista de eventos"""
        self.listbox.delete(0, tk.END)
        self.eventos_data = []
        
        # Busca eventos
        eventos = self.evento_service.listar_eventos_locais()
        
        if not eventos:
            self.listbox.insert(tk.END, "Nenhum evento encontrado")
            self.listbox.insert(tk.END, "Clique em 'Sincronizar Eventos'")
            return
        
        for evento in eventos:
            # Formata data
            data_str = evento['data_inicio'][:10] if evento['data_inicio'] else "Sem data"
            display = f"{evento['nome']} ({data_str})"
            
            self.listbox.insert(tk.END, display)
            self.eventos_data.append((evento['id'], evento['nome'], evento['data_inicio']))
        
        print(f"{len(eventos)} eventos carregados")