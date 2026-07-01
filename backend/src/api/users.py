"""
Rotas de usuários: perfil, atualização.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_async_session
from src.db.models.usuario import Usuario
from src.schemas.usuario import UsuarioRead, UsuarioUpdate
from src.core.deps import get_current_active_user


router = APIRouter(prefix="/api/users", tags=["users"])


@router.get(
    "/me",
    response_model=UsuarioRead,
    summary="Perfil do usuário autenticado",
)
async def get_me(
    current_user: Usuario = Depends(get_current_active_user),
) -> Usuario:
    return current_user


@router.patch(
    "/me",
    response_model=UsuarioRead,
    summary="Atualizar perfil do usuário autenticado",
)
async def update_me(
    dados: UsuarioUpdate,
    current_user: Usuario = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> Usuario:
    """Atualiza apenas os campos enviados."""
    update_data = dados.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)
    await session.commit()
    await session.refresh(current_user)
    return current_user


@router.get(
    "/{user_id}",
    response_model=UsuarioRead,
    summary="Perfil público de um usuário",
)
async def get_user(
    user_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> Usuario:
    result = await session.execute(select(Usuario).where(Usuario.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user
