"""
Microsserviço de Usuários
Porta: 8003
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from uuid import UUID
from passlib.context import CryptContext

from app.shared.core.database import get_db
from app.shared.models.usuario import Usuario
from app.shared import schemas
from app.shared.core.security import require_roles

app = FastAPI(title="Usuarios Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    return pwd_context.hash(password.strip())


@app.get("/")
def health_check():
    return {"service": "usuarios-service", "status": "running"}


@app.post("/", response_model=schemas.UsuarioOut, status_code=status.HTTP_201_CREATED)
def criar_usuario(
    u: schemas.UsuarioCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("administrador"))
):
    if db.query(Usuario).filter(Usuario.email == u.email).first():
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    
    if u.cpf and db.query(Usuario).filter(Usuario.cpf == u.cpf).first():
        raise HTTPException(status_code=400, detail="CPF já cadastrado")
    
    usuario = Usuario(
        nome=u.nome,
        email=u.email,
        senha_hash=hash_password(u.senha),
        cpf=u.cpf,
        papel=u.papel if hasattr(u, "papel") else "usuario",
        email_verificado=False
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@app.get("/", response_model=list[schemas.UsuarioOut])
def listar_usuarios(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("administrador"))
):
    return db.query(Usuario).all()


@app.get("/{usuario_id}", response_model=schemas.UsuarioOut)
def obter_usuario(usuario_id: UUID, db: Session = Depends(get_db)):
    u = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return u


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)