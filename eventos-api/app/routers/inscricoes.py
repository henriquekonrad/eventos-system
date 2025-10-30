from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.inscricao import Inscricao
from app.models.evento import Evento
from app.models.usuario import Usuario
from app import schemas
from uuid import UUID
import datetime

router = APIRouter(prefix="/inscricoes", tags=["Inscricoes"])

def to_uuid(id_str: str):
    try:
        return UUID(id_str)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido")

@router.post("/", status_code=status.HTTP_201_CREATED)
def criar_inscricao_completa(payload: schemas.InscricaoCreateRapida, db: Session = Depends(get_db)):
    """
    Reaproveitei o schema de InscricaoCreateRapida para dados básicos.
    Este endpoint cria inscrição completa ou parcial conforme campos enviados.
    Para inscrição completa (com usuário), após integrar auth você poderá ligar usuario_id ao cadastro.
    """
    # valida evento
    eid = to_uuid(payload.evento_id)
    evento = db.query(Evento).filter(Evento.id == eid).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")

    inscr = Inscricao(
        evento_id=eid,
        inscricao_rapida=True if (payload.cpf_rapido or payload.email_rapido) else False,
        nome_rapido=payload.nome_rapido,
        cpf_rapido=payload.cpf_rapido,
        email_rapido=payload.email_rapido,
        status="confirmada",
        sincronizado=False
    )
    db.add(inscr)
    db.commit()
    db.refresh(inscr)
    return {"id": str(inscr.id), "message": "inscrição criada"}

@router.get("/evento/{evento_id}", response_model=list[schemas.InscricaoOut])
def listar_inscricoes_por_evento(evento_id: str, db: Session = Depends(get_db)):
    eid = to_uuid(evento_id)
    return db.query(Inscricao).filter(Inscricao.evento_id == eid).all()

@router.get("/usuario/{usuario_id}", response_model=list[schemas.InscricaoOut])
def listar_inscricoes_por_usuario(usuario_id: str, db: Session = Depends(get_db)):
    uid = to_uuid(usuario_id)
    return db.query(Inscricao).filter(Inscricao.usuario_id == uid).all()

@router.get("/{inscricao_id}", response_model=schemas.InscricaoOut)
def obter_inscricao(inscricao_id: str, db: Session = Depends(get_db)):
    iid = to_uuid(inscricao_id)
    i = db.query(Inscricao).filter(Inscricao.id == iid).first()
    if not i:
        raise HTTPException(status_code=404, detail="Inscrição não encontrada")
    return i

@router.delete("/{inscricao_id}")
def cancelar_inscricao(inscricao_id: str, db: Session = Depends(get_db)):
    iid = to_uuid(inscricao_id)
    i = db.query(Inscricao).filter(Inscricao.id == iid).first()
    if not i:
        raise HTTPException(status_code=404, detail="Inscrição não encontrada")
    i.status = "cancelada"
    i.cancelado_em = datetime.datetime.utcnow()
    i.sincronizado = False
    db.add(i)
    db.commit()
    return {"message": "Inscrição cancelada"}
