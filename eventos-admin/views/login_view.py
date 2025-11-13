# views/login_view.py
"""
Tela de Login.
Autentica usuário antes de acessar sistema.
"""
import customtkinter as ctk
from config.settings import UIConfig
from services.api_service import APIService
from views.main_view import MainView

class LoginView(ctk.CTk):
    """
    Tela de login do sistema.
    """
    
    def __init__(self):
        super().__init__()
        
        # Configuração da janela
        self.title("Login - Sistema de Eventos")
        self.geometry("400x350")
        
        # Service
        self.api_service = APIService()
        
        # Centraliza janela
        self._center_window()
        
        # Cria UI
        self._setup_ui()
    
    def _center_window(self):
        """Centraliza janela na tela"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def _setup_ui(self):
        """Configura interface"""
        # Frame principal
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        title = ctk.CTkLabel(
            main_frame,
            text="🎫 Sistema de Check-in",
            font=("Arial", 24, "bold")
        )
        title.pack(pady=(20, 10))
        
        subtitle = ctk.CTkLabel(
            main_frame,
            text="Faça login para continuar",
            font=("Arial", 12),
            text_color="gray"
        )
        subtitle.pack(pady=(0, 30))
        
        # Campos
        self.email_var = ctk.StringVar()
        self.senha_var = ctk.StringVar()
        
        self._create_field("Email:", self.email_var, show=None)
        self._create_field("Senha:", self.senha_var, show="*")
        
        # Mensagem de erro
        self.error_label = ctk.CTkLabel(
            main_frame,
            text="",
            font=("Arial", 10),
            text_color=UIConfig.COLOR_ERROR
        )
        self.error_label.pack(pady=5)
        
        # Botão login
        self.login_btn = ctk.CTkButton(
            main_frame,
            text="Entrar",
            command=self._on_login_click,
            height=40,
            font=("Arial", 14, "bold")
        )
        self.login_btn.pack(pady=20, padx=40, fill="x")
        
        # Bind Enter key
        self.bind("<Return>", lambda e: self._on_login_click())
    
    def _create_field(self, label: str, variable: ctk.StringVar, show=None):
        """Cria campo de formulário"""
        frame = ctk.CTkFrame(self.children['!ctkframe'])
        frame.pack(fill="x", padx=40, pady=5)
        
        ctk.CTkLabel(
            frame,
            text=label,
            font=("Arial", 11)
        ).pack(anchor="w", pady=(0, 2))
        
        entry = ctk.CTkEntry(
            frame,
            textvariable=variable,
            show=show
        )
        entry.pack(fill="x")
    
    def _on_login_click(self):
        """Handler: Tenta fazer login"""
        email = self.email_var.get().strip()
        senha = self.senha_var.get().strip()
        
        # Validação básica
        if not email or not senha:
            self._show_error("Preencha todos os campos")
            return
        
        # Desabilita botão
        self.login_btn.configure(state="disabled", text="Conectando...")
        self.update()
        
        # Tenta login
        token = self.api_service.login(email, senha)
        
        if token:
            print("[LOGIN] Sucesso!")
            self._open_main_window()
        else:
            self._show_error("Email ou senha inválidos")
            self.login_btn.configure(state="normal", text="Entrar")
    
    def _show_error(self, message: str):
        """Exibe mensagem de erro"""
        self.error_label.configure(text=f"❌ {message}")
    
    def _open_main_window(self):
        """Abre janela principal e fecha login"""
        self.withdraw()  # Esconde login
        main_window = MainView()
        main_window.mainloop()
        self.destroy()  # Fecha login