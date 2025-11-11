# ui/login_frame.py
import customtkinter as ctk
from tkinter import messagebox
from api_client import login
from ui.main_window import MainWindow

class LoginFrame(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Login - Sistema de Eventos")
        self.geometry("400x250")
        self.resizable(False, False)

        ctk.CTkLabel(self, text="Email:").pack(pady=(30,5))
        self.email_entry = ctk.CTkEntry(self, width=300)
        self.email_entry.pack()

        ctk.CTkLabel(self, text="Senha:").pack(pady=(10,5))
        self.senha_entry = ctk.CTkEntry(self, width=300, show="*")
        self.senha_entry.pack()

        self.login_btn = ctk.CTkButton(self, text="Login", command=self.fazer_login)
        self.login_btn.pack(pady=20)

    def fazer_login(self):
        email = self.email_entry.get()
        senha = self.senha_entry.get()
        try:
            token = login(email, senha)
            if token:
                messagebox.showinfo("Sucesso", "Login realizado com sucesso!")
                self.destroy()  # fecha a janela de login
                # abre a janela principal
                app = MainWindow()
                app.mainloop()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha no login:\n{e}")
