"""
Schemas do Faro (Farejador de Corrupção).
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field

from src.db.models.enums import StatusFaro


class FaroBase(BaseModel):
    tipo_entidade: str = Field(..., max_length=30)
    referencia_id: str = Field(..., max_length=100)
    entidade_nome: Optional[str] = Field(None, max_length=255)
    heuristicas: List[str] = Field(default_factory=list)
    evidencia: Dict[str, Any] = Field(default_factory=dict)
    score_risco: int = Field(default=0, ge=0, le=100)
    severidade: str = Field(default="MEDIA", pattern=r"^(BAIXA|MEDIA|ALTA|CRITICA)$")
    denuncia_id: Optional[int] = None


class FaroCreate(FaroBase):
    pass


class FaroUpdate(BaseModel):
    status: Optional[StatusFaro] = None
    desfecho: Optional[str] = None
    severidade: Optional[str] = Field(None, pattern=r"^(BAIXA|MEDIA|ALTA|CRITICA)$")
    score_risco: Optional[int] = Field(None, ge=0, le=100)


class FaroRead(FaroBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: StatusFaro
    data_deteccao: datetime
    data_investigacao: Optional[datetime]
    desfecho: Optional[str]
    created_at: datetime
    updated_at: datetime
