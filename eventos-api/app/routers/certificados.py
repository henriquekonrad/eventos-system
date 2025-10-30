from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.certificado import Certificado
from app.models.inscricao import Inscricao
from app.models.checkin import Checkin
from app import schemas
from uuid import UUID
import secrets
import datetime

router = APIRouter(prefix="/certificados", tags=["Certificados"])

def to_uuid(id_str: str):
    try:
        return UUID(id_str)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido")

@router.post("/emitir", response_model=schemas.CertificadoOut, status_code=status.HTTP_201_CREATED)
def emitir_certificado(payload: schemas.CertificadoCreate, db: Session = Depends(get_db)):
    iid = to_uuid(payload.inscricao_id)
    eid = to_uuid(payload.evento_id)

    inscr = db.query(Inscricao).filter(Inscricao.id == iid, Inscricao.evento_id == eid).first()
    if not inscr:
        raise HTTPException(status_code=404, detail="Inscrição não encontrada para este evento")

    check = db.query(Checkin).filter(Checkin.inscricao_id == iid).first()
    if not check:
        raise HTTPException(status_code=400, detail="Não é possível emitir certificado sem registro de presença (check-in)")

    codigo = secrets.token_urlsafe(12)
    cert = Certificado(
        inscricao_id=iid,
        evento_id=eid,
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
    uid = to_uuid(usuario_id)
    inscricoes = db.query(Inscricao.id).filter(Inscricao.usuario_id == uid).subquery()
    certs = db.query(Certificado).filter(Certificado.inscricao_id.in_(inscricoes)).all()
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
