"""
shared/core/middleware.py
Middlewares compartilhados entre todos os microsserviços
"""
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
import os
from dotenv import load_dotenv

load_dotenv()


def add_cors_middleware(app: FastAPI):
    """
    Adiciona middleware CORS configurado para todos os microsserviços.
    
    Usage:
        from shared.core.middleware import add_cors_middleware
        
        app = FastAPI()
        add_cors_middleware(app)
    """
    # Obter origens permitidas do .env (opcional)
    allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "*")
    
    # Se for "*", usar lista com "*", senão fazer split por vírgula
    if allowed_origins_str == "*":
        allowed_origins = ["*"]
    else:
        allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,  # ["http://localhost:3000", "https://seusite.com"]
        allow_credentials=True,
        allow_methods=["*"],  # Permite todos os métodos (GET, POST, PUT, DELETE, etc)
        allow_headers=["*"],  # Permite todos os headers
        expose_headers=["*"],
        max_age=3600,  # Cache das preflight requests por 1 hora
    )
    
    return app


def add_common_middleware(app: FastAPI):
    """
    Adiciona todos os middlewares comuns (CORS, logging, etc)
    
    Usage:
        from shared.core.middleware import add_common_middleware
        
        app = FastAPI()
        add_common_middleware(app)
    """
    # CORS
    add_cors_middleware(app)
    
    # Adicione outros middlewares aqui no futuro
    # Ex: Logging, Rate Limiting, etc
    
    return app