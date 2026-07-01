"""
Rotas de Comentários (com threads aninhadas).
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_async_session
from src.db.models.comentario import Comentario
from src.schemas.comentario import ComentarioCreate, ComentarioRead, ComentarioUpdate
from src.core.deps import get_current_active_user
from src.db.models.usuario import Usuario


router = APIRouter(prefix="/api/denuncias/{denuncia_id}/comentarios", tags=["comentarios"])


@router.get(
    "",
    response_model=List[ComentarioRead],
    summary="Listar comentários de uma denúncia",
)
async def list_comentarios(
    denuncia_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> list[Comentario]:
    result = await session.execute(
        select(Comentario)
        .where(Comentario.denuncia_id == denuncia_id)
        .order_by(Comentario.created_at.asc())
    )
    return list(result.scalars().all())


@router.post(
    "",
    response_model=ComentarioRead,
    status_code=201,
    summary="Comentar em uma denúncia (cidadão autenticado)",
)
async def create_comentario(
    denuncia_id: int,
    dados: ComentarioCreate,
    current_user: Usuario = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> Comentario:
    # Valida parent_id (se for resposta)
    if dados.parent_id:
        parent = await session.get(Comentario, dados.parent_id)
        if not parent or parent.denuncia_id != denuncia_id:
            raise HTTPException(
                status_code=400,
                detail="Comentário pai inválido ou pertence a outra denúncia",
            )

    comentario = Comentario(
        texto=dados.texto,
        parent_id=dados.parent_id,
        autor_id=current_user.id,
        denuncia_id=denuncia_id,
    )
    session.add(comentario)
    await session.commit()
    await session.refresh(comentario)
    return comentario


@router.patch(
    "/{comentario_id}",
    response_model=ComentarioRead,
    summary="Editar comentário (apenas o autor)",
)
async def update_comentario(
    denuncia_id: int,
    comentario_id: int,
    dados: ComentarioUpdate,
    current_user: Usuario = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> Comentario:
    comentario = await session.get(Comentario, comentario_id)
    if not comentario or comentario.denuncia_id != denuncia_id:
        raise HTTPException(status_code=404, detail="Comentário não encontrado")
    if comentario.autor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Apenas o autor pode editar")

    comentario.texto = dados.texto
    comentario.editado = True
    await session.commit()
    await session.refresh(comentario)
    return comentario


@router.delete(
    "/{comentario_id}",
    status_code=204,
    summary="Apagar comentário (autor ou moderador+)",
)
async def delete_comentario(
    denuncia_id: int,
    comentario_id: int,
    current_user: Usuario = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> None:
    comentario = await session.get(Comentario, comentario_id)
    if not comentario or comentario.denuncia_id != denuncia_id:
        raise HTTPException(status_code=404, detail="Comentário não encontrado")

    is_owner = comentario.autor_id == current_user.id
    is_mod = current_user.role.value in ("moderador", "admin")
    if not (is_owner or is_mod):
        raise HTTPException(status_code=403, detail="Sem permissão")

    await session.delete(comentario)
    await session.commit()
