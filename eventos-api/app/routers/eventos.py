from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.evento import Evento
from app.core.database import get_db

router = APIRouter(prefix="/eventos", tags=["Eventos"])

@router.get("/")
def listar_eventos(db: Session = Depends(get_db)):
    return db.query(Evento).all()
