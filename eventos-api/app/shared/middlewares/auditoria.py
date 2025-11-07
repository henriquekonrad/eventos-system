# app/shared/middlewares/auditoria.py
from fastapi import Request, Response
from sqlalchemy.orm import Session
import datetime, traceback
from app.shared.models.log_auditoria import LogAuditoria
from app.shared.core.security import verificar_token_middleware

MAX_PAYLOAD_LENGTH = 5000

async def _get_usuario_id(request: Request):
    """
    Tenta extrair o usuário do header Authorization (JWT) apenas para auditoria.
    Retorna None se não houver token válido.
    """
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None
        payload = verificar_token_middleware(auth_header)
        return payload.get("sub") or payload.get("id")
    except Exception:
        return None

async def auditoria_middleware(request: Request, call_next):
    """
    Auditoria completa: salva payload da requisição e resposta.
    """
    try:
        raw_req_body = await request.body()
        payload_requisicao = raw_req_body.decode("utf-8", errors="ignore")[:MAX_PAYLOAD_LENGTH] if raw_req_body else ""
    except Exception:
        payload_requisicao = ""

    response: Response = await call_next(request)

    try:
        payload_resposta = ""
        if hasattr(response, "body") and response.body:
            payload_resposta = response.body.decode("utf-8", errors="ignore")[:MAX_PAYLOAD_LENGTH]
        elif hasattr(response, "content") and response.content:
            payload_resposta = response.content.decode("utf-8", errors="ignore")[:MAX_PAYLOAD_LENGTH]
    except Exception:
        payload_resposta = ""

    try:
        db: Session = getattr(request.state, "db", None)
        if db is None:
            return response

        usuario_id = await _get_usuario_id(request)

        log = LogAuditoria(
            metodo_http=request.method,
            caminho=request.url.path,
            payload_requisicao=payload_requisicao,
            payload_resposta=payload_resposta,
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

async def auditoria_middleware_light(request: Request, call_next):
    """
    Auditoria leve: apenas metadados, sem payload.
    """
    response: Response = await call_next(request)

    try:
        db: Session = getattr(request.state, "db", None)
        if db is None:
            return response

        usuario_id = await _get_usuario_id(request)

        log = LogAuditoria(
            metodo_http=request.method,
            caminho=request.url.path,
            payload_requisicao="",
            payload_resposta="",
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
