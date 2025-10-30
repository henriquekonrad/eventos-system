# app/models/log_auditoria.py
from sqlalchemy import Column, String, DateTime, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid
import datetime
from app.core.database import Base

class LogAuditoria(Base):
    __tablename__ = "logs_auditoria"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    metodo_http = Column(String(10))
    caminho = Column(String(500))
    payload_requisicao = Column(Text)
    payload_resposta = Column(Text)
    codigo_status = Column(Integer)
    ip_cliente = Column(String(100))
    usuario_id = Column(UUID(as_uuid=True), nullable=True)
    ocorrido_em = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
