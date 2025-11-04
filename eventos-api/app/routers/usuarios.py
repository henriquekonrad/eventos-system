from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.usuario import Usuario
from app.core.database import get_db
from app import schemas
from passlib.context import CryptContext
from uuid import UUID
from app.core.security import require_api_key, require_roles

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    return pwd_context.hash(password.strip())


@router.post("/", response_model=schemas.UsuarioOut, status_code=status.HTTP_201_CREATED)
def criar_usuario(
    u: schemas.UsuarioCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles("administrador")),
    api_key: None = Depends(require_api_key)
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


@router.get("/", response_model=list[schemas.UsuarioOut])
def listar_usuarios(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles("administrador")),
    api_key: None = Depends(require_api_key)
):
    return db.query(Usuario).all()


@router.get("/{usuario_id}", response_model=schemas.UsuarioOut)
def obter_usuario(usuario_id: UUID, db: Session = Depends(get_db),
                  api_key: None = Depends(require_api_key)):
    u = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return u
