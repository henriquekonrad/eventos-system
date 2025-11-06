"""
Microsserviço de Autenticação
Porta: 8001
"""
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext

from app.shared.core.database import get_db
from app.shared.models.usuario import Usuario
from app.shared.core.config import settings
from app.shared import schemas
from app.shared.core.middleware import add_common_middleware
from app.shared.core.security import require_service_api_key

app = FastAPI(title="Auth Service", version="1.0.0")

add_common_middleware(app)

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
    

@app.post("/login", response_model=schemas.Token)
def login(
    data: schemas.LoginIn,
    db: Session = Depends(get_db),
    api_key: None = Depends(require_service_api_key("auth"))
):
    """
    Realiza login e retorna token JWT.
    
    REQUER: API Key (sem JWT - é o endpoint que CRIA o JWT)
    """
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
def validar_token(
    token: str,
    api_key: None = Depends(require_service_api_key("auth"))
):
    """
    Endpoint para outros microsserviços validarem tokens.
    Útil para comunicação inter-serviços.
    
    REQUER: API Key (sem JWT - valida o JWT de outros)
    """
    try:
        payload = verificar_token(token)
        return {"valid": True, "payload": payload}
    except HTTPException:
        return {"valid": False}


@app.get("/me")
def me(
    token: str,
    db: Session = Depends(get_db),
    api_key: None = Depends(require_service_api_key("auth"))
):
    """
    Retorna dados do usuário autenticado baseado no token.
    
    REQUER: API Key + token como query param
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