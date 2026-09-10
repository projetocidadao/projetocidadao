"""
Schemas de Progresso de Curso.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ProgressoBase(BaseModel):
    percentual: float = Field(default=0.0, ge=0.0, le=100.0)


class ProgressoUpdate(ProgressoBase):
    """Payload para atualizar percentual de um curso."""
    pass


class ProgressoRead(ProgressoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int
    curso_id: int
    concluido: bool
    created_at: datetime
    updated_at: datetime


class ProgressoComCursoRead(BaseModel):
    """Progresso do usuário com dados do curso associado."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int
    curso_id: int
    percentual: float
    concluido: bool
    created_at: datetime
    updated_at: datetime
    curso_titulo: str
    curso_slug: str
    curso_nivel: str
    curso_duracao_minutos: int
    curso_total_modulos: int
    area_id: int


class ProgressoResumoRead(BaseModel):
    """Resumo de progresso do usuário."""
    total_cursos_iniciados: int
    total_cursos_concluidos: int
    total_cursos_em_andamento: int
    percentual_medio: float
    minutos_estudados_estimados: int
