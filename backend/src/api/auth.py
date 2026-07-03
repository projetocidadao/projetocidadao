"""
Rotas de autenticação: registro e login.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_async_session
from src.db.config import settings
from src.db.models.usuario import Usuario
from src.schemas.usuario import (
    UsuarioCreate,
    UsuarioRead,
    Token,
    UsuarioLogin,
)
from src.core.security import hash_senha, verificar_senha, criar_access_token

from datetime import timedelta


router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UsuarioRead,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar novo usuário",
)
async def register(
    dados: UsuarioCreate,
    session: AsyncSession = Depends(get_async_session),
) -> Usuario:
    """Cria uma nova conta de cidadão."""
    # Verifica email duplicado
    result = await session.execute(select(Usuario).where(Usuario.email == dados.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email já cadastrado",
        )

    usuario = Usuario(
        email=dados.email,
        nome=dados.nome,
        senha_hash=hash_senha(dados.senha),
        biografia=dados.biografia,
        cidade=dados.cidade,
        estado=dados.estado,
    )
    session.add(usuario)
    await session.commit()
    await session.refresh(usuario)
    return usuario


@router.post(
    "/login",
    response_model=Token,
    summary="Login (form-data ou JSON)",
)
async def login(
    dados: UsuarioLogin,
    session: AsyncSession = Depends(get_async_session),
) -> Token:
    """Autentica e retorna um JWT."""
    result = await session.execute(select(Usuario).where(Usuario.email == dados.email))
    user = result.scalar_one_or_none()

    if not user or not verificar_senha(dados.senha, user.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha inválidos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo",
        )

    expires = timedelta(minutes=settings.jwt_expires_minutes)
    token = criar_access_token(
        subject=user.id,
        role=user.role.value,
        expires_delta=expires,
    )

    return Token(
        access_token=token,
        expires_in=settings.jwt_expires_minutes * 60,
        usuario=UsuarioRead.model_validate(user),
    )


@router.post(
    "/login/form",
    response_model=Token,
    summary="Login via OAuth2PasswordRequestForm (Swagger UI)",
    include_in_schema=True,
)
async def login_form(
    form: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_async_session),
) -> Token:
    """Endpoint de login compatível com o botão 'Authorize' da documentação."""
    result = await session.execute(select(Usuario).where(Usuario.email == form.username))
    user = result.scalar_one_or_none()

    if not user or not verificar_senha(form.password, user.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha inválidos",
        )

    token = criar_access_token(
        subject=user.id,
        role=user.role.value,
    )

    return Token(
        access_token=token,
        expires_in=settings.jwt_expires_minutes * 60,
        usuario=UsuarioRead.model_validate(user),
    )
