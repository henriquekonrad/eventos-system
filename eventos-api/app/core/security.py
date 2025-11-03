from fastapi import Depends, HTTPException, status
from app.models.usuario import Usuario
from app.routers.auth import get_current_user

def require_roles(*roles: str):
    def wrapper(current_user: Usuario = Depends(get_current_user)):
        if current_user.papel not in roles:
            raise HTTPException(status_code=403, detail="Acesso negado")
        return current_user
    return wrapper