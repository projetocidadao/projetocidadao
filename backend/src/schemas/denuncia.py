"""
Schemas da Denúncia.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from src.models.enums import CategoriaDenuncia, StatusDenuncia


class DenunciaBase(BaseModel):
    titulo: str = Field(..., min_length=5, max_length=200)
    descricao: str = Field(..., min_length=20)
    categoria: CategoriaDenuncia
    anonima: bool = False
    publica: bool = True
    lat: Optional[float] = Field(None, ge=-90, le=90)
    lng: Optional[float] = Field(None, ge=-180, le=180)
    endereco: Optional[str] = Field(None, max_length=500)
    municipio: Optional[str] = Field(None, max_length=100)
    estado: Optional[str] = Field(None, min_length=2, max_length=2)
    cep: Optional[str] = Field(None, min_length=8, max_length=10)
    data_fato: Optional[datetime] = None
    valor_dano_estimado: Optional[float] = Field(None, ge=0)
    envolvidos: Optional[str] = None
    area_id: int


class DenunciaCreate(DenunciaBase):
    pass


class DenunciaUpdate(BaseModel):
    titulo: Optional[str] = Field(None, min_length=5, max_length=200)
    descricao: Optional[str] = Field(None, min_length=20)
    status: Optional[StatusDenuncia] = None
    canal_destino: Optional[str] = Field(None, max_length=100)


class DenunciaRead(DenunciaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: StatusDenuncia
    codigo_rastreio: str
    votos: int
    visualizacoes: int
    autor_id: Optional[int]
    area_id: int
    canal_destino: Optional[str]
    created_at: datetime
    updated_at: datetime


class DenunciaStatusUpdate(BaseModel):
    status: StatusDenuncia
    canal_destino: Optional[str] = Field(None, max_length=100)
