"""
Schemas do Comentário.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ComentarioBase(BaseModel):
    texto: str = Field(..., min_length=1, max_length=5000)
    parent_id: Optional[int] = None


class ComentarioCreate(ComentarioBase):
    denuncia_id: int


class ComentarioUpdate(BaseModel):
    texto: str = Field(..., min_length=1, max_length=5000)


class ComentarioRead(ComentarioBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    editado: bool
    autor_id: int
    denuncia_id: int
    created_at: datetime
    updated_at: datetime
