from fastapi import Request
from sqlalchemy.orm import Session
from app.shared.core.database import SessionLocal


async def database_middleware(request: Request, call_next):
    db: Session = SessionLocal()
    request.state.db = db
    
    try:
        response = await call_next(request)
    finally:
        db.close()
    
    return response