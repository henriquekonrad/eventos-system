# main.py
"""
Entry Point do Sistema de Check-in.
Inicializa banco de dados e abre tela de login.
"""
import customtkinter as ctk
import sqlite3
from config.settings import UIConfig, DB_PATH
from views.login_view import LoginView

def init_database():
    """Inicializa banco de dados com todas as tabelas"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tabela de eventos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS eventos (
            id TEXT PRIMARY KEY,
            nome TEXT,
            data_inicio TEXT,
            atualizado_em TEXT
        )
    """)
    
    # Tabela de inscritos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inscritos (
            inscricao_id TEXT PRIMARY KEY,
            evento_id TEXT,
            nome TEXT,
            cpf TEXT,
            email TEXT,
            sincronizado INTEGER DEFAULT 0,
            criado_em TEXT
        )
    """)
    
    # Tabela de check-ins
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS checkins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            inscricao_id TEXT,
            ingresso_id TEXT,
            usuario_id TEXT,
            evento_id TEXT,
            tipo TEXT,
            sincronizado INTEGER DEFAULT 0,
            criado_em TEXT
        )
    """)
    
    # Tabela de requisições pendentes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pending_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            method TEXT,
            url TEXT,
            body TEXT,
            headers TEXT,
            created_at TEXT,
            related_inscricao_id TEXT,
            related_cpf TEXT
        )
    """)
    
    # Migração: adiciona colunas se não existirem
    try:
        cursor.execute("ALTER TABLE pending_requests ADD COLUMN related_inscricao_id TEXT")
    except sqlite3.OperationalError:
        pass  # Coluna já existe
    
    try:
        cursor.execute("ALTER TABLE pending_requests ADD COLUMN related_cpf TEXT")
    except sqlite3.OperationalError:
        pass  # Coluna já existe
    
    conn.commit()
    conn.close()
    
    print("[DB] Banco de dados inicializado")

def main():
    """Função principal"""
    # Configuração do customtkinter
    ctk.set_appearance_mode(UIConfig.APPEARANCE_MODE)
    ctk.set_default_color_theme(UIConfig.COLOR_THEME)
    
    # Inicializa banco
    init_database()
    
    # Abre tela de login
    app = LoginView()
    app.mainloop()

if __name__ == "__main__":
    main()