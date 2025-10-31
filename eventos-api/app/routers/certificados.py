from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.certificado import Certificado
from app.models.inscricao import Inscricao
from app.models.checkin import Checkin
from app import schemas
import secrets
import datetime

router = APIRouter(prefix="/certificados", tags=["Certificados"])


@router.post("/emitir", response_model=schemas.CertificadoOut, status_code=status.HTTP_201_CREATED)
def emitir_certificado(payload: schemas.CertificadoCreate, db: Session = Depends(get_db)):
    inscr = db.query(Inscricao).filter(
        Inscricao.id == payload.inscricao_id,
        Inscricao.evento_id == payload.evento_id
    ).first()
    if not inscr:
        raise HTTPException(status_code=404, detail="Inscrição não encontrada para este evento")

    check = db.query(Checkin).filter(Checkin.inscricao_id == payload.inscricao_id).first()
    if not check:
        raise HTTPException(status_code=400, detail="Não é possível emitir certificado sem registro de presença (check-in)")

    codigo = secrets.token_urlsafe(12)
    cert = Certificado(
        inscricao_id=payload.inscricao_id,
        evento_id=payload.evento_id,
        codigo_certificado=codigo,
        emitido_em=datetime.datetime.utcnow(),
        caminho_pdf=None,
        revogado=False
    )
    db.add(cert)
    db.commit()
    db.refresh(cert)
    return cert


@router.get("/{codigo}", response_model=schemas.CertificadoOut)
def obter_por_codigo(codigo: str, db: Session = Depends(get_db)):
    c = db.query(Certificado).filter(Certificado.codigo_certificado == codigo).first()
    if not c:
        raise HTTPException(status_code=404, detail="Certificado não encontrado")
    return c


@router.get("/usuario/{usuario_id}", response_model=list[schemas.CertificadoOut])
def listar_por_usuario(usuario_id: str, db: Session = Depends(get_db)):
    certs = (
        db.query(Certificado)
        .join(Inscricao, Inscricao.id == Certificado.inscricao_id)
        .filter(Inscricao.usuario_id == usuario_id)
        .all()
    )
    return certs


@router.post("/revogar/{codigo}")
def revogar_certificado(codigo: str, db: Session = Depends(get_db)):
    c = db.query(Certificado).filter(Certificado.codigo_certificado == codigo).first()
    if not c:
        raise HTTPException(status_code=404, detail="Certificado não encontrado")
    c.revogado = True
    db.add(c)
    db.commit()
    return {"message": "Certificado revogado"}
