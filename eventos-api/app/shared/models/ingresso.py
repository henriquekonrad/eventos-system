from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
import datetime
from app.shared.core.database import Base


class Ingresso(Base):
    __tablename__ = "ingressos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    inscricao_id = Column(UUID(as_uuid=True), ForeignKey("inscricoes.id"), nullable=False)
    evento_id = Column(UUID(as_uuid=True), ForeignKey("eventos.id"), nullable=False)

    codigo_ingresso = Column(String(100), unique=True, nullable=False)
    token_qr = Column(String(500), unique=True, nullable=True)
    status = Column(String(50), default="emitido")

    emitido_em = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
