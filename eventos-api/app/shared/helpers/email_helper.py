import os
import httpx
from typing import Dict, Any, Literal
import logging

logger = logging.getLogger(__name__)

EMAIL_SERVICE_URL = os.getenv("EMAIL_SERVICE_URL")
EMAIL_API_KEY = os.getenv("EMAIL_API_KEY", "")

TemplateType = Literal["inscricao", "cancelamento", "checkin"]


def enviar_email_sync(
    to: str,
    template: TemplateType,
    data: Dict[str, Any]
) -> bool:
    """
    Versão síncrona do envio de email.
    """
    
    subjects = {
        "inscricao": "Inscrição confirmada",
        "cancelamento": "Inscrição cancelada",
        "checkin": "Presença registrada"
    }
    
    subject = subjects.get(template, "Notificação")
    
    payload = {
        "to": to,
        "subject": subject,
        "template": template,
        "data": data
    }
    
    headers = {
        "x-api-key": EMAIL_API_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        with httpx.Client() as client:
            response = client.post(
                f"{EMAIL_SERVICE_URL}/email/send",
                json=payload,
                headers=headers,
                timeout=10.0
            )
            
            if response.status_code == 200:
                logger.info(f"Email enviado com sucesso para {to} (template: {template})")
                return True
            else:
                logger.error(
                    f"Falha ao enviar email para {to}. "
                    f"Status: {response.status_code}, "
                    f"Response: {response.text}"
                )
                return False
                
    except httpx.TimeoutException:
        logger.error(f"Timeout ao enviar email para {to}")
        return False
    except Exception as e:
        logger.error(f"Erro ao enviar email para {to}: {str(e)}")
        return False