from fastapi import Request, Response
from starlette.responses import StreamingResponse
from app.shared.helpers.auditoria_helper import AuditoriaService
from app.shared.core.database import SessionLocal
import traceback


async def auditoria_middleware(request: Request, call_next):
    # 1. CAPTURAR REQUEST BODY
    payload_requisicao = ""
    try:
        body_bytes = await request.body()
        if body_bytes:
            payload_requisicao = body_bytes.decode("utf-8", errors="ignore")
        
        # IMPORTANTE: Permitir que o body seja lido novamente pelos endpoints
        async def receive():
            return {"type": "http.request", "body": body_bytes}
        request._receive = receive
        
    except Exception as e:
        payload_requisicao = f"Erro ao capturar: {str(e)}"
    
    # 2. CAPTURAR METADADOS
    metodo = request.method
    caminho = request.url.path
    ip_cliente = request.client.host if request.client else None
    
    # Obter usuario_id se disponível
    usuario_id = None
    if hasattr(request.state, "user"):
        user = getattr(request.state, "user", None)
        if user:
            usuario_id = getattr(user, "id", None) or user.get("sub")
    
    # 3. PROCESSAR REQUISIÇÃO
    response = await call_next(request)
    
    # 4. CAPTURAR RESPONSE BODY
    payload_resposta = ""
    try:
        if isinstance(response, StreamingResponse):
            response_body = b""
            
            async for chunk in response.body_iterator:
                response_body += chunk
            
            # Decodificar
            payload_resposta = response_body.decode("utf-8", errors="ignore")
            
            response = Response(
                content=response_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
        
    except Exception as e:
        payload_resposta = f"Erro ao capturar: {str(e)}"
    
    # 5. REGISTRAR AUDITORIA
    try:
        db = SessionLocal()
        try:
            AuditoriaService.registrar_log(
                db=db,
                metodo_http=metodo,
                caminho=caminho,
                codigo_status=response.status_code,
                ip_cliente=ip_cliente,
                usuario_id=usuario_id,
                payload_requisicao=payload_requisicao,
                payload_resposta=payload_resposta
            )
        finally:
            db.close()
    except Exception as e:
        print(f"[AUDITORIA] Falha ao registrar: {e}")
        traceback.print_exc()
    
    return response