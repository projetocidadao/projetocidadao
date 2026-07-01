"""
Rotas de Áreas Temáticas (públicas para leitura).
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_async_session
from src.db.models.area import Area
from src.schemas.area import AreaRead
from src.core.deps import get_current_active_user
from src.db.models.usuario import Usuario


router = APIRouter(prefix="/api/areas", tags=["areas"])


@router.get(
    "",
    response_model=List[AreaRead],
    summary="Listar todas as áreas ativas",
)
async def list_areas(
    session: AsyncSession = Depends(get_async_session),
) -> list[Area]:
    """Lista todas as áreas temáticas ativas, ordenadas."""
    result = await session.execute(
        select(Area).where(Area.ativo == True).order_by(Area.ordem, Area.nome)
    )
    return list(result.scalars().all())


@router.get(
    "/{slug}",
    response_model=AreaRead,
    summary="Detalhe de uma área por slug",
)
async def get_area(
    slug: str,
    session: AsyncSession = Depends(get_async_session),
) -> Area:
    result = await session.execute(select(Area).where(Area.slug == slug, Area.ativo == True))
    area = result.scalar_one_or_none()
    if not area:
        raise HTTPException(status_code=404, detail="Área não encontrada")
    return area
