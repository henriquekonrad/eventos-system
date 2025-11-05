"""
Microsserviço de Certificados
Porta: 8007
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from uuid import UUID
import datetime
import secrets
import sys
sys.path.append('..')

from shared.core.database import get_db
from shared.models.certificado import Certificado
from shared.models.inscricao import Inscricao
from shared.models.checkin import Checkin
from shared import schemas
from shared.core.security import require_roles, get_current_user_from_token

app = FastAPI(title="Certificados Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {"service": "certificados-service", "status": "running"}


@app.post("/emitir", response_model=schemas.CertificadoOut, status_code=status.HTTP_201_CREATED)
def emitir_certificado(
    payload: schemas.CertificadoCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("atendente", "administrador"))
):
    """
    Emite um certificado para uma inscrição.
    Requer que o participante tenha feito check-in.
    Apenas atendentes e administradores podem emitir.
    """
    # Verificar se a inscrição existe e pertence ao evento
    inscr = db.query(Inscricao).filter(
        Inscricao.id == payload.inscricao_id,
        Inscricao.evento_id == payload.evento_id
    ).first()
    
    if not inscr:
        raise HTTPException(
            status_code=404,
            detail="Inscrição não encontrada para este evento"
        )
    
    # Verificar se houve check-in
    check = db.query(Checkin).filter(Checkin.inscricao_id == payload.inscricao_id).first()
    
    if not check:
        raise HTTPException(
            status_code=400,
            detail="Não é possível emitir certificado sem registro de presença (check-in)"
        )
    
    # Verificar se já existe certificado
    cert_existente = db.query(Certificado).filter(
        Certificado.inscricao_id == payload.inscricao_id,
        Certificado.evento_id == payload.evento_id
    ).first()
    
    if cert_existente:
        raise HTTPException(
            status_code=400,
            detail="Certificado já foi emitido para esta inscrição"
        )
    
    # Gerar código único do certificado
    codigo = secrets.token_urlsafe(12)
    
    cert = Certificado(
        inscricao_id=payload.inscricao_id,
        evento_id=payload.evento_id,
        codigo_certificado=codigo,
        emitido_em=datetime.datetime.utcnow(),
        caminho_pdf=None,  # Pode ser preenchido depois
        revogado=False
    )
    
    db.add(cert)
    db.commit()
    db.refresh(cert)
    
    return cert


@app.get("/codigo/{codigo}", response_model=schemas.CertificadoOut)
def obter_por_codigo(
    codigo: str,
    db: Session = Depends(get_db)
):
    """
    Endpoint público para validação de certificados.
    Permite verificar autenticidade sem login.
    Útil para empresas validarem certificados de candidatos.
    """
    c = db.query(Certificado).filter(Certificado.codigo_certificado == codigo).first()
    
    if not c:
        raise HTTPException(status_code=404, detail="Certificado não encontrado")
    
    if c.revogado:
        raise HTTPException(
            status_code=400,
            detail="Certificado revogado/inválido"
        )
    
    return c


@app.get("/meus", response_model=list[schemas.CertificadoOut])
def listar_meus_certificados(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_from_token)
):
    """
    Lista todos os certificados do usuário autenticado.
    """
    certs = (
        db.query(Certificado)
        .join(Inscricao, Inscricao.id == Certificado.inscricao_id)
        .filter(Inscricao.usuario_id == current_user.id)
        .all()
    )
    
    return certs


@app.get("/evento/{evento_id}", response_model=list[schemas.CertificadoOut])
def listar_certificados_por_evento(
    evento_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("atendente", "administrador"))
):
    """
    Lista todos os certificados emitidos para um evento.
    Apenas atendentes e administradores.
    """
    certs = db.query(Certificado).filter(Certificado.evento_id == evento_id).all()
    return certs


@app.post("/revogar/{codigo}")
def revogar_certificado(
    codigo: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("atendente", "administrador"))
):
    """
    Revoga um certificado (torna-o inválido).
    Apenas atendentes e administradores podem revogar.
    """
    c = db.query(Certificado).filter(Certificado.codigo_certificado == codigo).first()
    
    if not c:
        raise HTTPException(status_code=404, detail="Certificado não encontrado")
    
    if c.revogado:
        raise HTTPException(
            status_code=400,
            detail="Certificado já estava revogado"
        )
    
    c.revogado = True
    db.add(c)
    db.commit()
    
    return {
        "message": "Certificado revogado com sucesso",
        "codigo": codigo,
        "revogado_em": datetime.datetime.utcnow()
    }


@app.get("/{certificado_id}", response_model=schemas.CertificadoOut)
def obter_certificado(
    certificado_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Obtém um certificado pelo ID.
    """
    cert = db.query(Certificado).filter(Certificado.id == certificado_id).first()
    
    if not cert:
        raise HTTPException(status_code=404, detail="Certificado não encontrado")
    
    return cert


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)