import customtkinter as ctk
from tkinter import messagebox
from typing import Callable, Optional
from config.settings import UIConfig
from services.checkin_service import CheckinService
from utils.validators import Validators

class InscricaoRapidaDialog:
    """
    Dialog modal para inscrição rápida.
    """
    
    def __init__(
        self, 
        parent: ctk.CTk,
        evento_id: str,
        cpf_inicial: str = "",
        on_success: Optional[Callable[[str], None]] = None
    ):
        self.parent = parent
        self.evento_id = evento_id
        self.cpf_inicial = cpf_inicial
        self.on_success = on_success

        self.checkin_service = CheckinService()
        
        self.popup = None
        self.nome_entry = None
        self.email_entry = None
        self.cpf_entry = None
    
    def show(self):
        self._create_popup()
        self._create_ui()
    
    def _create_popup(self):
        self.popup = ctk.CTkToplevel(self.parent)
        self.popup.title("Inscrição Rápida - Pessoa SEM cadastro")
        self.popup.geometry(UIConfig.DIALOG_MEDIUM)
        
        self.popup.update_idletasks()
        self.popup.attributes('-topmost', True)
        self.popup.focus_force()
        self.popup.after(100, lambda: self.popup.grab_set())
    
    def _create_ui(self):
        # Título
        titulo = ctk.CTkLabel(
            self.popup,
            text="Inscrição Rápida\nPara pessoas que NÃO TEM cadastro no sistema",
            font=("Arial", 12, "bold"),
            text_color=UIConfig.COLOR_RAPIDA
        )
        titulo.pack(pady=(10, 15))
        
        # Campos
        self.nome_entry = self._create_field("Nome Completo:")
        self.cpf_entry = self._create_field("CPF:", initial_value=self.cpf_inicial)
        self.email_entry = self._create_field("Email:")
        
        # Aviso
        aviso = ctk.CTkLabel(
            self.popup,
            text="Será criado um usuário temporário.\n"
                 "A pessoa poderá completar o cadastro depois no site.",
            font=("Arial", 12),
            text_color="white"
        )
        aviso.pack(pady=(10, 5))
        
        # Botão confirmar
        ok_btn = ctk.CTkButton(
            self.popup,
            text="Criar Usuário Temporário e Fazer Check-in",
            command=self._on_submit,
            height=40,
            fg_color=UIConfig.COLOR_RAPIDA,
            hover_color=UIConfig.COLOR_WARNING
        )
        ok_btn.pack(pady=15)
    
    def _create_field(self, label: str, initial_value: str = ""):
        ctk.CTkLabel(
            self.popup,
            text=label,
            font=("Arial", 11, "bold")
        ).pack(pady=(8 if label != "Nome Completo:" else 5, 2))

        entry = ctk.CTkEntry(
            self.popup,
            width=450
        )
        entry.pack(padx=20)
        if initial_value:
            entry.insert(0, initial_value)
        return entry
    
    def _on_submit(self):
        nome = self.nome_entry.get().strip()
        cpf = self.cpf_entry.get().strip()
        email = self.email_entry.get().strip()
        
        if not nome or not cpf or not email:
            self._show_error("Preencha todos os campos!")
            return
        
        print(
            "nome:",Validators.validar_nome(nome),
            "cpf:",Validators.validar_cpf(cpf),
            "email:",Validators.validar_email(email)
        )
        if not Validators.validar_nome(nome) or not Validators.validar_cpf(cpf) or not Validators.validar_email(email):
            self._show_error("Campos inválidos")
            return

        sucesso, mensagem = self.checkin_service.registrar_checkin_rapido(
            evento_id=self.evento_id,
            nome=nome,
            cpf=cpf,
            email=email
        )
        
        self.popup.destroy()
        if self.on_success:
            self.on_success(mensagem)
    
    def _show_error(self, message: str):
        messagebox.showerror(message)
        print(f"{message}")