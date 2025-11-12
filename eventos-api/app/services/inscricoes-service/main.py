"""
Microsserviço de Inscrições
Porta: 8004
"""
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID, uuid4
from secrets import token_urlsafe
import datetime

from app.shared.core.database import get_db
from app.shared.models.inscricao import Inscricao
from app.shared.models.evento import Evento
from app.shared.models.usuario import Usuario
from app.shared import schemas
from app.shared.middlewares.add import add_common_middlewares
from app.shared.core.security import (
    require_jwt_and_service_key,
    require_service_api_key
)

app = FastAPI(title="Inscricoes Service", version="1.0.0")
add_common_middlewares(app, audit=True)


@app.post("/", status_code=status.HTTP_201_CREATED)
def criar_inscricao_normal(
    evento_id: UUID,
    usuario_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_jwt_and_service_key("inscricoes", "administrador", "atendente"))
):
    """
    Cria uma inscrição normal para um usuário já cadastrado.
    
    REQUER: API Key + JWT + Role (administrador OU atendente)
    """
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    existente = db.query(Inscricao).filter(
        Inscricao.evento_id == evento_id,
        Inscricao.usuario_id == usuario_id
    ).first()
    
    if existente:
        raise HTTPException(status_code=400, detail="Usuário já inscrito neste evento")
    
    inscr = Inscricao(
        evento_id=evento_id,
        usuario_id=usuario_id,
        inscricao_rapida=False,
        status="ativa",
        sincronizado=False
    )
    db.add(inscr)
    db.commit()
    db.refresh(inscr)
    
    return {"inscricao_id": str(inscr.id), "message": "Inscrição criada"}


@app.post("/rapida", status_code=status.HTTP_201_CREATED)
def criar_inscricao_rapida(
    payload: schemas.InscricaoCreateRapida,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_jwt_and_service_key("inscricoes", "administrador", "atendente"))
):
    """
    Cria uma inscrição rápida com criação automática de usuário temporário.
    Útil para eventos onde o participante não tem cadastro prévio.
    
    REQUER: API Key + JWT + Role (administrador OU atendente)
    """
    evento = db.query(Evento).filter(Evento.id == payload.evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    # Gerar email temporário se não fornecido
    email = payload.email_rapido or f"temp_{uuid4()}@rapido.local"
    
    # Criar usuário rápido
    usuario_rapido = Usuario(
        nome=payload.nome_rapido,
        email=email,
        cpf=payload.cpf_rapido,
        senha_hash=token_urlsafe(16),  # senha temporária
        papel="rapido",
        email_verificado=False
    )
    db.add(usuario_rapido)
    db.commit()
    db.refresh(usuario_rapido)
    
    # Criar inscrição vinculada ao usuário rápido
    inscr = Inscricao(
        evento_id=payload.evento_id,
        usuario_id=usuario_rapido.id,
        inscricao_rapida=True,
        nome_rapido=payload.nome_rapido,
        cpf_rapido=payload.cpf_rapido,
        email_rapido=payload.email_rapido,
        status="ativa",
        sincronizado=False
    )
    db.add(inscr)
    db.commit()
    db.refresh(inscr)
    
    return {
        "inscricao_id": str(inscr.id),
        "usuario_id": str(usuario_rapido.id),
        "message": "Inscrição rápida criada com usuário rápido associado"
    }


@app.get("/evento/{evento_id}", response_model=list[schemas.InscricaoOut])
def listar_inscricoes_por_evento(
    evento_id: UUID,
    db: Session = Depends(get_db),
    api_key: None = Depends(require_service_api_key("inscricoes"))
):
    """
    Lista todas as inscrições de um evento específico.
    Útil para relatórios e gestão de participantes.
    
    REQUER: API Key (sem JWT - permite consulta para sistemas de gestão)
    """
    return db.query(Inscricao).filter(Inscricao.evento_id == evento_id).all()


@app.get("/usuario/{usuario_id}", response_model=list[schemas.InscricaoOut])
def listar_inscricoes_por_usuario(
    usuario_id: UUID,
    db: Session = Depends(get_db),
    api_key: None = Depends(require_service_api_key("inscricoes"))
):
    """
    Lista todas as inscrições de um usuário específico.
    Útil para histórico do participante.
    
    REQUER: API Key (sem JWT - permite consulta por ID de usuário)
    """
    return db.query(Inscricao).filter(Inscricao.usuario_id == usuario_id).all()


@app.get("/{inscricao_id}", response_model=schemas.InscricaoOut)
def obter_inscricao(
    inscricao_id: UUID,
    db: Session = Depends(get_db),
    api_key: None = Depends(require_service_api_key("inscricoes"))
):
    """
    Obtém detalhes de uma inscrição específica pelo ID.
    
    REQUER: API Key (sem JWT - busca por ID interno)
    """
    inscr = db.query(Inscricao).filter(Inscricao.id == inscricao_id).first()
    if not inscr:
        raise HTTPException(status_code=404, detail="Inscrição não encontrada")
    return inscr



@app.get("/evento/{evento_id}/estatisticas")
def estatisticas_inscricoes(
    evento_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_jwt_and_service_key("inscricoes", "atendente", "administrador"))
):
    """
    Retorna estatísticas de inscrições de um evento.
    
    REQUER: API Key + JWT + Role (atendente OU administrador)
    """
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    total_ativas = db.query(Inscricao).filter(
        Inscricao.evento_id == evento_id,
        Inscricao.status == "ativa"
    ).count()
    
    total_canceladas = db.query(Inscricao).filter(
        Inscricao.evento_id == evento_id,
        Inscricao.status == "cancelada"
    ).count()
    
    total_rapidas = db.query(Inscricao).filter(
        Inscricao.evento_id == evento_id,
        Inscricao.inscricao_rapida == True
    ).count()
    
    total_normais = db.query(Inscricao).filter(
        Inscricao.evento_id == evento_id,
        Inscricao.inscricao_rapida == False
    ).count()
    
    total_inscricoes = total_ativas + total_canceladas
    
    return {
        "evento_id": str(evento_id),
        "total_inscricoes": total_inscricoes,
        "ativas": total_ativas,
        "canceladas": total_canceladas,
        "inscricoes_rapidas": total_rapidas,
        "inscricoes_normais": total_normais,
        "taxa_cancelamento": round((total_canceladas / total_inscricoes * 100) if total_inscricoes > 0 else 0, 2)
    }

@app.get("/evento/{evento_id}/inscritos")
def listar_inscritos_evento(
    evento_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_jwt_and_service_key("inscricoes", "atendente", "administrador"))
):
    """
    Lista os inscritos de um evento com detalhes básicos:
    id da inscrição, nome, CPF e email.

    REQUER: API Key + JWT + Role (atendente OU administrador)
    """
    inscricoes = db.query(Inscricao).filter(Inscricao.evento_id == evento_id).all()
    if not inscricoes:
        return []

    inscritos = []
    for i in inscricoes:
        if not i.inscricao_rapida:
            usuario = db.query(Usuario).filter(Usuario.id == i.usuario_id).first()
            inscritos.append({
                "id": str(i.id),
                "nome": usuario.nome,
                "cpf": usuario.cpf,
                "email": usuario.email
            })
        else:
            inscritos.append({
                "id": str(i.id),
                "nome": i.nome_rapido,
                "cpf": i.cpf_rapido,
                "email": i.email_rapido
            })

    return inscritos

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)