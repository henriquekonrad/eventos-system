from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.evento import Evento
from app import schemas
from uuid import UUID
from app.core.security import require_api_key, require_roles
from app.routers.auth import get_current_user
from app.models.usuario import Usuario

router = APIRouter(prefix="/eventos", tags=["Eventos"])

@router.post("/", response_model=schemas.EventoOut, status_code=status.HTTP_201_CREATED)
def criar_evento(
    payload: schemas.EventoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles("administrador")),
    api_key: None = Depends(require_api_key)
):
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
def obter_evento(evento_id: UUID, db: Session = Depends(get_db)):
    e = db.query(Evento).filter(Evento.id == evento_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    return e

@router.put("/{evento_id}", response_model=schemas.EventoOut)
def atualizar_evento(
    evento_id: UUID,
    payload: schemas.EventoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles("administrador")),
    api_key: None = Depends(require_api_key)
):
    e = db.query(Evento).filter(Evento.id == evento_id).first()
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
def remover_evento(
    evento_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles("administrador")),
    api_key: None = Depends(require_api_key)
):
    e = db.query(Evento).filter(Evento.id == evento_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    db.delete(e)
    db.commit()
    return {"message": "evento removido"}
