from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.checkin import Checkin
from app.models.inscricao import Inscricao
from app.models.evento import Evento
from app.models.usuario import Usuario
from app import schemas
import uuid
from uuid import UUID
import datetime
from app.core.security import require_roles
from app.routers.auth import get_current_user
from passlib.context import CryptContext
import secrets

router = APIRouter(prefix="/checkins", tags=["Checkins"])
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


def to_uuid(id_str: str):
    try:
        return UUID(id_str)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido")


@router.post("/", status_code=status.HTTP_201_CREATED)
def registrar_checkin(
    inscricao_id: UUID,
    ingresso_id: UUID,
    usuario_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles("atendente", "administrador"))
):
    """
    Registra check-in para uma inscrição existente.
    Somente atendentes ou administradores podem registrar.
    """
    inscr = db.query(Inscricao).filter(Inscricao.id == inscricao_id).first()
    if not inscr:
        raise HTTPException(status_code=404, detail="Inscrição não encontrada")

    existente = (
        db.query(Checkin)
        .filter(Checkin.inscricao_id == inscricao_id, Checkin.ingresso_id == ingresso_id)
        .first()
    )
    if existente:
        raise HTTPException(status_code=400, detail="Check-in já registrado para este ingresso")

    try:
        with db.begin():
            check = Checkin(
                inscricao_id=inscricao_id,
                ingresso_id=ingresso_id,
                usuario_id=usuario_id,
                ocorrido_em=datetime.datetime.utcnow()
            )
            db.add(check)

            inscr.sincronizado = False
            db.add(inscr)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao registrar check-in: {e}")

    return {"id": str(check.id), "ocorrido_em": check.ocorrido_em}


@router.post("/rapido", status_code=status.HTTP_201_CREATED)
def checkin_rapido(
    evento_id: UUID,
    nome: str,
    cpf: str,
    email: str,
    ingresso_id: UUID | None = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles("atendente", "administrador"))
):
    """
    Cria inscrição rápida, usuário rápido (caso não exista) e registra check-in.
    - Email, nome e CPF obrigatórios.
    - Senha temporária é gerada automaticamente.
    """
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")

    try:
        with db.begin():
            user = db.query(Usuario).filter(Usuario.email == email).first()
            senha_temp = None

            if not user:
                senha_temp = "temp_" + secrets.token_hex(4)
                user = Usuario(
                    nome=nome,
                    email=email,
                    senha_hash=pwd.hash(senha_temp),
                    papel="rapido",
                    ativo=True,
                )
                db.add(user)
                db.flush()

            inscr = Inscricao(
                evento_id=evento_id,
                usuario_id=user.id,
                inscricao_rapida=True,
                nome_rapido=nome,
                cpf_rapido=cpf,
                email_rapido=email,
                status="ativa",
                sincronizado=False
            )
            db.add(inscr)
            db.flush()

            check = Checkin(
                inscricao_id=inscr.id,
                ingresso_id=ingresso_id or uuid.uuid4(),
                usuario_id=user.id,
                ocorrido_em=datetime.datetime.utcnow()
            )
            db.add(check)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao registrar check-in rápido: {e}")

    return {
        "inscricao_id": str(inscr.id),
        "checkin_id": str(check.id),
        "usuario_id": str(user.id),
        "usuario_email": user.email,
        "senha_temporaria": senha_temp,
    }
