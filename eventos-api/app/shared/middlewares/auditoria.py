from fastapi import Request
from app.shared.helpers.auditoria_helper import AuditoriaService
from app.shared.core.database import SessionLocal
import traceback

async def auditoria_middleware(request: Request, call_next):
    """
    Middleware de auditoria seguindo Single Responsibility Principle.
    
    Responsabilidades:
    1. Capturar metadados da requisição/resposta
    2. Delegar persistência ao Service Layer
    
    NÃO faz:
    - Gerenciamento de sessão DB (usa sua própria)
    - Lógica de negócio
    - Acoplamento com outros middlewares
    """
    
    # Capturar metadados (não lê body para não consumir stream)
    metodo = request.method
    caminho = request.url.path
    ip_cliente = request.client.host if request.client else None
    
    # Obter usuario_id se disponível
    usuario_id = None
    if hasattr(request.state, "user"):
        user = getattr(request.state, "user", None)
        if user:
            usuario_id = getattr(user, "id", None)
    
    # Processar requisição
    response = await call_next(request)
    
    # Registrar auditoria de forma assíncrona (não bloqueia response)
    try:
        # Cria SUA PRÓPRIA sessão (independente de outros middlewares)
        db = SessionLocal()
        try:
            AuditoriaService.registrar_log(
                db=db,
                metodo_http=metodo,
                caminho=caminho,
                codigo_status=response.status_code,
                ip_cliente=ip_cliente,
                usuario_id=usuario_id
            )
        finally:
            db.close()
    except Exception as e:
        # Log de erro, mas NÃO quebra o fluxo da aplicação
        print(f"[AUDITORIA] Falha ao registrar: {e}")
        traceback.print_exc()
    
    return response