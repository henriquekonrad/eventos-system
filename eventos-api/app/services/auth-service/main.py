"""
Microsserviço de Autenticação
Porta: 8001
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
import sys
sys.path.append('..')

from shared.core.database import get_db
from shared.models.usuario import Usuario
from shared.core.config import settings
from shared import schemas

app = FastAPI(title="Auth Service", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 3


def criar_token(dados: dict, exp_min: int = ACCESS_TOKEN_EXPIRE_MINUTES):
    to_encode = dados.copy()
    expire = datetime.utcnow() + timedelta(minutes=exp_min)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


def verificar_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )


@app.get("/")
def health_check():
    return {"service": "auth-service", "status": "running"}


@app.post("/login", response_model=schemas.Token)
def login(data: schemas.LoginIn, db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.email == data.email).first()
    
    if not user or not pwd.verify(data.senha, user.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas"
        )
    
    token = criar_token({
        "sub": str(user.id),
        "role": user.papel or "participante"
    })
    
    return {"access_token": token, "token_type": "bearer"}


@app.post("/validar-token")
def validar_token(token: str):
    """
    Endpoint para outros microsserviços validarem tokens
    """
    try:
        payload = verificar_token(token)
        return {"valid": True, "payload": payload}
    except HTTPException:
        return {"valid": False}


@app.get("/me")
def me(token: str, db: Session = Depends(get_db)):
    """
    Retorna dados do usuário autenticado
    """
    payload = verificar_token(token)
    user_id = payload.get("sub")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )
    
    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    return {
        "id": str(user.id),
        "nome": user.nome,
        "email": user.email,
        "papel": user.papel
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)