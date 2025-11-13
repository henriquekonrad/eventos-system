import customtkinter as ctk
from tkinter import messagebox
from typing import Callable, Optional
import urllib.parse
from config.settings import UIConfig
from repositories.pending_repository import PendingRepository
from repositories.checkin_repository import CheckinRepository
from repositories.inscrito_repository import InscritoRepository

class PendingDialog:
    """
    Dialog para visualizar e gerenciar requisições pendentes.
    """
    
    def __init__(
        self,
        parent: ctk.CTk,
        on_remove: Optional[Callable[[int], None]] = None
    ):
        self.parent = parent
        self.on_remove = on_remove
        
        self.pending_repo = PendingRepository()
        self.checkin_repo = CheckinRepository()
        self.inscrito_repo = InscritoRepository()
        
        self.popup = None
    
    def show(self):
        """Exibe o dialog"""
        pendentes = self.pending_repo.find_all()
        
        self._create_popup()
        
        if not pendentes:
            self._show_empty_state()
        else:
            self._show_pending_list(pendentes)
        
        self._create_close_button()
    
    def _create_popup(self):
        """Cria janela"""
        self.popup = ctk.CTkToplevel(self.parent)
        self.popup.title("Requisições Aguardando Sincronização")
        self.popup.geometry(UIConfig.DIALOG_LARGE)
        
        self.popup.update_idletasks()
        self.popup.attributes('-topmost', True)
        self.popup.focus_force()
    
    def _show_empty_state(self):
        """Exibe estado vazio (sem pendências)"""
        main_frame = ctk.CTkFrame(self.popup)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Ícone
        icon = ctk.CTkLabel(
            main_frame,
            text="✓",
            font=("Arial", 80),
            text_color=UIConfig.COLOR_SUCCESS
        )
        icon.pack(pady=50)
        
        # Mensagem
        msg = ctk.CTkLabel(
            main_frame,
            text="Nenhuma operação pendente!",
            font=("Arial", 18, "bold")
        )
        msg.pack()
        
        desc = ctk.CTkLabel(
            main_frame,
            text="Todas as operações foram sincronizadas com sucesso.",
            font=("Arial", 12),
            text_color="gray"
        )
        desc.pack(pady=10)
    
    def _show_pending_list(self, pendentes: list):
        """Exibe lista de pendências"""
        main_frame = ctk.CTkFrame(self.popup)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        header = ctk.CTkLabel(
            main_frame,
            text=f"{len(pendentes)} operação(ões) aguardando envio ao servidor",
            font=("Arial", 16, "bold")
        )
        header.pack(pady=(10, 15))
        
        scroll_frame = ctk.CTkScrollableFrame(main_frame, height=350)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        for i, pendente in enumerate(pendentes, 1):
            self._create_pending_card(scroll_frame, i, pendente)
    
    def _create_pending_card(self, parent, index: int, pendente: dict):
        """Cria card para uma requisição pendente"""
        card = ctk.CTkFrame(parent)
        card.pack(fill="x", padx=5, pady=5)
        
        # Header do card
        card_header = ctk.CTkFrame(card)
        card_header.pack(fill="x", padx=10, pady=8)
        
        # Determinar tipo e cor
        tipo, cor = self._get_operation_type(pendente['url'])
        
        tipo_label = ctk.CTkLabel(
            card_header,
            text=f"#{index} - {tipo}",
            font=("Arial", 13, "bold"),
            text_color=cor
        )
        tipo_label.pack(side="left")
        
        # Botão remover
        remove_btn = ctk.CTkButton(
            card_header,
            text="Remover",
            width=100,
            height=28,
            fg_color=UIConfig.COLOR_ERROR,
            hover_color="darkred",
            command=lambda: self._on_remove_click(pendente['id'])
        )
        remove_btn.pack(side="right")
        
        # Detalhes
        details_frame = ctk.CTkFrame(card, fg_color="transparent")
        details_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        info_text = self._extract_info_from_url(pendente['url'])
        
        info_label = ctk.CTkLabel(
            details_frame,
            text=info_text,
            font=("Arial", 11),
            justify="left",
            anchor="w"
        )
        info_label.pack(fill="x", pady=2)
        
        data_label = ctk.CTkLabel(
            details_frame,
            text=f"Criado em: {pendente['created_at'][:19]}",
            font=("Arial", 9),
            text_color="gray"
        )
        data_label.pack(anchor="w", pady=(5, 0))
    
    def _create_close_button(self):
        close_btn = ctk.CTkButton(
            self.popup,
            text="Fechar",
            command=self.popup.destroy,
            height=40
        )
        close_btn.pack(pady=(0, 15))
    
    def _get_operation_type(self, url: str) -> tuple:
        """Retorna (tipo, cor) baseado na URL"""
        if '/rapido' in url:
            return ("Check-in Rápido", UIConfig.COLOR_WARNING)
        elif '/8006/' in url:
            return ("Check-in Normal", UIConfig.COLOR_SUCCESS)
        elif '/8004/' in url:
            return ("Inscrição", UIConfig.COLOR_INFO)
        else:
            return ("Operação", "gray")
    
    def _extract_info_from_url(self, url: str) -> str:
        """Extrai informações legíveis da URL"""
        parsed = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed.query)
        
        info_parts = []
        
        if 'nome' in params:
            info_parts.append(f"👤 Nome: {params['nome'][0]}")
        if 'cpf' in params:
            info_parts.append(f"📄 CPF: {params['cpf'][0]}")
        if 'email' in params:
            info_parts.append(f"📧 Email: {params['email'][0]}")
        if 'inscricao_id' in params:
            info_parts.append(f"🎫 Inscrição: {params['inscricao_id'][0][:8]}...")
        
        return "\n".join(info_parts) if info_parts else "Detalhes da operação"
    
    def _on_remove_click(self, request_id: int):
        """Handler: Remove pendente"""
        resposta = messagebox.askyesno(
            "Confirmar Remoção",
            "Tem certeza que deseja remover esta operação?\n\n"
            "⚠️ Ela não será enviada ao servidor!\n"
            "Os dados locais relacionados também serão removidos.\n\n"
            "Use apenas se foi registrada por engano.",
            parent=self.popup
        )
        
        if not resposta:
            return
        
        info = self.pending_repo.delete(request_id)
        
        # Limpa dados locais relacionados
        if info and info['related_inscricao_id']:
            self.checkin_repo.delete_by_inscricao(info['related_inscricao_id'])
            
            inscrito = self.inscrito_repo.find_by_id(info['related_inscricao_id'])
            if inscrito and inscrito['sincronizado'] == 0:
                self.inscrito_repo.delete(info['related_inscricao_id'])
        
        if self.on_remove:
            self.on_remove(request_id)
        
        self.popup.destroy()
        self.show()