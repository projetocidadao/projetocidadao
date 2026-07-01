"""
Dependências de autenticação e autorização.
"""
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_async_session
from src.db.models.usuario import Usuario, UserRole
from src.core.security import decodificar_token


# TokenUrl = endpoint que recebe form-data (login)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_async_session),
) -> Usuario:
    """
    Decodifica o token JWT e retorna o usuário correspondente.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decodificar_token(token)
        user_id_str: Optional[str] = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        user_id = int(user_id_str)
    except (JWTError, ValueError):
        raise credentials_exception

    result = await session.execute(select(Usuario).where(Usuario.id == user_id))
    user = result.scalar_one_or_none()

    if user is None or not user.ativo:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: Usuario = Depends(get_current_user),
) -> Usuario:
    """Garante que o usuário está ativo."""
    if not current_user.ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo",
        )
    return current_user


def require_role(*allowed_roles: UserRole):
    """
    Factory de dependência que exige um papel específico.
    Uso: current_user: Usuario = Depends(require_role(UserRole.MODERADOR, UserRole.ADMIN))
    """
    async def role_checker(
        current_user: Usuario = Depends(get_current_active_user),
    ) -> Usuario:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso restrito a: {', '.join(r.value for r in allowed_roles)}",
            )
        return current_user
    return role_checker


# Atalhos prontos
require_admin = require_role(UserRole.ADMIN)
require_moderator = require_role(UserRole.MODERADOR, UserRole.ADMIN)
require_avancado = require_role(UserRole.AVANCADO, UserRole.MODERADOR, UserRole.ADMIN)
