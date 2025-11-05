"""
shared/core/security.py
Funções de segurança compartilhadas entre TODOS os microsserviços
"""
from fastapi import Depends, HTTPException, status, Header
from jose import jwt, JWTError
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

load_dotenv()

# Importar após load_dotenv
from .config import settings
from .database import get_db

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
API_KEY = os.getenv("API_KEY", "sua_api_key_aqui")


def verificar_token_middleware(authorization: str = Header(...)):
    """
    Middleware para validar token JWT em qualquer microsserviço.
    Uso: current_user = Depends(verificar_token_middleware)
    
    Retorna o payload do token (dict com 'sub' e 'role')
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Formato de token inválido. Use: Bearer <token>"
        )
    
    token = authorization.replace("Bearer ", "")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token inválido ou expirado: {str(e)}"
        )


def require_roles(*roles: str):
    """
    Dependency para verificar se o usuário tem um dos papéis necessários.
    
    Uso:
        @app.post("/admin-only")
        def admin_route(user: dict = Depends(require_roles("administrador"))):
            return {"message": "Você é admin!"}
    
    Args:
        *roles: Lista de papéis permitidos (ex: "administrador", "atendente")
    
    Returns:
        Função wrapper que retorna o payload do token se autorizado
    """
    def wrapper(authorization: str = Header(...)):
        payload = verificar_token_middleware(authorization)
        user_role = payload.get("role")
        
        if user_role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso negado. Papéis permitidos: {', '.join(roles)}"
            )
        
        return payload
    
    return wrapper


def get_current_user_from_token(authorization: str = Header(...), db: Session = Depends(get_db)):
    """
    Retorna o objeto Usuario completo do banco baseado no token.
    
    Uso:
        @app.get("/meu-perfil")
        def perfil(user: Usuario = Depends(get_current_user_from_token)):
            return {"nome": user.nome, "email": user.email}
    
    Returns:
        Objeto Usuario do SQLAlchemy
    """
    from ..models.usuario import Usuario
    
    payload = verificar_token_middleware(authorization)
    user_id = payload.get("sub")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido: ID de usuário não encontrado"
        )
    
    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado no banco de dados"
        )
    
    return user


def require_api_key(x_api_key: str = Header(...)):
    """
    Valida API Key estática (opcional, para segurança adicional).
    
    Uso:
        @app.get("/protected")
        def protected(api_key: None = Depends(require_api_key)):
            return {"message": "API Key válida!"}
    """
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key inválida ou ausente"
        )
    return None