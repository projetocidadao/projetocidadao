"""
Schemas da Area.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class AreaBase(BaseModel):
    slug: str = Field(..., min_length=2, max_length=80)
    nome: str = Field(..., min_length=2, max_length=150)
    descricao: str = Field(..., min_length=10, max_length=1000)
    icone: str = Field(..., min_length=1, max_length=50)
    cor: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    artigo_cf: Optional[str] = Field(None, max_length=50)
    ordem: int = 0


class AreaCreate(AreaBase):
    pass


class AreaUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=2, max_length=150)
    descricao: Optional[str] = Field(None, min_length=10, max_length=1000)
    icone: Optional[str] = Field(None, min_length=1, max_length=50)
    cor: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    artigo_cf: Optional[str] = Field(None, max_length=50)
    ordem: Optional[int] = None
    ativo: Optional[bool] = None


class AreaRead(AreaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ativo: bool
    created_at: datetime
    updated_at: datetime
