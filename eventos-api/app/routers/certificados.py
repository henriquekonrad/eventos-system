from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.certificado import Certificado
from app.models.inscricao import Inscricao
from app.models.checkin import Checkin
from app.models.usuario import Usuario
from app import schemas
import secrets
import datetime
from app.core.security import require_roles
from app.routers.auth import get_current_user

router = APIRouter(prefix="/certificados", tags=["Certificados"])

@router.post("/emitir",
    response_model=schemas.CertificadoOut,
    status_code=status.HTTP_201_CREATED)
def emitir_certificado(
    payload: schemas.CertificadoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles("atendente", "administrador"))
):
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
    """
    Endpoint público para validação de certificados.
    Permite verificar autenticidade sem login.
    """
    c = db.query(Certificado).filter(Certificado.codigo_certificado == codigo).first()
    if not c:
        raise HTTPException(status_code=404, detail="Certificado não encontrado")
    if c.revogado:
        raise HTTPException(status_code=400, detail="Certificado revogado/inválido")
    return c


@router.get("/meus", response_model=list[schemas.CertificadoOut])
def listar_meus_certificados(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    certs = (
        db.query(Certificado)
        .join(Inscricao, Inscricao.id == Certificado.inscricao_id)
        .filter(Inscricao.usuario_id == current_user.id)
        .all()
    )
    return certs

@router.post("/revogar/{codigo}")
def revogar_certificado(
    codigo: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles("atendente", "administrador"))
):
    c = db.query(Certificado).filter(Certificado.codigo_certificado == codigo).first()
    if not c:
        raise HTTPException(status_code=404, detail="Certificado não encontrado")
    c.revogado = True
    db.add(c)
    db.commit()
    return {"message": "Certificado revogado"}
