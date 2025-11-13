# views/evento_list_view.py
"""
View de Lista de Eventos.
Exibe eventos disponíveis e permite seleção.
"""
import customtkinter as ctk
import tkinter as tk
from typing import Optional, Callable
from services.evento_service import EventoService

class EventoListView(ctk.CTkFrame):
    """
    View para lista de eventos.
    Padrão Observer: Notifica quando evento é selecionado.
    """
    
    def __init__(
        self, 
        master,
        on_evento_select: Optional[Callable[[str, str], None]] = None,
        **kwargs
    ):
        """
        Args:
            master: Frame pai
            on_evento_select: Callback(evento_id, evento_nome) quando seleciona
        """
        super().__init__(master, **kwargs)
        
        # Service
        self.evento_service = EventoService()
        
        # Callback
        self.on_evento_select = on_evento_select
        
        # Estado
        self.eventos_data = []  # Lista de (id, nome, data)
        
        self._setup_ui()
        self.atualizar_lista()
    
    def _setup_ui(self):
        """Configura interface"""
        # Título
        title = ctk.CTkLabel(
            self,
            text="📅 Eventos",
            font=("Arial", 16, "bold")
        )
        title.pack(pady=(10, 5))
        
        # Listbox
        self.listbox = tk.Listbox(self, width=35, height=20)
        self.listbox.pack(padx=10, pady=(5, 10), fill="both", expand=True)
        self.listbox.bind("<<ListboxSelect>>", self._on_select)
        
        # Botão sincronizar
        self.sync_btn = ctk.CTkButton(
            self,
            text="🔄 Sincronizar Eventos",
            command=self._on_sync_click
        )
        self.sync_btn.pack(pady=(0, 10), padx=10, fill="x")
    
    def _on_select(self, event):
        """Handler: Evento selecionado"""
        selection = self.listbox.curselection()
        
        if not selection:
            return
        
        idx = selection[0]
        
        if idx >= len(self.eventos_data):
            return
        
        evento_id, nome, data = self.eventos_data[idx]
        
        print(f"[VIEW] Evento selecionado: {nome}")
        
        # Sincroniza inscritos do evento
        sucesso = self.evento_service.sincronizar_inscritos(evento_id)
        
        # Notifica callback
        if self.on_evento_select:
            self.on_evento_select(evento_id, nome, sucesso)
    
    def _on_sync_click(self):
        """Handler: Sincronizar eventos"""
        print("[VIEW] Sincronizando eventos...")
        self.evento_service.sincronizar_eventos()
        self.atualizar_lista()
    
    def atualizar_lista(self):
        """Atualiza lista de eventos"""
        # Limpa lista
        self.listbox.delete(0, tk.END)
        self.eventos_data = []
        
        # Busca eventos
        eventos = self.evento_service.listar_eventos_locais()
        
        if not eventos:
            self.listbox.insert(tk.END, "Nenhum evento encontrado")
            self.listbox.insert(tk.END, "Clique em 'Sincronizar Eventos'")
            return
        
        # Popula lista
        for evento in eventos:
            # Formata data
            data_str = evento['data_inicio'][:10] if evento['data_inicio'] else "Sem data"
            display = f"{evento['nome']} ({data_str})"
            
            self.listbox.insert(tk.END, display)
            self.eventos_data.append((evento['id'], evento['nome'], evento['data_inicio']))
        
        print(f"[VIEW] {len(eventos)} eventos carregados")