from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.inscricao import Inscricao
from app.models.evento import Evento
from app.models.usuario import Usuario
from app import schemas
from uuid import UUID, uuid4
from secrets import token_urlsafe
import datetime

router = APIRouter(prefix="/inscricoes", tags=["Inscricoes"])

def to_uuid(id_str: str):
    try:
        return UUID(id_str)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido")

@router.post("/", status_code=status.HTTP_201_CREATED)
def criar_inscricao_normal(evento_id: UUID, usuario_id: UUID, db: Session = Depends(get_db)):
    """
    Cria uma inscrição normal (usuário já cadastrado).
    """
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")

    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    existente = db.query(Inscricao).filter(
        Inscricao.evento_id == evento_id,
        Inscricao.usuario_id == usuario_id
    ).first()
    if existente:
        raise HTTPException(status_code=400, detail="Usuário já inscrito neste evento")

    inscr = Inscricao(
        evento_id=evento_id,
        usuario_id=usuario_id,
        inscricao_rapida=False,
        status="ativa",
        sincronizado=False
    )
    db.add(inscr)
    db.commit()
    db.refresh(inscr)

    return {"id": str(inscr.id), "message": "inscrição criada"}

@router.post("/rapida", status_code=status.HTTP_201_CREATED)
def criar_inscricao_rapida(payload: schemas.InscricaoCreateRapida, db: Session = Depends(get_db)):
    """
    Cria uma inscrição rápida (visitante sem conta).
    """
    evento = db.query(Evento).filter(Evento.id == payload.evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")

    email = payload.email_rapido or f"temp_{uuid4()}@rapido.local"
    usuario_rapido = Usuario(
        nome=payload.nome_rapido,
        email=email,
        cpf=payload.cpf_rapido,
        senha_hash=token_urlsafe(16),  # senha temporária
        papel="rapido",
        email_verificado=False
    )
    db.add(usuario_rapido)
    db.commit()
    db.refresh(usuario_rapido)

    inscr = Inscricao(
        evento_id=payload.evento_id,
        inscricao_rapida=True,
        nome_rapido=payload.nome_rapido,
        cpf_rapido=payload.cpf_rapido,
        email_rapido=payload.email_rapido,
        status="ativa",
        sincronizado=False
    )
    db.add(inscr)
    db.commit()
    db.refresh(inscr)

    return {
        "inscricao_id": str(inscr.id),
        "usuario_id": str(usuario_rapido.id),
        "message": "Inscrição rápida criada com usuário rápido associado"
    }

@router.get("/evento/{evento_id}", response_model=list[schemas.InscricaoOut])
def listar_inscricoes_por_evento(evento_id: UUID, db: Session = Depends(get_db)):
    return db.query(Inscricao).filter(Inscricao.evento_id == evento_id).all()

@router.get("/usuario/{usuario_id}", response_model=list[schemas.InscricaoOut])
def listar_inscricoes_por_usuario(usuario_id: UUID, db: Session = Depends(get_db)):
    return db.query(Inscricao).filter(Inscricao.usuario_id == usuario_id).all()

@router.get("/{inscricao_id}", response_model=schemas.InscricaoOut)
def obter_inscricao(inscricao_id: UUID, db: Session = Depends(get_db)):
    i = db.query(Inscricao).filter(Inscricao.id == inscricao_id).first()
    if not i:
        raise HTTPException(status_code=404, detail="Inscrição não encontrada")
    return i

@router.delete("/{inscricao_id}")
def cancelar_inscricao(inscricao_id: UUID, db: Session = Depends(get_db)):
    i = db.query(Inscricao).filter(Inscricao.id == inscricao_id).first()
    if not i:
        raise HTTPException(status_code=404, detail="Inscrição não encontrada")
    i.status = "cancelada"
    i.cancelado_em = datetime.datetime.utcnow()
    i.sincronizado = False
    db.add(i)
    db.commit()
    return {"message": "Inscrição cancelada"}
