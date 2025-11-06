from sqlalchemy import Column, DateTime, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid, datetime
from app.shared.core.database import Base

class Checkin(Base):
    __tablename__ = "checkins"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    inscricao_id = Column(UUID(as_uuid=True), ForeignKey("inscricoes.id"))
    ingresso_id = Column(UUID(as_uuid=True), ForeignKey("ingressos.id"))
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"))
    ocorrido_em = Column(DateTime, default=datetime.datetime.utcnow)
