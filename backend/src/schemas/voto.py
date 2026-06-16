"""
Schemas do Voto.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class VotoBase(BaseModel):
    apoio: bool = True  # True = apoio / False = contra
    pontos: int = Field(default=1, ge=0, le=10, description="Peso do voto (1-10)")


class VotoCreate(VotoBase):
    """Para criar/atualizar um voto."""
    denuncia_id: int


class VotoUpdate(BaseModel):
    """Para trocar apoio/contra ou ajustar peso."""
    apoio: Optional[bool] = None
    pontos: Optional[int] = Field(None, ge=0, le=10)


class VotoRead(VotoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int
    denuncia_id: int
    created_at: datetime
    updated_at: datetime


class RankingItem(BaseModel):
    """Item do ranking de denúncias."""
    model_config = ConfigDict(from_attributes=True)

    denuncia_id: int
    titulo: str
    categoria: str
    codigo_rastreio: str
    score_apoio: int
    score_contra: int
    score_total: int
    total_votos: int
    visualizacoes: int
    municipio: Optional[str] = None
    estado: Optional[str] = None


class VotoStats(BaseModel):
    """Estatísticas agregadas de uma denúncia."""
    denuncia_id: int
    apoio: int
    contra: int
    total: int
    score: int  # apoio - contra
    pontuacao_total: int  # soma dos pesos
    votaram: list[int]  # ids de quem votou (apenas para mod)
