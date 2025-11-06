from sqlalchemy import Column, DateTime, String, ForeignKey, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid, datetime
from app.shared.core.database import Base

class Certificado(Base):
    __tablename__ = "certificados"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    inscricao_id = Column(UUID(as_uuid=True), ForeignKey("inscricoes.id"), nullable=False)
    evento_id = Column(UUID(as_uuid=True), ForeignKey("eventos.id"), nullable=False)
    codigo_certificado = Column(String(100), unique=True, nullable=False)
    emitido_em = Column(DateTime, default=datetime.datetime.utcnow)
    caminho_pdf = Column(String(500), nullable=True)  # caminho/URL do pdf armazenado
    revogado = Column(Boolean, default=False)
