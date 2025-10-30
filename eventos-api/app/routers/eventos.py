from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.evento import Evento
from app import schemas
from uuid import UUID
import uuid

router = APIRouter(prefix="/eventos", tags=["Eventos"])

def to_uuid(id_str: str):
    try:
        return UUID(id_str)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido")

@router.post("/", response_model=schemas.EventoOut, status_code=status.HTTP_201_CREATED)
def criar_evento(payload: schemas.EventoCreate, db: Session = Depends(get_db)):
    evento = Evento(
        titulo=payload.titulo,
        descricao=payload.descricao,
        inicio_em=payload.inicio_em,
        fim_em=payload.fim_em
    )
    db.add(evento)
    db.commit()
    db.refresh(evento)
    return evento

@router.get("/", response_model=list[schemas.EventoOut])
def listar_eventos(db: Session = Depends(get_db)):
    return db.query(Evento).order_by(Evento.inicio_em).all()

@router.get("/{evento_id}", response_model=schemas.EventoOut)
def obter_evento(evento_id: str, db: Session = Depends(get_db)):
    eid = to_uuid(evento_id)
    e = db.query(Evento).filter(Evento.id == eid).first()
    if not e:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    return e

@router.put("/{evento_id}", response_model=schemas.EventoOut)
def atualizar_evento(evento_id: str, payload: schemas.EventoCreate, db: Session = Depends(get_db)):
    eid = to_uuid(evento_id)
    e = db.query(Evento).filter(Evento.id == eid).first()
    if not e:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    e.titulo = payload.titulo
    e.descricao = payload.descricao
    e.inicio_em = payload.inicio_em
    e.fim_em = payload.fim_em
    db.add(e)
    db.commit()
    db.refresh(e)
    return e

@router.delete("/{evento_id}")
def remover_evento(evento_id: str, db: Session = Depends(get_db)):
    eid = to_uuid(evento_id)
    e = db.query(Evento).filter(Evento.id == eid).first()
    if not e:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    db.delete(e)
    db.commit()
    return {"message": "evento removido"}
