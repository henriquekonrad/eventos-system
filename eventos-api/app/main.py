from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import Base, engine, SessionLocal
from app.middlewares.auditoria import auditoria_middleware
from app.routers import auth, usuarios, eventos, inscricoes, checkins, certificados, ingressos

app = FastAPI(title="Eventos API")

# Em produção use migrations (alembic).
Base.metadata.create_all(bind=engine)

# CORS (ajuste allow_origins conforme o front)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware para criar/fechar sessão DB e torná-la disponível em request.state.db
@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    request.state.db = SessionLocal()
    try:
        response = await call_next(request)
        return response
    finally:
        try:
            request.state.db.close()
        except Exception:
            pass

# Middleware de auditoria — usa request.state.db e registra logs na tabela logs_auditoria
@app.middleware("http")
async def auditoria(request: Request, call_next):
    return await auditoria_middleware(request, call_next)

app.include_router(auth.router, prefix="/api")
app.include_router(usuarios.router, prefix="/api")
app.include_router(eventos.router, prefix="/api")
app.include_router(inscricoes.router, prefix="/api")
app.include_router(checkins.router, prefix="/api")
app.include_router(certificados.router, prefix="/api")
app.include_router(ingressos.router, prefix="/api")

@app.get("/ping")
def ping():
    return {"message": "pong"}
