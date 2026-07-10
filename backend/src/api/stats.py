"""
Endpoint publico de estatisticas agregadas - v2.0.
GET /api/stats
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_async_session
from src.schemas.stats import StatsRead
from src.services.stats import estatisticas_completas


router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get(
    "",
    response_model=StatsRead,
    summary="Estatisticas publicas agregadas (v2.0)",
    description=(
        "Retorna contadores e agregacoes publicas do sistema: contadores gerais, "
        "distribuicao por mes, por area, por categoria, por estado/UF, "
        "top municipios, top cidadaos, saude do farejador e engajamento. "
        "Nenhum dado pessoal e exposto."
    ),
)
async def get_stats(
    session: AsyncSession = Depends(get_async_session),
) -> StatsRead:
    return await estatisticas_completas(session)
