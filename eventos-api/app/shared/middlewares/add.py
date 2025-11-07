"""
shared/middlewares/add.py
Adiciona todos os middlewares comuns aos microsserviços
"""
from app.shared.middlewares.cors import add_cors_middleware
from app.shared.middlewares.database import database_middleware
from app.shared.middlewares.auditoria import auditoria_middleware, auditoria_middleware_light
from fastapi import FastAPI


def add_common_middlewares(app: FastAPI, audit: bool = False, light: bool = False):
    """
    Adiciona middlewares comuns a todos os microsserviços:
    - CORS
    - Database (sessão do banco)
    - (Opcional) Auditoria
    """
    add_cors_middleware(app)
    
    app.middleware("http")(database_middleware)
    
    if audit:
        if light:
            app.middleware("http")(auditoria_middleware_light)
        else:
            app.middleware("http")(auditoria_middleware)
    
    return app