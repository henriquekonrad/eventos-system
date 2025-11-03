from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID

# ---------- Usuarios ----------
class UsuarioCreate(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    cpf: Optional[str] = None

class UsuarioOut(BaseModel):
    id: UUID
    nome: str
    email: EmailStr
    cpf: Optional[str] = None
    email_verificado: Optional[bool] = False
    papel: Optional[str] = None
    criado_em: Optional[datetime] = None
    atualizado_em: Optional[datetime] = None

    class Config:
        orm_mode = True

# ---------- Evento ----------
class EventoCreate(BaseModel):
    titulo: str
    descricao: Optional[str] = None
    inicio_em: Optional[datetime] = None
    fim_em: Optional[datetime] = None

class EventoOut(BaseModel):
    id: UUID
    titulo: str
    descricao: Optional[str] = None
    inicio_em: Optional[datetime] = None
    fim_em: Optional[datetime] = None

    class Config:
        orm_mode = True

# ---------- Inscricao ----------
class InscricaoCreateRapida(BaseModel):
    evento_id: UUID
    nome_rapido: str
    cpf_rapido: Optional[str] = None
    email_rapido: Optional[EmailStr] = None

class InscricaoOut(BaseModel):
    id: UUID
    evento_id: UUID
    usuario_id: Optional[UUID] = None
    inscricao_rapida: Optional[bool] = None
    nome_rapido: Optional[str] = None
    cpf_rapido: Optional[str] = None
    email_rapido: Optional[EmailStr] = None
    status: Optional[str] = None
    cancelado_em: Optional[datetime] = None
    sincronizado: Optional[bool] = None

    class Config:
        orm_mode = True

# ---------- Checkin ----------
class CheckinCreate(BaseModel):
    inscricao_id: UUID
    ingresso_id: UUID
    usuario_id: UUID

class CheckinOut(BaseModel):
    id: UUID
    inscricao_id: UUID
    ingresso_id: UUID
    usuario_id: UUID
    ocorrido_em: Optional[datetime]

    class Config:
        orm_mode = True

# ---------- Certificado ----------
class CertificadoCreate(BaseModel):
    inscricao_id: UUID
    evento_id: UUID

class CertificadoOut(BaseModel):
    id: UUID
    inscricao_id: UUID
    evento_id: UUID
    codigo_certificado: str
    emitido_em: Optional[datetime]
    caminho_pdf: Optional[str]
    revogado: Optional[bool]

    class Config:
        orm_mode = True

# ------------ Ingresso --------------
class IngressoSchema(BaseModel):
    id: UUID
    inscricao_id: UUID
    evento_id: UUID
    codigo_ingresso: str
    token_qr: str
    status: str
    emitido_em: datetime

    class Config:
        orm_mode = True

# ------------ Token --------------
class Token(BaseModel):
    access_token: str
    token_type: str

class LoginIn(BaseModel):
    email: str
    senha: str
