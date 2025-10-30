from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.checkin import Checkin
from app.models.inscricao import Inscricao
from app.models.evento import Evento
from app import schemas
import uuid
from uuid import UUID
import datetime

router = APIRouter(prefix="/checkins", tags=["Checkins"])

def to_uuid(id_str: str):
    try:
        return UUID(id_str)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido")

@router.post("/", status_code=status.HTTP_201_CREATED)
def registrar_checkin(inscricao_id: str, ingresso_id: str, usuario_id: str, db: Session = Depends(get_db)):
    iid = to_uuid(inscricao_id)
    inscr = db.query(Inscricao).filter(Inscricao.id == iid).first()
    if not inscr:
        raise HTTPException(status_code=404, detail="Inscrição não encontrada")

    check = Checkin(
        inscricao_id=iid,
        ingresso_id=to_uuid(ingresso_id),
        usuario_id=to_uuid(usuario_id),
        ocorrido_em=datetime.datetime.utcnow()
    )
    db.add(check)
    db.commit()
    db.refresh(check)
    try:
        inscr.sincronizado = False
        db.add(inscr)
        db.commit()
    except Exception:
        pass

    return {"id": str(check.id), "ocorrido_em": check.ocorrido_em}

@router.post("/rapido", status_code=status.HTTP_201_CREATED)
def checkin_rapido(evento_id: str, nome: str, cpf: str = None, email: str = None, ingresso_id: str = None, db: Session = Depends(get_db)):
    """
    Cria inscrição rápida e registra checkin na sequência.
    Retorna id da inscrição e id do checkin.
    """
    eid = to_uuid(evento_id)
    evento = db.query(Evento).filter(Evento.id == eid).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")

    inscr = Inscricao(
        evento_id=eid,
        inscricao_rapida=True,
        nome_rapido=nome,
        cpf_rapido=cpf,
        email_rapido=email,
        status="confirmada",
        sincronizado=False
    )
    db.add(inscr)
    db.commit()
    db.refresh(inscr)

    # se ingresso_id não informado, geramos uuid temporário (ou aqui você pode exigir)
    ing_id = ingresso_id if ingresso_id else str(uuid.uuid4())
    # criar checkin
    check = Checkin(
        inscricao_id=inscr.id,
        ingresso_id=to_uuid(ing_id) if ingresso_id else ing_id,  # se you prefer sempre uuid: force it
        usuario_id=None,
        ocorrido_em=datetime.datetime.utcnow()
    )
    db.add(check)
    db.commit()
    db.refresh(check)

    return {"inscricao_id": str(inscr.id), "checkin_id": str(check.id)}
