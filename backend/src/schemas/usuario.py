"""
Schemas do Usuário.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.models.enums import UserRole


class UsuarioBase(BaseModel):
    email: EmailStr
    nome: str = Field(..., min_length=2, max_length=150)
    bio: Optional[str] = Field(None, max_length=500)
    cidade: Optional[str] = Field(None, max_length=100)
    estado: Optional[str] = Field(None, min_length=2, max_length=2)


class UsuarioCreate(UsuarioBase):
    senha: str = Field(..., min_length=8, max_length=128)


class UsuarioUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=2, max_length=150)
    bio: Optional[str] = Field(None, max_length=500)
    cidade: Optional[str] = Field(None, max_length=100)
    estado: Optional[str] = Field(None, min_length=2, max_length=2)
    avatar_url: Optional[str] = None


class UsuarioLogin(BaseModel):
    email: EmailStr
    senha: str


class UsuarioRead(UsuarioBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: UserRole
    pontos: int
    nivel: int
    avatar_url: Optional[str]
    ativo: bool
    verificado: bool
    created_at: datetime
    updated_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # em segundos
    usuario: UsuarioRead


class TokenPayload(BaseModel):
    sub: str  # user id (string)
    exp: int
    iat: int
    role: str
