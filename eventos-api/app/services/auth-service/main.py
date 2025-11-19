"""
Microsserviço de Autenticação
Porta: 8001
"""
from fastapi import FastAPI, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from typing import Optional
from uuid import UUID

from app.shared.core.database import get_db
from app.shared.models.usuario import Usuario
from app.shared.core.config import settings
from app.shared import schemas
from app.shared.middlewares.add import add_common_middlewares
from app.shared.core.security import require_service_api_key

app = FastAPI(title="Auth Service", version="1.0.0")
add_common_middlewares(app, audit=True)

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 45


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


def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    """Helper para extrair usuário do token JWT"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token não fornecido"
        )
    
    token = authorization.replace("Bearer ", "")
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
    
    return user


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


@app.post("/registrar", status_code=status.HTTP_201_CREATED)
def registrar(
    data: schemas.UsuarioCreate,
    db: Session = Depends(get_db),
    api_key: None = Depends(require_service_api_key("auth"))
):
    """
    Registra um novo usuário no sistema.
    
    REQUER: API Key (sem JWT - é um registro público)
    """
    # Verificar se email já existe
    if db.query(Usuario).filter(Usuario.email == data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )
    
    # Verificar se CPF já existe (se fornecido)
    if data.cpf and db.query(Usuario).filter(Usuario.cpf == data.cpf).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CPF já cadastrado"
        )
    
    # Criar novo usuário
    novo_usuario = Usuario(
        nome=data.nome,
        email=data.email,
        cpf=data.cpf,
        senha_hash=pwd.hash(data.senha),
        papel="participante",  # Novos registros sempre começam como participante
        email_verificado=False
    )
    
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    
    return {
        "id": str(novo_usuario.id),
        "nome": novo_usuario.nome,
        "email": novo_usuario.email,
        "papel": novo_usuario.papel
    }


@app.patch("/completar-cadastro")
def completar_cadastro(
    data: schemas.CompletarCadastroIn,
    db: Session = Depends(get_db),
    api_key: None = Depends(require_service_api_key("auth")),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Completa o cadastro de um usuário 'rápido'.
    Permite atualizar nome, CPF e senha.
    
    REQUER: API Key + JWT
    """
    # Verificar se é usuário rápido
    if current_user.papel != "rapido":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas usuários rápidos podem completar cadastro"
        )
    
    # Atualizar nome se fornecido
    if data.nome:
        current_user.nome = data.nome.strip()
    
    # Atualizar CPF se fornecido
    if data.cpf:
        # Verificar se CPF já existe em outro usuário
        cpf_existente = db.query(Usuario).filter(
            Usuario.cpf == data.cpf,
            Usuario.id != current_user.id
        ).first()
        
        if cpf_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CPF já cadastrado para outro usuário"
            )
        
        current_user.cpf = data.cpf
    
    # Atualizar senha se fornecida
    if data.senha:
        if len(data.senha) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A senha deve ter no mínimo 6 caracteres"
            )
        current_user.senha_hash = pwd.hash(data.senha)
    
    # Mudar papel para participante (sai de "rapido")
    current_user.papel = "participante"
    current_user.email_verificado = True
    
    db.commit()
    db.refresh(current_user)
    
    return {
        "id": str(current_user.id),
        "nome": current_user.nome,
        "email": current_user.email,
        "cpf": current_user.cpf,
        "papel": current_user.papel,
        "message": "Cadastro completado com sucesso!"
    }


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
        "cpf": user.cpf,
        "papel": user.papel
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)