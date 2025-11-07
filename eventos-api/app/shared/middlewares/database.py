"""
shared/middlewares/database.py
Middleware para injetar sessão do banco de dados no request.state
"""
from fastapi import Request
from sqlalchemy.orm import Session
from app.shared.core.database import SessionLocal


async def database_middleware(request: Request, call_next):
    """
    Cria uma sessão do banco e injeta no request.state.db
    para ser usada por outros middlewares e endpoints.
    """
    db: Session = SessionLocal()
    request.state.db = db
    
    try:
        response = await call_next(request)
    finally:
        db.close()
    
    return response