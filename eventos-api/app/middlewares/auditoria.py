from fastapi import Request
import datetime
from sqlalchemy.orm import Session
from app.models.log_auditoria import LogAuditoria

async def auditoria_middleware(request: Request, call_next):
    response = await call_next(request)
    try:
        db: Session = request.state.db
        log = LogAuditoria(
            metodo_http=request.method,
            caminho=request.url.path,
            payload_requisicao=await request.body(),
            codigo_status=response.status_code,
            ip_cliente=request.client.host,
            ocorrido_em=datetime.datetime.utcnow()
        )
        db.add(log)
        db.commit()
    except Exception:
        pass
    return response
