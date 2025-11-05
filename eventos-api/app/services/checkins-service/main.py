"""
Microsserviço de Check-ins
Porta: 8006
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from uuid import UUID, uuid4
from passlib.context import CryptContext
import datetime
import secrets
import sys
sys.path.append('..')

from shared.core.database import get_db
from shared.models.checkin import Checkin
from shared.models.inscricao import Inscricao
from shared.models.evento import Evento
from shared.models.usuario import Usuario
from shared.core.security import require_roles

app = FastAPI(title="Checkins Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


@app.get("/")
def health_check():
    return {"service": "checkins-service", "status": "running"}


@app.post("/", status_code=status.HTTP_201_CREATED)
def registrar_checkin(
    inscricao_id: UUID,
    ingresso_id: UUID,
    usuario_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("atendente", "administrador"))
):
    inscr = db.query(Inscricao).filter(Inscricao.id == inscricao_id).first()
    if not inscr:
        raise HTTPException(status_code=404, detail="Inscrição não encontrada")
    
    existente = (
        db.query(Checkin)
        .filter(
            Checkin.inscricao_id == inscricao_id,
            Checkin.ingresso_id == ingresso_id
        )
        .first()
    )
    
    if existente:
        raise HTTPException(
            status_code=400,
            detail="Check-in já registrado para este ingresso"
        )
    
    try:
        with db.begin():
            check = Checkin(
                inscricao_id=inscricao_id,
                ingresso_id=ingresso_id,
                usuario_id=usuario_id,
                ocorrido_em=datetime.datetime.utcnow()
            )
            db.add(check)
            
            inscr.sincronizado = False
            db.add(inscr)
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao registrar check-in: {e}"
        )
    
    return {
        "id": str(check.id),
        "ocorrido_em": check.ocorrido_em,
        "message": "Check-in registrado com sucesso"
    }


@app.post("/rapido", status_code=status.HTTP_201_CREATED)
def checkin_rapido(
    evento_id: UUID,
    nome: str,
    cpf: str,
    email: str,
    ingresso_id: UUID | None = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("atendente", "administrador"))
):
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    try:
        with db.begin():
            user = db.query(Usuario).filter(Usuario.email == email).first()
            senha_temp = None
            
            if not user:
                senha_temp = "temp_" + secrets.token_hex(4)
                user = Usuario(
                    nome=nome,
                    email=email,
                    cpf=cpf,
                    senha_hash=pwd.hash(senha_temp),
                    papel="rapido",
                    ativo=True,
                )
                db.add(user)
                db.flush()
            
            inscr_existente = db.query(Inscricao).filter(
                Inscricao.evento_id == evento_id,
                Inscricao.usuario_id == user.id
            ).first()
            
            if inscr_existente:
                inscr = inscr_existente
            else:
                inscr = Inscricao(
                    evento_id=evento_id,
                    usuario_id=user.id,
                    inscricao_rapida=True,
                    nome_rapido=nome,
                    cpf_rapido=cpf,
                    email_rapido=email,
                    status="ativa",
                    sincronizado=False
                )
                db.add(inscr)
                db.flush()
            
            check_existente = db.query(Checkin).filter(
                Checkin.inscricao_id == inscr.id
            ).first()
            
            if check_existente:
                raise HTTPException(
                    status_code=400,
                    detail="Check-in já foi realizado para esta inscrição"
                )
            
            check = Checkin(
                inscricao_id=inscr.id,
                ingresso_id=ingresso_id or uuid4(),
                usuario_id=user.id,
                ocorrido_em=datetime.datetime.utcnow()
            )
            db.add(check)
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao registrar check-in rápido: {e}"
        )
    
    return {
        "inscricao_id": str(inscr.id),
        "checkin_id": str(check.id),
        "usuario_id": str(user.id),
        "usuario_email": user.email,
        "senha_temporaria": senha_temp,
        "message": "Check-in rápido realizado com sucesso"
    }


@app.get("/inscricao/{inscricao_id}")
def verificar_checkin(inscricao_id: UUID, db: Session = Depends(get_db)):
    checkins = db.query(Checkin).filter(Checkin.inscricao_id == inscricao_id).all()
    
    if not checkins:
        return {
            "inscricao_id": str(inscricao_id),
            "tem_checkin": False,
            "total_checkins": 0
        }
    
    return {
        "inscricao_id": str(inscricao_id),
        "tem_checkin": True,
        "total_checkins": len(checkins),
        "checkins": [
            {
                "id": str(c.id),
                "ocorrido_em": c.ocorrido_em,
                "ingresso_id": str(c.ingresso_id)
            }
            for c in checkins
        ]
    }
