# main.py
import customtkinter as ctk
from db import init_db
from ui.login_frame import LoginFrame

def main():
    init_db()
    login_window = LoginFrame()
    login_window.mainloop()

if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    main()
