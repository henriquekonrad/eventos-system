from sqlalchemy import Column, DateTime, String, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
import uuid, datetime
from app.core.database import Base

class Inscricao(Base):
    __tablename__ = "inscricoes"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    evento_id = Column(UUID(as_uuid=True), ForeignKey("eventos.id"), nullable=False)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    inscricao_rapida = Column(Boolean)
    nome_rapido = Column(String(200), nullable=False)
    cpf_rapido = Column(String(20))
    email_rapido = Column(String(255))
    status = Column(String(50), default="confirmada")  # ou "cancelada"
    cancelado_em = Column(DateTime, default=datetime.datetime.utcnow)
    sincronizado = Column(Boolean)
