from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.usuario import Usuario
from app.core.database import get_db

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@router.get("/")
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(Usuario).all()
