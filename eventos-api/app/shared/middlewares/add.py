from app.shared.middlewares.cors import add_cors_middleware
from app.shared.middlewares.auditoria import auditoria_middleware
from fastapi import FastAPI

def add_common_middlewares(app: FastAPI, audit: bool = False):
    """
    Adiciona middlewares de forma desacoplada.
    Ordem não importa mais! Cada middleware é independente.
    """
    add_cors_middleware(app)
    
    if audit:
        app.middleware("http")(auditoria_middleware)
    
    return app