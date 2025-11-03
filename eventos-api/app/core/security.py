from fastapi import Depends, HTTPException, status
from app.models.usuario import Usuario
from app.routers.auth import get_current_user
from fastapi import Header, HTTPException, status
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("API_KEY")

def require_roles(*roles: str):
    def wrapper(current_user: Usuario = Depends(get_current_user)):
        if current_user.papel not in roles:
            raise HTTPException(status_code=403, detail="Acesso negado")
        return current_user
    return wrapper

def require_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key inválida"
        )