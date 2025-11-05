"""
Microsserviço de Ingressos
Porta: 8005
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from uuid import UUID, uuid4
from typing import List
import datetime
import hashlib
import sys
sys.path.append('..')

from shared.core.database import get_db
from shared.models.ingresso import Ingresso
from shared.models.inscricao import Inscricao
from shared.models.evento import Evento
from shared.schemas import IngressoSchema
from shared.core.security import require_roles

app = FastAPI(title="Ingressos Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {"service": "ingressos-service", "status": "running"}


@app.get("/evento/{evento_id}", response_model=List[IngressoSchema])
def listar_ingressos_por_evento(
    evento_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Lista todos os ingressos de um evento específico.
    Endpoint público (não precisa de autenticação).
    """
    ingressos = db.query(Ingresso).filter(Ingresso.evento_id == evento_id).all()
    
    if not ingressos:
        raise HTTPException(
            status_code=404,
            detail="Nenhum ingresso encontrado para este evento"
        )
    
    return ingressos


@app.post("/inscricao/{inscricao_id}", response_model=IngressoSchema, status_code=status.HTTP_201_CREATED)
def criar_ingresso(
    inscricao_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("administrador", "atendente"))
):
    """
    Cria um ingresso para uma inscrição existente.
    Apenas administradores e atendentes podem criar ingressos.
    """
    inscricao = db.query(Inscricao).filter(Inscricao.id == inscricao_id).first()
    if not inscricao:
        raise HTTPException(status_code=404, detail="Inscrição não encontrada")
    
    evento = db.query(Evento).filter(Evento.id == inscricao.evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    # Gerar código único do ingresso
    codigo = f"ING-{uuid4().hex[:8].upper()}"
    
    # Gerar token QR único
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


@app.get("/validar/{token_qr}")
def validar_ingresso(
    token_qr: str,
    db: Session = Depends(get_db)
):
    """
    Valida um ingresso através do token QR.
    Endpoint público para leitores de QR Code.
    """
    ingresso = db.query(Ingresso).filter(Ingresso.token_qr == token_qr).first()
    
    if not ingresso:
        raise HTTPException(
            status_code=404,
            detail="Ingresso inválido ou não encontrado"
        )
    
    if ingresso.status == "usado":
        raise HTTPException(
            status_code=400,
            detail="Ingresso já foi utilizado"
        )
    
    return {
        "mensagem": "Ingresso válido",
        "ingresso_id": str(ingresso.id),
        "evento_id": str(ingresso.evento_id),
        "inscricao_id": str(ingresso.inscricao_id),
        "codigo": ingresso.codigo_ingresso,
        "status": ingresso.status,
        "emitido_em": ingresso.emitido_em
    }


@app.post("/usar/{ingresso_id}")
def marcar_ingresso_usado(
    ingresso_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("administrador", "atendente"))
):
    """
    Marca um ingresso como usado (check-in realizado).
    Apenas administradores e atendentes podem marcar.
    """
    ingresso = db.query(Ingresso).filter(Ingresso.id == ingresso_id).first()
    
    if not ingresso:
        raise HTTPException(status_code=404, detail="Ingresso não encontrado")
    
    if ingresso.status == "usado":
        raise HTTPException(
            status_code=400,
            detail="Ingresso já foi utilizado anteriormente"
        )
    
    ingresso.status = "usado"
    db.commit()
    db.refresh(ingresso)
    
    return {
        "mensagem": "Check-in realizado com sucesso",
        "ingresso": ingresso.codigo_ingresso,
        "horario": datetime.datetime.utcnow()
    }


@app.get("/{ingresso_id}", response_model=IngressoSchema)
def obter_ingresso(
    ingresso_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Obtém detalhes de um ingresso específico pelo ID.
    """
    ingresso = db.query(Ingresso).filter(Ingresso.id == ingresso_id).first()
    
    if not ingresso:
        raise HTTPException(status_code=404, detail="Ingresso não encontrado")
    
    return ingresso


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)