"""
Rotas do Farejador de Corrupção — listagem e atualização de 'faros' (sinais detectados).
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_async_session
from src.db.models.faro import Faro
from src.db.models.enums import StatusFaro
from src.schemas.faro import FaroCreate, FaroRead, FaroUpdate
from src.core.deps import require_moderator, require_admin
from src.db.models.usuario import Usuario


router = APIRouter(prefix="/api/faros", tags=["farejador"])


@router.get(
    "",
    response_model=List[FaroRead],
    summary="Listar sinais detectados (moderador+)",
)
async def list_faros(
    status: Optional[StatusFaro] = Query(None),
    severidade: Optional[str] = Query(None, pattern=r"^(BAIXA|MEDIA|ALTA|CRITICA)$"),
    tipo_entidade: Optional[str] = Query(None),
    min_score: Optional[int] = Query(None, ge=0, le=100),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: Usuario = Depends(require_moderator),
    session: AsyncSession = Depends(get_async_session),
) -> list[Faro]:
    """Lista sinais do farejador. Acesso restrito a moderadores."""
    query = select(Faro)
    if status:
        query = query.where(Faro.status == status)
    if severidade:
        query = query.where(Faro.severidade == severidade)
    if tipo_entidade:
        query = query.where(Faro.tipo_entidade == tipo_entidade)
    if min_score is not None:
        query = query.where(Faro.score_risco >= min_score)

    query = query.order_by(Faro.score_risco.desc(), Faro.data_deteccao.desc())
    query = query.offset(skip).limit(limit)
    result = await session.execute(query)
    return list(result.scalars().all())


@router.post(
    "",
    response_model=FaroRead,
    status_code=201,
    summary="Registrar nova detecção (sistema ou admin)",
)
async def create_faro(
    dados: FaroCreate,
    current_user: Usuario = Depends(require_admin),
    session: AsyncSession = Depends(get_async_session),
) -> Faro:
    """Cria um registro de sinal. Em produção, este endpoint é chamado pelos workers do farejador."""
    faro = Faro(**dados.model_dump())
    session.add(faro)
    await session.commit()
    await session.refresh(faro)
    return faro


@router.patch(
    "/{faro_id}",
    response_model=FaroRead,
    summary="Atualizar status/desfecho (moderador+)",
)
async def update_faro(
    faro_id: int,
    dados: FaroUpdate,
    current_user: Usuario = Depends(require_moderator),
    session: AsyncSession = Depends(get_async_session),
) -> Faro:
    faro = await session.get(Faro, faro_id)
    if not faro:
        raise HTTPException(status_code=404, detail="Faro não encontrado")

    update_data = dados.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(faro, field, value)

    # Se mudou de NOVO para EM_ANALISE, registra data de investigação
    if dados.status == StatusFaro.EM_ANALISE and not faro.data_investigacao:
        from datetime import datetime, timezone
        faro.data_investigacao = datetime.now(timezone.utc)

    await session.commit()
    await session.refresh(faro)
    return faro


@router.get(
    "/stats",
    summary="Estatísticas agregadas do farejador (moderador+)",
)
async def faro_stats(
    current_user: Usuario = Depends(require_moderator),
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    """Retorna contadores por status, severidade e tipo."""
    from sqlalchemy import func

    # Total por status
    status_count = {}
    result = await session.execute(
        select(Faro.status, func.count(Faro.id)).group_by(Faro.status)
    )
    for s, count in result.all():
        status_count[s.value] = count

    # Total por severidade
    sev_count = {}
    result = await session.execute(
        select(Faro.severidade, func.count(Faro.id)).group_by(Faro.severidade)
    )
    for s, count in result.all():
        sev_count[s] = count

    # Top scores
    result = await session.execute(
        select(Faro)
        .order_by(Faro.score_risco.desc())
        .limit(10)
    )
    top_risco = [FaroRead.model_validate(f) for f in result.scalars().all()]

    return {
        "por_status": status_count,
        "por_severidade": sev_count,
        "top_risco": top_risco,
    }
