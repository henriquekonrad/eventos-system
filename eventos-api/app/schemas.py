# app/schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# ---------- Usuarios ----------
class UsuarioCreate(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    cpf: Optional[str] = None

class UsuarioOut(BaseModel):
    id: str
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
    id: str
    titulo: str
    descricao: Optional[str] = None
    inicio_em: Optional[datetime] = None
    fim_em: Optional[datetime] = None

    class Config:
        orm_mode = True

# ---------- Inscricao ----------
class InscricaoCreateRapida(BaseModel):
    evento_id: str
    nome_rapido: str
    cpf_rapido: Optional[str] = None
    email_rapido: Optional[EmailStr] = None

class InscricaoOut(BaseModel):
    id: str
    evento_id: str
    usuario_id: Optional[str] = None
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
    inscricao_id: str
    ingresso_id: str
    usuario_id: str  # pela model esse campo é non-null

class CheckinOut(BaseModel):
    id: str
    inscricao_id: str
    ingresso_id: str
    usuario_id: str
    ocorrido_em: Optional[datetime]

    class Config:
        orm_mode = True

# ---------- Certificado ----------
class CertificadoCreate(BaseModel):
    inscricao_id: str
    evento_id: str

class CertificadoOut(BaseModel):
    id: str
    inscricao_id: str
    evento_id: str
    codigo_certificado: str
    emitido_em: Optional[datetime]
    caminho_pdf: Optional[str]
    revogado: Optional[bool]

    class Config:
        orm_mode = True
