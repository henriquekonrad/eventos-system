from sqlalchemy import Column, DateTime, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid, datetime
from app.core.database import Base

class Checkin(Base):
    __tablename__ = "checkins"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    inscricao_id = Column(UUID(as_uuid=True), ForeignKey("inscricoes.id"), nullable=False)
    ingresso_id = Column(UUID(as_uuid=True), ForeignKey("ingressos.id", nullable=False))
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", nullable=False))
    ocorrido_em = Column(DateTime, default=datetime.datetime.utcnow)
