"""
shared/helpers/auditoria_helper.py
Service Layer para lógica de auditoria
"""
from sqlalchemy.orm import Session
from app.shared.models.log_auditoria import LogAuditoria
import datetime
from typing import Optional


class AuditoriaService:
    """
    Service Layer para auditoria.
    Single Responsibility: apenas lógica de auditoria.
    """
    
    @staticmethod
    def registrar_log(
        db: Session,
        metodo_http: str,
        caminho: str,
        codigo_status: int,
        ip_cliente: Optional[str] = None,
        usuario_id: Optional[str] = None,
        payload_requisicao: str = "",  # ← ADICIONAR (com default vazio)
        payload_resposta: str = ""     # ← ADICIONAR (com default vazio)
    ) -> LogAuditoria:
        """
        Registra um log de auditoria.
        Responsabilidade única: persistir dados de auditoria.
        """
        # Regra de negócio: limitar tamanho dos payloads
        if len(payload_requisicao) > 5000:
            payload_requisicao = payload_requisicao[:5000] + "... (truncado)"
        
        if len(payload_resposta) > 5000:
            payload_resposta = payload_resposta[:5000] + "... (truncado)"
        
        log = LogAuditoria(
            metodo_http=metodo_http,
            caminho=caminho,
            payload_requisicao=payload_requisicao,
            payload_resposta=payload_resposta,
            codigo_status=codigo_status,
            ip_cliente=ip_cliente,
            usuario_id=usuario_id,
            ocorrido_em=datetime.datetime.utcnow()
        )
        
        db.add(log)
        db.commit()
        db.refresh(log)
        return log