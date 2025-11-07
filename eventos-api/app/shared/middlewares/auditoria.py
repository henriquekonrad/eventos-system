"""
shared/middlewares/auditoria.py
Middleware de auditoria para registrar todas as requisições
"""
from fastapi import Request, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import datetime
import traceback
import io
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
    # Capturar payload da requisição
    try:
        raw_req_body = await request.body()
        if raw_req_body:
            payload_requisicao = raw_req_body.decode("utf-8", errors="ignore")
            # Limitar tamanho do payload
            if len(payload_requisicao) > 5000:
                payload_requisicao = payload_requisicao[:5000] + "... (truncado)"
        else:
            payload_requisicao = ""
    except Exception as e:
        payload_requisicao = f"Erro ao capturar: {str(e)}"
    
    # Processar a requisição
    response = await call_next(request)
    
    # Capturar payload da resposta
    payload_resposta = ""
    try:
        # Para StreamingResponse, precisamos consumir o corpo
        if isinstance(response, StreamingResponse):
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk
            
            payload_resposta = response_body.decode("utf-8", errors="ignore")
            
            # Recriar a resposta com o mesmo corpo
            response = Response(
                content=response_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
        elif hasattr(response, "body"):
            body = response.body
            if isinstance(body, (bytes, bytearray)):
                payload_resposta = body.decode("utf-8", errors="ignore")
            else:
                payload_resposta = str(body)
        
        # Limitar tamanho da resposta
        if len(payload_resposta) > 5000:
            payload_resposta = payload_resposta[:5000] + "... (truncado)"
    except Exception as e:
        payload_resposta = f"Erro ao capturar: {str(e)}"
    
    # Salvar log de auditoria
    try:
        db: Session = getattr(request.state, "db", None)
        if db is None:
            print("[AUDITORIA] AVISO: request.state.db não encontrado!")
            return response
        
        # Obter usuario_id se existir
        usuario_id = None
        if hasattr(request.state, "user"):
            user = getattr(request.state, "user", None)
            if user:
                usuario_id = getattr(user, "id", None)
        
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
    response = await call_next(request)
    
    try:
        db: Session = getattr(request.state, "db", None)
        if db is None:
            print("[AUDITORIA LIGHT] AVISO: request.state.db não encontrado!")
            return response
        
        # Obter usuario_id se existir
        usuario_id = None
        if hasattr(request.state, "user"):
            user = getattr(request.state, "user", None)
            if user:
                usuario_id = getattr(user, "id", None)
        
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
        traceback.print_exc()
    
    return response