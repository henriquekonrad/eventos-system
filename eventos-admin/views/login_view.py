import customtkinter as ctk
from config.settings import UIConfig
from services.api_service import APIService
from repositories.auth_cache_repository import AuthCacheRepository
from views.main_view import MainView

class LoginView(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.api_service = APIService()
        self.auth_cache = AuthCacheRepository()

        if self._try_auto_login():
            return

        self.title("Login - Sistema de Eventos")
        self.height = 375
        self.width = 400
        self._setup_ui()
        self._center_window()
    
    def _center_window(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.width // 2)
        y = (self.winfo_screenheight() // 2) - (self.height // 2)
        self.geometry(f"{self.width}x{self.height}+{x}+{y}")
    
    def _setup_ui(self):
        main_frame = ctk.CTkFrame(self)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Título
        title = ctk.CTkLabel(
            main_frame,
            text="Sistema de Check-in",
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
        
        self.bind("<Return>", lambda e: self._on_login_click())
    
    def _create_field(self, label: str, variable: ctk.StringVar, show=None):
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
        """Tenta fazer login"""
        email = self.email_var.get().strip()
        senha = self.senha_var.get().strip()
        
        if not email or not senha:
            self._show_error("Preencha todos os campos")
            return
        
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
        self.error_label.configure(text=f"ERRO: {message}")
    
    def _open_main_window(self):
        self.withdraw()
        main_window = MainView()
        main_window.mainloop()
        self.destroy()

    def _try_auto_login(self) -> bool:
        """Tenta login automático usando token salvo no cache"""
        
        if not self.api_service.has_token():
            print("Nenhum token carregado do cache")
            return False

        # Testa token
        if self.api_service.is_online():
            print("Auto-login bem-sucedido")
            self._open_main_window()
            return True

        # Se inválido, limpa token
        print("Token salvo é inválido. Limpando cache")
        self.api_service.clear_token()
        return False