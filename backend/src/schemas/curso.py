"""
Schemas do Curso.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class CursoBase(BaseModel):
    slug: str = Field(..., min_length=2, max_length=120)
    titulo: str = Field(..., min_length=3, max_length=200)
    descricao: str = Field(..., min_length=10, max_length=1000)
    conteudo: str = Field(..., min_length=10)  # markdown
    duracao_minutos: int = Field(default=60, ge=1, le=6000)
    nivel: str = Field(default="iniciante")
    publico_alvo: Optional[str] = Field(None, max_length=500)
    area_id: int


class CursoCreate(CursoBase):
    status: str = Field(default="rascunho", pattern=r"^(rascunho|em_aprovacao|publicado|arquivado)$")


class CursoUpdate(BaseModel):
    titulo: Optional[str] = Field(None, min_length=3, max_length=200)
    descricao: Optional[str] = Field(None, min_length=10, max_length=1000)
    conteudo: Optional[str] = None
    duracao_minutos: Optional[int] = Field(None, ge=1, le=6000)
    nivel: Optional[str] = None
    publico_alvo: Optional[str] = Field(None, max_length=500)
    status: Optional[str] = Field(None, pattern=r"^(rascunho|em_aprovacao|publicado|arquivado)$")
    ordem: Optional[int] = None
    total_modulos: Optional[int] = None


class CursoRead(CursoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    autor_id: Optional[int]
    total_modulos: int
    ordem: int
    created_at: datetime
    updated_at: datetime
