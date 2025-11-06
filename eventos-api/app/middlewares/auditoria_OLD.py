from fastapi import Request, Response
import datetime, traceback
from app.models.log_auditoria import LogAuditoria

async def auditoria_middleware(request: Request, call_next):
    """
    Registra um log na tabela logs_auditoria para cada request.
    """
    try:
        try:
            raw_req_body = await request.body()
            payload_requisicao = raw_req_body.decode("utf-8", errors="ignore")
        except Exception:
            payload_requisicao = ""
    except Exception:
        payload_requisicao = ""

    response: Response = await call_next(request)

    payload_resposta = ""
    try:
        if hasattr(response, "body"):
            body = response.body
            if isinstance(body, (bytes, bytearray)):
                payload_resposta = body.decode("utf-8", errors="ignore")
            else:
                try:
                    payload_resposta = str(body)
                except Exception:
                    payload_resposta = ""
        else:
            try:
                content = getattr(response, "content", None)
                if isinstance(content, (bytes, bytearray)):
                    payload_resposta = content.decode("utf-8", errors="ignore")
                else:
                    payload_resposta = str(content) if content is not None else ""
            except Exception:
                payload_resposta = ""
    except Exception:
        payload_resposta = ""

    try:
        db = getattr(request.state, "db", None)
        if db is None:
            return response

        usuario_id = None
        if hasattr(request.state, "user") and getattr(request.state, "user"):
            u = getattr(request.state, "user")
            usuario_id = getattr(u, "id", None)

        log = LogAuditoria(
            metodo_http=request.method,
            caminho=request.url.path,
            payload_requisicao=payload_requisicao,
            payload_resposta=payload_resposta,
            codigo_status=response.status_code,
            ip_cliente=(request.client.host if request.client else None),
            usuario_id=usuario_id,
            ocorrido_em=datetime.datetime.utcnow()
        )
        db.add(log)
        db.commit()
    except Exception:
        traceback.print_exc()

    return response
