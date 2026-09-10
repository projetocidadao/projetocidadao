"""
Rotas de Progresso de Curso.

Permite que usuários autenticados registrem e consultem seu progresso
nos cursos. Atende ao Princípio 5 (Sabedoria) do MAPA_PRINCIPIOS.md.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_async_session
from src.db.models.progresso import Progresso
from src.db.models.curso import Curso
from src.db.models.usuario import Usuario
from src.schemas.progresso import (
    ProgressoRead,
    ProgressoUpdate,
    ProgressoComCursoRead,
    ProgressoResumoRead,
)
from src.core.deps import get_current_active_user


router = APIRouter(prefix="/api", tags=["progresso"])


@router.get(
    "/cursos/{slug}/progresso",
    response_model=ProgressoRead,
    summary="Consultar progresso do usuário em um curso",
)
async def get_progresso_curso(
    slug: str,
    current_user: Usuario = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> Progresso:
    """Retorna o progresso do usuário autenticado no curso identificado por slug."""
    result = await session.execute(
        select(Curso).where(Curso.slug == slug)
    )
    curso = result.scalar_one_or_none()
    if not curso:
        raise HTTPException(status_code=404, detail="Curso não encontrado")

    result = await session.execute(
        select(Progresso).where(
            Progresso.usuario_id == current_user.id,
            Progresso.curso_id == curso.id,
        )
    )
    progresso = result.scalar_one_or_none()
    if not progresso:
        # Retorna progresso zero padrão se não existir ainda
        return Progresso(
            id=0,
            usuario_id=current_user.id,
            curso_id=curso.id,
            percentual=0.0,
            concluido=False,
            created_at=None,
            updated_at=None,
        )
    return progresso


@router.put(
    "/cursos/{slug}/progresso",
    response_model=ProgressoRead,
    summary="Atualizar progresso do usuário em um curso",
)
async def update_progresso_curso(
    slug: str,
    dados: ProgressoUpdate,
    current_user: Usuario = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> Progresso:
    """Cria ou atualiza o progresso do usuário autenticado no curso.

    - Se percentual >= 100, marca como concluido=True automaticamente.
    - Se percentual < 100 e concluido era True, desmarca.
    """
    result = await session.execute(
        select(Curso).where(Curso.slug == slug)
    )
    curso = result.scalar_one_or_none()
    if not curso:
        raise HTTPException(status_code=404, detail="Curso não encontrado")

    result = await session.execute(
        select(Progresso).where(
            Progresso.usuario_id == current_user.id,
            Progresso.curso_id == curso.id,
        )
    )
    progresso = result.scalar_one_or_none()

    concluido = dados.percentual >= 100.0

    if progresso:
        progresso.percentual = dados.percentual
        progresso.concluido = concluido
    else:
        progresso = Progresso(
            usuario_id=current_user.id,
            curso_id=curso.id,
            percentual=dados.percentual,
            concluido=concluido,
        )
        session.add(progresso)

    await session.commit()
    await session.refresh(progresso)
    return progresso


@router.get(
    "/usuarios/me/progresso",
    response_model=List[ProgressoComCursoRead],
    summary="Listar progresso do usuário em todos os cursos",
)
async def list_meu_progresso(
    current_user: Usuario = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> list[dict]:
    """Lista o progresso do usuário autenticado em todos os cursos iniciados."""
    result = await session.execute(
        select(
            Progresso,
            Curso.titulo.label("curso_titulo"),
            Curso.slug.label("curso_slug"),
            Curso.nivel.label("curso_nivel"),
            Curso.duracao_minutos.label("curso_duracao_minutos"),
            Curso.total_modulos.label("curso_total_modulos"),
            Curso.area_id.label("area_id"),
        )
        .join(Curso, Progresso.curso_id == Curso.id)
        .where(Progresso.usuario_id == current_user.id)
        .order_by(Progresso.updated_at.desc())
    )
    rows = result.all()
    return [
        {
            "id": p.id,
            "usuario_id": p.usuario_id,
            "curso_id": p.curso_id,
            "percentual": p.percentual,
            "concluido": p.concluido,
            "created_at": p.created_at,
            "updated_at": p.updated_at,
            "curso_titulo": curso_titulo,
            "curso_slug": curso_slug,
            "curso_nivel": curso_nivel,
            "curso_duracao_minutos": curso_duracao_minutos,
            "curso_total_modulos": curso_total_modulos,
            "area_id": area_id,
        }
        for p, curso_titulo, curso_slug, curso_nivel, curso_duracao_minutos, curso_total_modulos, area_id in rows
    ]


@router.get(
    "/usuarios/me/progresso/resumo",
    response_model=ProgressoResumoRead,
    summary="Resumo de progresso do usuário",
)
async def resumo_meu_progresso(
    current_user: Usuario = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    """Retorna estatísticas consolidadas do progresso do usuário."""
    result = await session.execute(
        select(
            func.count(Progresso.id).label("total_iniciados"),
            func.count(Progresso.id).filter(Progresso.concluido == True).label("total_concluidos"),
            func.count(Progresso.id).filter(Progresso.concluido == False).label("total_andamento"),
            func.avg(Progresso.percentual).label("percentual_medio"),
        ).where(Progresso.usuario_id == current_user.id)
    )
    row = result.one()

    # Estimativa de minutos estudados: soma de (percentual/100 * duracao_minutos) dos cursos iniciados
    result_min = await session.execute(
        select(
            func.coalesce(func.sum(Progresso.percentual / 100.0 * Curso.duracao_minutos), 0)
        )
        .join(Curso, Progresso.curso_id == Curso.id)
        .where(Progresso.usuario_id == current_user.id)
    )
    minutos_estudados = int(result_min.scalar() or 0)

    return {
        "total_cursos_iniciados": row.total_iniciados or 0,
        "total_cursos_concluidos": row.total_concluidos or 0,
        "total_cursos_em_andamento": row.total_andamento or 0,
        "percentual_medio": round(float(row.percentual_medio or 0), 2),
        "minutos_estudados_estimados": minutos_estudados,
    }
