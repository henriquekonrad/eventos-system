"""
Microsserviço de Ingressos
Porta: 8005
"""
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID, uuid4
from typing import List
import datetime
import hashlib

from app.shared.core.database import get_db
from app.shared.models.ingresso import Ingresso
from app.shared.models.inscricao import Inscricao
from app.shared.models.evento import Evento
from app.shared.schemas import IngressoSchema
from app.shared.middlewares.add import add_common_middlewares
from app.shared.core.security import (
    require_jwt_and_service_key,
    require_service_api_key
)

app = FastAPI(title="Ingressos Service", version="1.0.0")
add_common_middlewares(app, audit=True)


@app.get("/evento/{evento_id}", response_model=List[IngressoSchema])
def listar_ingressos_por_evento(
    evento_id: UUID,
    db: Session = Depends(get_db),
    api_key: None = Depends(require_service_api_key("ingressos"))
):
    """
    Lista todos os ingressos de um evento específico.
    Útil para relatórios e gestão de ingressos.
    
    REQUER: API Key (sem JWT - permite consulta para sistemas de gestão)
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
    current_user: dict = Depends(require_jwt_and_service_key("ingressos", "administrador", "atendente"))
):
    """
    Cria um ingresso para uma inscrição existente.
    Gera automaticamente:
    - Código único do ingresso (formato: ING-XXXXXXXX)
    - Token QR para validação (hash SHA256)
    
    REQUER: API Key + JWT + Role (administrador OU atendente)
    """
    inscricao = db.query(Inscricao).filter(Inscricao.id == inscricao_id).first()
    if not inscricao:
        raise HTTPException(status_code=404, detail="Inscrição não encontrada")
    
    evento = db.query(Evento).filter(Evento.id == inscricao.evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    ingresso_existente = db.query(Ingresso).filter(
        Ingresso.inscricao_id == inscricao_id
    ).first()
    
    if ingresso_existente:
        raise HTTPException(
            status_code=400,
            detail="Já existe um ingresso para esta inscrição"
        )
    
    codigo = f"ING-{uuid4().hex[:8].upper()}"
    
    # Gerar token QR único (hash SHA256)
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
    Endpoint PÚBLICO usado por leitores de QR Code na entrada do evento.
    Não requer autenticação para permitir validação rápida na portaria.
    
    REQUER: Nada (público para validação na entrada)
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
    current_user: dict = Depends(require_jwt_and_service_key("ingressos", "administrador", "atendente"))
):
    """
    Marca um ingresso como usado (check-in realizado).
    Uma vez marcado, não pode ser utilizado novamente.
    
    REQUER: API Key + JWT + Role (administrador OU atendente)
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
    db: Session = Depends(get_db),
    api_key: None = Depends(require_service_api_key("ingressos"))
):
    """
    Obtém detalhes de um ingresso específico pelo ID.
    Útil para consultas internas e sistemas de gestão.
    
    REQUER: API Key (sem JWT - busca por ID interno)
    """
    ingresso = db.query(Ingresso).filter(Ingresso.id == ingresso_id).first()
    
    if not ingresso:
        raise HTTPException(status_code=404, detail="Ingresso não encontrado")
    
    return ingresso


@app.get("/inscricao/{inscricao_id}/ingresso", response_model=IngressoSchema)
def obter_ingresso_por_inscricao(
    inscricao_id: UUID,
    db: Session = Depends(get_db),
    api_key: None = Depends(require_service_api_key("ingressos"))
):
    """
    Obtém o ingresso de uma inscrição específica.
    Retorna erro 404 se a inscrição não tiver ingresso emitido.
    
    REQUER: API Key (sem JWT - consulta por inscrição)
    """
    ingresso = db.query(Ingresso).filter(Ingresso.inscricao_id == inscricao_id).first()
    
    if not ingresso:
        raise HTTPException(
            status_code=404,
            detail="Ingresso não encontrado para esta inscrição"
        )
    
    return ingresso


@app.get("/evento/{evento_id}/estatisticas")
def estatisticas_ingressos(
    evento_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_jwt_and_service_key("ingressos", "atendente", "administrador"))
):
    """
    Retorna estatísticas de ingressos de um evento.
    
    REQUER: API Key + JWT + Role (atendente OU administrador)
    """
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    total_emitidos = db.query(Ingresso).filter(
        Ingresso.evento_id == evento_id,
        Ingresso.status == "emitido"
    ).count()
    
    total_usados = db.query(Ingresso).filter(
        Ingresso.evento_id == evento_id,
        Ingresso.status == "usado"
    ).count()
    
    total_ingressos = db.query(Ingresso).filter(
        Ingresso.evento_id == evento_id
    ).count()
    
    # Calcular taxa de utilização
    taxa_utilizacao = (total_usados / total_ingressos * 100) if total_ingressos > 0 else 0
    
    return {
        "evento_id": str(evento_id),
        "total_ingressos": total_ingressos,
        "emitidos": total_emitidos,
        "usados": total_usados,
        "taxa_utilizacao": round(taxa_utilizacao, 2),
        "nao_usados": total_emitidos
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)