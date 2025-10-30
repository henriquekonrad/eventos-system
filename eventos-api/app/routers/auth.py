from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.usuario import Usuario
from pydantic import BaseModel
from passlib.context import CryptContext

router = APIRouter(prefix="/auth", tags=["Auth"])
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

class LoginIn(BaseModel):
    email: str
    senha: str

@router.post("/login")
def login(data: LoginIn, db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.email == data.email).first()
    if not user or not pwd.verify(data.senha, user.senha_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")
    # Por enquanto retornamos dados do usuário (sem JWT). Substituir por token JWT depois.
    return {"id": str(user.id), "email": user.email, "nome": user.nome}

@router.post("/logout")
def logout():
    # placeholder; se implementar JWT, aqui você pode invalidar token (blacklist) ou apenas deixar cliente apagar.
    return {"message": "logout (placeholder)"}

@router.get("/me")
def me():
    # placeholder: quando integrar auth, usar get_current_user e retornar dados do usuário
    return {"message": "endpoint /me — implemente get_current_user e retorne usuário atual"}
