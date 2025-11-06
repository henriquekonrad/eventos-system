from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.core.database import Base

class Evento(Base):
    __tablename__ = "eventos"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    titulo = Column(String, nullable=False)
    descricao = Column(Text)
    inicio_em = Column(DateTime)
    fim_em = Column(DateTime)
