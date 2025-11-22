"""
CHECKINS SERVICE - Porta: 8006
Atualizado: emite certificado automaticamente após check-in
"""
import hashlib
import logging
import httpx
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID, uuid4
from passlib.context import CryptContext
import datetime
import secrets
import os

from app.shared.core.database import get_db
from app.shared.models.checkin import Checkin
from app.shared.models.inscricao import Inscricao
from app.shared.models.evento import Evento
from app.shared.models.usuario import Usuario
from app.shared.middlewares.add import add_common_middlewares
from app.shared.core.security import require_jwt_and_service_key, require_service_api_key
from app.shared.models.ingresso import Ingresso
from app.shared.helpers.email_helper import enviar_email_sync

logger = logging.getLogger(__name__)

app = FastAPI(title="Checkins Service", version="1.0.0")
add_common_middlewares(app, audit=True)

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

# URLs dos outros serviços
CERTIFICADOS_URL = os.getenv("CERTIFICADOS_URL", "http://localhost:8007")
CERTIFICADOS_API_KEY = os.getenv("CERTIFICADOS_API_KEY", "")


async def emitir_certificado_automatico(inscricao_id: UUID):
    """Chama o serviço de certificados para emitir certificado automaticamente"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{CERTIFICADOS_URL}/emitir-automatico/{inscricao_id}",
                headers={"x-api-key": CERTIFICADOS_API_KEY},
                timeout=10.0
            )
            if response.status_code in [200, 201]:
                logger.info(f"✅ Certificado emitido para inscrição {inscricao_id}")
                return response.json()
            else:
                logger.warning(f"⚠️ Erro ao emitir certificado: {response.status_code}")
    except Exception as e:
        logger.error(f"❌ Erro ao chamar serviço de certificados: {e}")
    return None


@app.post("/", status_code=status.HTTP_201_CREATED)
async def registrar_checkin(
    inscricao_id: UUID,
    ingresso_id: UUID,
    usuario_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_jwt_and_service_key("checkins", "atendente", "administrador"))
):
    """Registra check-in e emite certificado automaticamente"""
    inscr = db.query(Inscricao).filter(Inscricao.id == inscricao_id).first()
    if not inscr:
        raise HTTPException(status_code=404, detail="Inscrição não encontrada")
    
    existente = db.query(Checkin).filter(
        Checkin.inscricao_id == inscricao_id,
        Checkin.ingresso_id == ingresso_id
    ).first()
    
    if existente:
        raise HTTPException(status_code=400, detail="Check-in já registrado para este ingresso")
    
    try:
        check = Checkin(
            inscricao_id=inscricao_id,
            ingresso_id=ingresso_id,
            usuario_id=usuario_id,
            ocorrido_em=datetime.datetime.utcnow()
        )
        db.add(check)
        inscr.sincronizado = False
        db.commit()
        
        # Emitir certificado automaticamente
        certificado = await emitir_certificado_automatico(inscricao_id)
        
        # Enviar email
        try:
            evento = db.query(Evento).filter(Evento.id == inscr.evento_id).first()
            usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
            
            if usuario and evento and usuario.email and "@" in usuario.email:
                enviar_email_sync(
                    to=usuario.email,
                    template="checkin",
                    data={"nome": usuario.nome, "evento": evento.titulo}
                )
        except Exception as e:
            logger.warning(f"Erro ao enviar email: {e}")
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao registrar check-in: {e}")
    
    return {
        "id": str(check.id),
        "ocorrido_em": check.ocorrido_em,
        "certificado_emitido": certificado is not None,
        "message": "Check-in registrado com sucesso"
    }


@app.post("/rapido", status_code=status.HTTP_201_CREATED)
async def checkin_rapido(
    evento_id: UUID,
    nome: str,
    cpf: str,
    email: str,
    ingresso_id: UUID | None = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_jwt_and_service_key("checkins", "atendente", "administrador"))
):
    """Check-in rápido com emissão automática de certificado"""
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    try:
        user = db.query(Usuario).filter(Usuario.email == email).first()
        senha_temp = None
        
        if not user:
            senha_temp = "temp_" + secrets.token_hex(4)
            user = Usuario(
                nome=nome, email=email, cpf=cpf,
                senha_hash=pwd.hash(senha_temp), papel="rapido"
            )
            db.add(user)
            db.flush()
        
        inscr = db.query(Inscricao).filter(
            Inscricao.evento_id == evento_id,
            Inscricao.usuario_id == user.id
        ).first()
        
        if not inscr:
            inscr = Inscricao(
                evento_id=evento_id, usuario_id=user.id, inscricao_rapida=True,
                nome_rapido=nome, cpf_rapido=cpf, email_rapido=email,
                status="ativa", sincronizado=False
            )
            db.add(inscr)
            db.flush()

        if not ingresso_id:
            ingresso = db.query(Ingresso).filter(Ingresso.inscricao_id == inscr.id).first()
            
            if not ingresso:
                codigo = f"ING-{uuid4().hex[:8].upper()}"
                token_qr = hashlib.sha256(f"{codigo}-{inscr.id}".encode()).hexdigest()
                ingresso = Ingresso(
                    inscricao_id=inscr.id, evento_id=evento_id, codigo_ingresso=codigo,
                    token_qr=token_qr, status="emitido", emitido_em=datetime.datetime.utcnow()
                )
                db.add(ingresso)
                db.flush()
            ingresso_id = ingresso.id
        
        check_existente = db.query(Checkin).filter(Checkin.inscricao_id == inscr.id).first()
        if check_existente:
            raise HTTPException(status_code=400, detail="Check-in já foi realizado")
        
        check = Checkin(
            inscricao_id=inscr.id, ingresso_id=ingresso_id,
            usuario_id=user.id, ocorrido_em=datetime.datetime.utcnow()
        )
        db.add(check)
        db.commit()
        
        # Emitir certificado automaticamente
        certificado = await emitir_certificado_automatico(inscr.id)
        
        # Enviar email
        try:
            if email and "@" in email:
                enviar_email_sync(
                    to=email, template="checkin",
                    data={"nome": nome, "evento": evento.titulo}
                )
        except Exception as e:
            logger.warning(f"Erro ao enviar email: {e}")
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro: {e}")
    
    return {
        "inscricao_id": str(inscr.id),
        "checkin_id": str(check.id),
        "usuario_id": str(user.id),
        "usuario_email": user.email,
        "senha_temporaria": senha_temp,
        "certificado_emitido": certificado is not None,
        "message": "Check-in rápido realizado com sucesso"
    }


@app.get("/inscricao/{inscricao_id}")
def verificar_checkin(
    inscricao_id: UUID,
    db: Session = Depends(get_db),
    api_key: None = Depends(require_service_api_key("checkins"))
):
    """Verifica se uma inscrição possui check-in"""
    checkins = db.query(Checkin).filter(Checkin.inscricao_id == inscricao_id).all()
    
    if not checkins:
        return {"inscricao_id": str(inscricao_id), "tem_checkin": False, "total_checkins": 0}
    
    return {
        "inscricao_id": str(inscricao_id),
        "tem_checkin": True,
        "total_checkins": len(checkins),
        "checkins": [{"id": str(c.id), "ocorrido_em": c.ocorrido_em, "ingresso_id": str(c.ingresso_id)} for c in checkins]
    }


@app.get("/evento/{evento_id}")
def listar_checkins_evento(
    evento_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_jwt_and_service_key("checkins", "atendente", "administrador"))
):
    """Lista todos os check-ins de um evento"""
    checkins = db.query(Checkin).join(Inscricao).filter(Inscricao.evento_id == evento_id).all()
    
    return {
        "evento_id": str(evento_id),
        "total_checkins": len(checkins),
        "checkins": [
            {"id": str(c.id), "inscricao_id": str(c.inscricao_id), "usuario_id": str(c.usuario_id), "ingresso_id": str(c.ingresso_id), "ocorrido_em": c.ocorrido_em}
            for c in checkins
        ]
    }


@app.get("/estatisticas/{evento_id}")
def estatisticas_checkin(
    evento_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_jwt_and_service_key("checkins", "atendente", "administrador"))
):
    """Retorna estatísticas de check-in"""
    total_inscricoes = db.query(Inscricao).filter(Inscricao.evento_id == evento_id, Inscricao.status == "ativa").count()
    total_checkins = db.query(Checkin).join(Inscricao).filter(Inscricao.evento_id == evento_id).count()
    taxa = (total_checkins / total_inscricoes * 100) if total_inscricoes > 0 else 0
    
    return {
        "evento_id": str(evento_id), "total_inscricoes": total_inscricoes,
        "total_checkins": total_checkins, "taxa_presenca": round(taxa, 2),
        "ausentes": total_inscricoes - total_checkins
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)