"""
Schemas Pydantic para o endpoint /api/stats (estatisticas publicas) - v2.0.
Adiciona: por_estado, top_municipios, top_usuarios, stats_farejos, engajamento.
"""
from datetime import datetime
from typing import List
from pydantic import BaseModel, Field


class StatsGerais(BaseModel):
    total_denuncias: int
    denuncias_publicas: int
    denuncias_anonimas: int
    denuncias_aguardando: int
    denuncias_em_analise: int
    denuncias_resolvidas: int
    denuncias_retiradas: int
    denuncias_canceladas_coacao: int
    pedidos_retirada_pendentes: int
    areas_ativas: int
    usuarios_cadastrados: int


class StatsPorMes(BaseModel):
    mes: str
    total: int
    publicas: int
    anonimas: int


class StatsPorArea(BaseModel):
    area_id: int
    area_nome: str
    area_slug: str
    total: int
    percentual: float


class StatsPorCategoria(BaseModel):
    categoria: str
    total: int
    percentual: float


# ----- NOVOS v2.0 -----

class StatsPorEstado(BaseModel):
    estado: str = Field(..., description="UF (sigla de 2 letras)")
    total: int
    percentual: float


class StatsTopMunicipio(BaseModel):
    municipio: str
    estado: str
    total: int


class StatsTopUsuario(BaseModel):
    usuario_id: int
    nome: str
    total_denuncias: int
    total_comentarios: int = 0
    pontos_cidadania: int = 0


class StatsFarejos(BaseModel):
    total_faros: int
    faros_ativos: int
    faros_em_analise: int
    faros_investigados: int
    por_heuristica: List[StatsPorCategoria]


class StatsEngajamento(BaseModel):
    denuncias_com_comentarios: int
    denuncias_com_votos: int
    total_comentarios: int
    total_votos: int
    total_visualizacoes: int
    media_comentarios_por_denuncia: float
    media_visualizacoes_por_denuncia: float


class StatsRead(BaseModel):
    geral: StatsGerais
    por_mes: List[StatsPorMes]
    por_area: List[StatsPorArea]
    por_categoria: List[StatsPorCategoria]
    # Novos
    por_estado: List[StatsPorEstado]
    top_municipios: List[StatsTopMunicipio]
    top_usuarios: List[StatsTopUsuario]
    farejos: StatsFarejos
    engajamento: StatsEngajamento
    ultima_atualizacao: datetime
