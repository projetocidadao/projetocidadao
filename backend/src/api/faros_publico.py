"""Endpoint publico do Farejador - faros verificados visiveis para todos."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime

from src.db.session import get_async_session
from src.db.models.faro import Faro
from src.db.models.enums import StatusFaro
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class FaroPublico(BaseModel):
    id: int
    tipo_entidade: str
    referencia_id: str
    entidade_nome: str | None = None
    status: str
    score_risco: int
    severidade: str
    data_deteccao: datetime
    desfecho: str | None = None
    heuristicas: list = []

    class Config:
        from_attributes = True


STATUS_PUBLICOS = [
    StatusFaro.EM_ANALISE,
    StatusFaro.CONFIRMADO,
    StatusFaro.INVESTIGADO,
    StatusFaro.ARQUIVADO,
]

router = APIRouter(prefix="/api/faros/publico", tags=["farejador-publico"])


@router.get(
    "",
    response_model=List[FaroPublico],
    summary="Faros verificados (publico)",
)
async def list_faros_publico(
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_async_session),
):
    """Lista faros com status >= em_analise. Faros 'novo' nao sao exibidos publicamente."""
    query = select(Faro).where(Faro.status.in_(STATUS_PUBLICOS))
    if status:
        try:
            s = StatusFaro(status)
            if s not in STATUS_PUBLICOS:
                raise HTTPException(400, "Status nao disponivel publicamente")
            query = query.where(Faro.status == s)
        except ValueError:
            raise HTTPException(400, "Status invalido")
    query = query.order_by(Faro.score_risco.desc(), Faro.data_deteccao.desc())
    query = query.offset(skip).limit(limit)
    result = await session.execute(query)
    return list(result.scalars().all())
