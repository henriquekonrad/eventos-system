from fastapi import Request, Response
from sqlalchemy.orm import Session
import datetime
import traceback
import json
from app.shared.models.log_auditoria import LogAuditoria

async def auditoria_middleware(request: Request, call_next):
    """
    Registra um log na tabela logs_auditoria para cada request.
    
    Captura:
    - Método HTTP
    - Caminho da requisição
    - Payload da requisição
    - Payload da resposta
    - Código de status
    - IP do cliente
    - ID do usuário (se autenticado)
    """
    try:
        raw_req_body = await request.body()
        if raw_req_body:
            payload_requisicao = raw_req_body.decode("utf-8", errors="ignore")
            # Limitar tamanho do payload (para evitar logs gigantes)
            if len(payload_requisicao) > 5000:
                payload_requisicao = payload_requisicao[:5000] + "... (truncado)"
        else:
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
        
        # Limitar tamanho da resposta
        if len(payload_resposta) > 5000:
            payload_resposta = payload_resposta[:5000] + "... (truncado)"
    except Exception:
        payload_resposta = ""
    
    try:
        db: Session = getattr(request.state, "db", None)
        if db is None:
            return response
        
        # Obter usuario
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
    except Exception as e:
        print(f"[AUDITORIA] Erro ao salvar log: {e}")
        traceback.print_exc()
    
    return response


async def auditoria_middleware_light(request: Request, call_next):
    """
    Versão leve da auditoria - não salva payloads (apenas metadados)
    Útil para serviços com alto volume de requisições
    """
    response: Response = await call_next(request)
    
    try:
        db: Session = getattr(request.state, "db", None)
        if db is None:
            return response
        
        usuario_id = None
        if hasattr(request.state, "user") and getattr(request.state, "user"):
            u = getattr(request.state, "user")
            usuario_id = getattr(u, "id", None)
        
        from shared.models.log_auditoria import LogAuditoria
        
        log = LogAuditoria(
            metodo_http=request.method,
            caminho=request.url.path,
            payload_requisicao="",  # Não salva payload na versão light
            payload_resposta="",
            codigo_status=response.status_code,
            ip_cliente=(request.client.host if request.client else None),
            usuario_id=usuario_id,
            ocorrido_em=datetime.datetime.utcnow()
        )
        
        db.add(log)
        db.commit()
    except Exception as e:
        print(f"[AUDITORIA LIGHT] Erro ao salvar log: {e}")
    
    return response