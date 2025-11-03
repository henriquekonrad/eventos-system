from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.ingresso import Ingresso
from app.models.inscricao import Inscricao
from app.models.evento import Evento
from app.schemas import IngressoSchema
from uuid import UUID, uuid4
import datetime
import hashlib
from typing import List
from app.core.security import require_roles
from app.routers.auth import get_current_user
from app.models.usuario import Usuario

router = APIRouter(prefix="/ingressos", tags=["Ingressos"])


@router.get("/evento/{evento_id}", response_model=List[IngressoSchema])
def listar_ingressos_por_evento(evento_id: UUID, db: Session = Depends(get_db)):
    ingressos = db.query(Ingresso).filter(Ingresso.evento_id == evento_id).all()
    if not ingressos:
        raise HTTPException(status_code=404, detail="Nenhum ingresso encontrado para este evento")
    return ingressos


@router.post("/inscricao/{inscricao_id}", response_model=IngressoSchema, status_code=status.HTTP_201_CREATED)
def criar_ingresso(
    inscricao_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles("administrador", "atendente"))
):
    inscricao = db.query(Inscricao).filter(Inscricao.id == inscricao_id).first()
    if not inscricao:
        raise HTTPException(status_code=404, detail="Inscrição não encontrada")

    evento = db.query(Evento).filter(Evento.id == inscricao.evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")

    codigo = f"ING-{uuid4().hex[:8].upper()}"
    token_qr = hashlib.sha256(f"{codigo}-{inscricao_id}".encode()).hexdigest()

    ingresso = Ingresso(
        inscricao_id=inscricao_id,
        evento_id=evento.id,
        codigo_ingresso=codigo,
        token_qr=token_qr,
        status="emitido",
        emitido_em=datetime.datetime.utcnow()
    )
    db.add(ingresso)
    db.commit()
    db.refresh(ingresso)
    return ingresso


@router.get("/validar/{token_qr}")
def validar_ingresso(token_qr: str, db: Session = Depends(get_db)):
    ingresso = db.query(Ingresso).filter(Ingresso.token_qr == token_qr).first()
    if not ingresso:
        raise HTTPException(status_code=404, detail="Ingresso inválido ou não encontrado")

    if ingresso.status == "usado":
        raise HTTPException(status_code=400, detail="Ingresso já utilizado")

    return {
        "mensagem": "Ingresso válido",
        "ingresso_id": str(ingresso.id),
        "evento_id": str(ingresso.evento_id),
        "inscricao_id": str(ingresso.inscricao_id),
        "status": ingresso.status
    }


@router.post("/usar/{ingresso_id}")
def marcar_ingresso_usado(
    ingresso_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles("administrador", "atendente"))
):
    ingresso = db.query(Ingresso).filter(Ingresso.id == ingresso_id).first()
    if not ingresso:
        raise HTTPException(status_code=404, detail="Ingresso não encontrado")

    if ingresso.status == "usado":
        raise HTTPException(status_code=400, detail="Ingresso já foi utilizado")

    ingresso.status = "usado"
    db.commit()
    db.refresh(ingresso)

    return {"mensagem": "Check-in realizado com sucesso", "ingresso": ingresso.codigo_ingresso}
