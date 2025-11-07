from fastapi import Request, Response
from sqlalchemy.orm import Session
import datetime, traceback
from app.shared.models.log_auditoria import LogAuditoria
from app.shared.core.security import verificar_token_middleware
import os

async def auditoria_middleware(request: Request, call_next):
    response: Response = await call_next(request)
    
    try:
        # Decodificar JWT só para auditoria
        usuario_id = None
        auth_header = request.headers.get("Authorization")
        if auth_header:
            try:
                payload = verificar_token_middleware(auth_header)
                usuario_id = payload.get("sub") or payload.get("id")
            except Exception:
                usuario_id = None
        
        # Payload da requisição
        try:
            raw_req_body = await request.body()
            payload_requisicao = raw_req_body.decode("utf-8", errors="ignore")
        except Exception:
            payload_requisicao = ""
        
        # Payload da resposta
        try:
            if hasattr(response, "body") and response.body:
                payload_resposta = response.body.decode("utf-8", errors="ignore")
            else:
                payload_resposta = ""
        except Exception:
            payload_resposta = ""
        
        db: Session = getattr(request.state, "db", None)
        if db:
            log = LogAuditoria(
                metodo_http=request.method,
                caminho=request.url.path,
                payload_requisicao=payload_requisicao[:5000],
                payload_resposta=payload_resposta[:5000],
                codigo_status=response.status_code,
                ip_cliente=request.client.host if request.client else None,
                usuario_id=usuario_id,
                ocorrido_em=datetime.datetime.utcnow()
            )
            db.add(log)
            db.commit()
            
    except Exception:
        traceback.print_exc()
    
    return response
