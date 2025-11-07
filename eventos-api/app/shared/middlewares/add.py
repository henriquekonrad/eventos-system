from app.shared.middlewares.cors import add_cors_middleware
from fastapi import FastAPI
from shared.middlewares.auditoria import auditoria_middleware
from shared.middlewares.auditoria import auditoria_middleware_light

def add_common_middlewares(app: FastAPI, audit: bool = False, light: bool = False):
    """
    Adiciona middlewares comuns a todos os microsserviços:
    - CORS
    - (Opcional) Auditoria
    """

    add_cors_middleware(app)

    if audit and not light:
        app.middleware("http")(auditoria_middleware)
    if audit and light:
        app.middleware("http")(auditoria_middleware_light)

    return app