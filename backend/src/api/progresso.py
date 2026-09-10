"""
Rotas de Progresso de Curso.

Permite que usuários logados registrem e acompanhem seu progresso nos cursos.

Endpoints:
- GET    /api/progresso/meus                  → lista progresso do usuário logado
- GET    /api/cursos/{curso_id}/progresso      → progresso do usuário num curso específico
- POST   /api/cursos/{curso_id}/progresso      → cria ou atualiza progresso (upsert)
- GET    /api/cursos/{curso_id}/progresso/stats → stats agregadas (moderador+)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_async_session
from src.db.models.curso import Curso
from src.db.models.progresso import Progresso
from src.db.models.usuario import Usuario
from src.schemas.progresso import ProgressoRead, ProgressoStats, ProgressoUpsert
from src.core.deps import get_current_active_user, require_moderator


router = APIRouter(prefix="/api", tags=["progresso"])


@router.get(
    "/progresso/meus",
    response_model=list[ProgressoRead],
    summary="Listar meu progresso em todos os cursos",
)
async def listar_meu_progresso(
    current_user: Usuario = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> list[Progresso]:
    """Retorna o progresso do usuário logado em todos os cursos que iniciou."""
    result = await session.execute(
        select(Progresso)
        .where(Progresso.usuario_id == current_user.id)
        .order_by(Progresso.updated_at.desc())
    )
    return list(result.scalars().all())


@router.get(
    "/cursos/{curso_id}/progresso",
    response_model=ProgressoRead,
    summary="Ver meu progresso num curso específico",
)
async def ver_progresso_curso(
    curso_id: int,
    current_user: Usuario = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> Progresso:
    """Retorna o progresso do usuário logado num curso específico."""
    curso = await session.get(Curso, curso_id)
    if not curso:
        raise HTTPException(status_code=404, detail="Curso não encontrado")

    result = await session.execute(
        select(Progresso).where(
            Progresso.usuario_id == current_user.id,
            Progresso.curso_id == curso_id,
        )
    )
    progresso = result.scalar_one_or_none()
    if not progresso:
        return Progresso(
            usuario_id=current_user.id,
            curso_id=curso_id,
            percentual=0.0,
            concluido=False,
        )
    return progresso


@router.post(
    "/cursos/{curso_id}/progresso",
    response_model=ProgressoRead,
    summary="Registrar ou atualizar progresso num curso",
)
async def upsert_progresso(
    curso_id: int,
    dados: ProgressoUpsert,
    current_user: Usuario = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> Progresso:
    """Cria ou atualiza o progresso do usuário logado num curso (upsert)."""
    curso = await session.get(Curso, curso_id)
    if not curso:
        raise HTTPException(status_code=404, detail="Curso não encontrado")

    result = await session.execute(
        select(Progresso).where(
            Progresso.usuario_id == current_user.id,
            Progresso.curso_id == curso_id,
        )
    )
    progresso = result.scalar_one_or_none()

    if progresso is None:
        progresso = Progresso(
            usuario_id=current_user.id,
            curso_id=curso_id,
            percentual=dados.percentual,
            concluido=dados.concluido,
        )
        session.add(progresso)
    else:
        progresso.percentual = dados.percentual
        progresso.concluido = dados.concluido

    await session.commit()
    await session.refresh(progresso)
    return progresso


@router.get(
    "/cursos/{curso_id}/progresso/stats",
    response_model=ProgressoStats,
    summary="Estatísticas agregadas de progresso (moderador+)",
)
async def stats_progresso_curso(
    curso_id: int,
    current_user: Usuario = Depends(require_moderator),
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    """Retorna estatísticas agregadas de progresso para um curso."""
    curso = await session.get(Curso, curso_id)
    if not curso:
        raise HTTPException(status_code=404, detail="Curso não encontrado")

    result = await session.execute(
        select(
            func.count(Progresso.id).label("total_matriculas"),
            func.count(Progresso.id).filter(Progresso.concluido.is_(True)).label("total_concluidos"),
            func.avg(Progresso.percentual).label("percentual_medio"),
        ).where(Progresso.curso_id == curso_id)
    )
    row = result.one()

    total_matriculas = int(row.total_matriculas or 0)
    total_concluidos = int(row.total_concluidos or 0)
    percentual_medio = float(row.percentual_medio or 0.0)
    taxa_conclusao = (total_concluidos / total_matriculas * 100.0) if total_matriculas > 0 else 0.0

    return {
        "curso_id": curso_id,
        "total_matriculas": total_matriculas,
        "total_concluidos": total_concluidos,
        "taxa_conclusao": round(taxa_conclusao, 2),
        "percentual_medio": round(percentual_medio, 2),
    }
