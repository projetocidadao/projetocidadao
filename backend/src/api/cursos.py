"""
Rotas de Cursos (CRUD com autorização).
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_async_session
from src.db.models.curso import Curso
from src.schemas.curso import CursoCreate, CursoRead, CursoUpdate
from src.core.deps import get_current_active_user, require_moderator
from src.db.models.usuario import Usuario


router = APIRouter(prefix="/api/cursos", tags=["cursos"])


@router.get(
    "",
    response_model=List[CursoRead],
    summary="Listar cursos publicados",
)
async def list_cursos(
    area_id: Optional[int] = Query(None, description="Filtrar por área"),
    search: Optional[str] = Query(None, description="Busca textual"),
    session: AsyncSession = Depends(get_async_session),
) -> list[Curso]:
    """Lista cursos publicados. Opcionalmente filtra por área e busca textual."""
    query = select(Curso).where(Curso.status == "publicado")
    if area_id:
        query = query.where(Curso.area_id == area_id)
    if search:
        query = query.where(Curso.titulo.ilike(f"%{search}%"))
    query = query.order_by(Curso.ordem, Curso.titulo)

    result = await session.execute(query)
    return list(result.scalars().all())


@router.get(
    "/{slug}",
    response_model=CursoRead,
    summary="Detalhe de um curso",
)
async def get_curso(
    slug: str,
    session: AsyncSession = Depends(get_async_session),
) -> Curso:
    result = await session.execute(select(Curso).where(Curso.slug == slug))
    curso = result.scalar_one_or_none()
    if not curso:
        raise HTTPException(status_code=404, detail="Curso não encontrado")
    return curso


@router.post(
    "",
    response_model=CursoRead,
    status_code=201,
    summary="Criar novo curso (moderador+)",
)
async def create_curso(
    dados: CursoCreate,
    current_user: Usuario = Depends(require_moderator),
    session: AsyncSession = Depends(get_async_session),
) -> Curso:
    curso = Curso(**dados.model_dump(), autor_id=current_user.id)
    session.add(curso)
    await session.commit()
    await session.refresh(curso)
    return curso


@router.patch(
    "/{curso_id}",
    response_model=CursoRead,
    summary="Atualizar curso (moderador+)",
)
async def update_curso(
    curso_id: int,
    dados: CursoUpdate,
    current_user: Usuario = Depends(require_moderator),
    session: AsyncSession = Depends(get_async_session),
) -> Curso:
    result = await session.execute(select(Curso).where(Curso.id == curso_id))
    curso = result.scalar_one_or_none()
    if not curso:
        raise HTTPException(status_code=404, detail="Curso não encontrado")

    for field, value in dados.model_dump(exclude_unset=True).items():
        setattr(curso, field, value)
    await session.commit()
    await session.refresh(curso)
    return curso


@router.delete(
    "/{curso_id}",
    status_code=204,
    summary="Arquivar curso (moderador+)",
)
async def delete_curso(
    curso_id: int,
    current_user: Usuario = Depends(require_moderator),
    session: AsyncSession = Depends(get_async_session),
) -> None:
    result = await session.execute(select(Curso).where(Curso.id == curso_id))
    curso = result.scalar_one_or_none()
    if not curso:
        raise HTTPException(status_code=404, detail="Curso não encontrado")
    # Soft delete via arquivamento
    curso.status = "arquivado"
    await session.commit()
