"""
Microsserviço de Eventos
Porta: 8002
"""
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.shared.core.database import get_db
from app.shared.models.evento import Evento
from app.shared import schemas
from app.shared.core.middleware import add_common_middleware
from app.shared.core.security import (
    require_jwt_and_service_key,
    require_service_api_key
)

app = FastAPI(title="Eventos Service", version="1.0.0")
add_common_middleware(app)


@app.get("/")
def health_check():
    """Público - Health check do serviço"""
    return {"service": "eventos-service", "status": "running"}


@app.post("/eventos", response_model=schemas.EventoOut, status_code=status.HTTP_201_CREATED)
def criar_evento(
    payload: schemas.EventoCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_jwt_and_service_key("eventos", "administrador"))
):
    """
    Cria um novo evento.
    
    REQUER: API Key + JWT + Role "administrador"
    """
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


@app.get("/eventos", response_model=list[schemas.EventoOut])
def listar_eventos(
    db: Session = Depends(get_db),
    api_key: None = Depends(require_service_api_key("eventos"))
):
    """
    Lista todos os eventos ordenados por data de início.
    
    REQUER: API Key (sem JWT - permite listagem para sistemas externos)
    """
    return db.query(Evento).order_by(Evento.inicio_em).all()


@app.get("/eventos/{evento_id}", response_model=schemas.EventoOut)
def obter_evento(
    evento_id: UUID,
    db: Session = Depends(get_db),
    api_key: None = Depends(require_service_api_key("eventos"))
):
    """
    Obtém detalhes de um evento específico pelo ID.
    
    REQUER: API Key (sem JWT - permite consulta para sistemas externos)
    """
    e = db.query(Evento).filter(Evento.id == evento_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    return e


@app.put("/eventos/{evento_id}", response_model=schemas.EventoOut)
def atualizar_evento(
    evento_id: UUID,
    payload: schemas.EventoCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_jwt_and_service_key("eventos", "administrador"))
):
    """
    Atualiza os dados de um evento existente.
    
    REQUER: API Key + JWT + Role "administrador"
    """
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


@app.delete("/eventos/{evento_id}")
def remover_evento(
    evento_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_jwt_and_service_key("eventos", "administrador"))
):
    """
    Remove um evento do sistema.
    
    REQUER: API Key + JWT + Role "administrador"
    """
    e = db.query(Evento).filter(Evento.id == evento_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    db.delete(e)
    db.commit()
    return {"message": "evento removido"}


@app.get("/eventos/publicos/ativos", response_model=list[schemas.EventoOut])
def listar_eventos_publicos(db: Session = Depends(get_db)):
    """
    Lista eventos públicos e ativos (sem necessidade de autenticação).
    Endpoint PÚBLICO para páginas de divulgação.
    
    REQUER: Nada (público para divulgação)
    """
    from datetime import datetime
    
    # Retorna apenas eventos que ainda não acabaram
    agora = datetime.utcnow()
    return (
        db.query(Evento)
        .filter(Evento.fim_em >= agora)
        .order_by(Evento.inicio_em)
        .all()
    )


@app.get("/eventos/{evento_id}/estatisticas")
def estatisticas_evento(
    evento_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_jwt_and_service_key("eventos", "atendente", "administrador"))
):
    """
    Retorna estatísticas de um evento (inscrições, check-ins, certificados).
    
    REQUER: API Key + JWT + Role (atendente OU administrador)
    """
    from shared.models.inscricao import Inscricao
    from shared.models.checkin import Checkin
    from shared.models.certificado import Certificado
    
    # Verificar se evento existe
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    # Contar inscrições
    total_inscricoes = db.query(Inscricao).filter(
        Inscricao.evento_id == evento_id,
        Inscricao.status == "ativa"
    ).count()
    
    # Contar check-ins
    total_checkins = (
        db.query(Checkin)
        .join(Inscricao, Inscricao.id == Checkin.inscricao_id)
        .filter(Inscricao.evento_id == evento_id)
        .count()
    )
    
    # Contar certificados emitidos
    total_certificados = db.query(Certificado).filter(
        Certificado.evento_id == evento_id,
        Certificado.revogado == False
    ).count()
    
    # Calcular taxas
    taxa_presenca = (total_checkins / total_inscricoes * 100) if total_inscricoes > 0 else 0
    taxa_certificacao = (total_certificados / total_checkins * 100) if total_checkins > 0 else 0
    
    return {
        "evento_id": str(evento_id),
        "titulo": evento.titulo,
        "total_inscricoes": total_inscricoes,
        "total_checkins": total_checkins,
        "total_certificados": total_certificados,
        "taxa_presenca": round(taxa_presenca, 2),
        "taxa_certificacao": round(taxa_certificacao, 2),
        "ausentes": total_inscricoes - total_checkins
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)