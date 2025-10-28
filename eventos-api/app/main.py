from fastapi import FastAPI, Request
from app.core.database import Base, engine
from app.routers import usuarios, eventos
from app.middlewares.auditoria import auditoria_middleware

app = FastAPI(title="Eventos API")

# Cria tabelas (somente no início)
Base.metadata.create_all(bind=engine)

# Adiciona middlewares
@app.middleware("http")
async def auditoria(request: Request, call_next):
    return await auditoria_middleware(request, call_next)

# Inclui routers
app.include_router(usuarios.router)
app.include_router(eventos.router)

# Teste básico
@app.get("/ping")
def ping():
    return {"message": "pong"}
