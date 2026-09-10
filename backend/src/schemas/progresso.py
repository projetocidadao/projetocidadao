"""
Schemas de Progresso de Curso.
"""
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ProgressoBase(BaseModel):
    percentual: float = Field(default=0.0, ge=0.0, le=100.0)
    concluido: bool = False


class ProgressoUpsert(ProgressoBase):
    pass


class ProgressoRead(ProgressoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int
    curso_id: int
    created_at: datetime
    updated_at: datetime


class ProgressoStats(BaseModel):
    """Estatísticas agregadas de progresso (para moderadores)."""
    curso_id: int
    total_matriculas: int
    total_concluidos: int
    taxa_conclusao: float
    percentual_medio: float
