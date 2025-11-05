"""
Microsserviço de Eventos
Porta: 8002
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from uuid import UUID
import sys
sys.path.append('..')

from shared.core.database import get_db
from shared.models.evento import Evento
from shared import schemas
from shared.core.security import require_roles

app = FastAPI(title="Eventos Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {"service": "eventos-service", "status": "running"}


@app.post("/", response_model=schemas.EventoOut, status_code=status.HTTP_201_CREATED)
def criar_evento(
    payload: schemas.EventoCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("administrador"))
):
    """
    Cria um novo evento.
    Apenas administradores podem criar eventos.
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


@app.get("/", response_model=list[schemas.EventoOut])
def listar_eventos(db: Session = Depends(get_db)):
    """
    Lista todos os eventos ordenados por data de início.
    Endpoint público (não precisa de autenticação).
    """
    return db.query(Evento).order_by(Evento.inicio_em).all()


@app.get("/{evento_id}", response_model=schemas.EventoOut)
def obter_evento(evento_id: UUID, db: Session = Depends(get_db)):
    """
    Obtém detalhes de um evento específico pelo ID.
    Endpoint público.
    """
    e = db.query(Evento).filter(Evento.id == evento_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    return e


@app.put("/{evento_id}", response_model=schemas.EventoOut)
def atualizar_evento(
    evento_id: UUID,
    payload: schemas.EventoCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("administrador"))
):
    """
    Atualiza os dados de um evento existente.
    Apenas administradores podem atualizar eventos.
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


@app.delete("/{evento_id}")
def remover_evento(
    evento_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("administrador"))
):
    """
    Remove um evento do sistema.
    Apenas administradores podem deletar eventos.
    """
    e = db.query(Evento).filter(Evento.id == evento_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    db.delete(e)
    db.commit()
    return {"message": "evento removido"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)