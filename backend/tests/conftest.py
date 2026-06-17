"""
Fixtures globais para os testes.

Cria:
- DB de teste isolado (cria/destrói tabelas por sessão)
- Cliente HTTP assíncrono
- Usuário comum autenticado
- Usuário admin autenticado
- Denúncia de exemplo
"""
import asyncio
import os
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

# Força ambiente de teste ANTES de importar a app
os.environ["APP_ENV"] = "test"
os.environ["DATABASE_URL"] = "postgresql+asyncpg://postgres:postgres@localhost:5432/projetocidadao_test"
os.environ["JWT_SECRET"] = "test-secret-key-for-testing-only-32-chars"

from src.db.base import Base
from src.db.session import get_async_session
from src.core.security import hash_password, criar_access_token
from src.models.usuario import Usuario
from src.models.enums import UserRole, CategoriaDenuncia, StatusDenuncia
from src.models.denuncia import Denuncia
from src.models.area import Area
from src.main import app  # noqa: E402


# =============================================================================
# Event loop
# =============================================================================
@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Loop de eventos único por sessão."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# =============================================================================
# Database
# =============================================================================
TEST_DATABASE_URL = os.environ["DATABASE_URL"]


@pytest_asyncio.fixture(scope="session")
async def engine():
    """Engine de teste — cria/destrói schema."""
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def session(engine) -> AsyncGenerator[AsyncSession, None]:
    """Sessão de DB isolada por teste (com rollback)."""
    async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session_maker() as session:
        yield session
        await session.rollback()


# =============================================================================
# HTTP Client
# =============================================================================
@pytest_asyncio.fixture
async def client(session) -> AsyncGenerator[AsyncClient, None]:
    """Cliente HTTP com DB de teste injetado."""

    async def _override_session():
        yield session

    app.dependency_overrides[get_async_session] = _override_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


# =============================================================================
# Usuários
# =============================================================================
@pytest_asyncio.fixture
async def usuario_comum(session: AsyncSession) -> Usuario:
    """Usuário cidadão comum."""
    u = Usuario(
        email="cidadao@test.org",
        nome="Cidadão Teste",
        senha_hash=hash_password("senha12345"),
        role=UserRole.CIDADAO,
        verificado=True,
        ativo=True,
        pontos=0,
        nivel=1,
    )
    session.add(u)
    await session.commit()
    await session.refresh(u)
    return u


@pytest_asyncio.fixture
async def usuario_admin(session: AsyncSession) -> Usuario:
    """Usuário administrador."""
    u = Usuario(
        email="admin@test.org",
        nome="Admin Teste",
        senha_hash=hash_password("admin12345"),
        role=UserRole.ADMIN,
        verificado=True,
        ativo=True,
        pontos=1000,
        nivel=10,
    )
    session.add(u)
    await session.commit()
    await session.refresh(u)
    return u


@pytest_asyncio.fixture
async def usuario_moderador(session: AsyncSession) -> Usuario:
    """Usuário moderador."""
    u = Usuario(
        email="moderador@test.org",
        nome="Moderador Teste",
        senha_hash=hash_password("mod12345"),
        role=UserRole.MODERADOR,
        verificado=True,
        ativo=True,
    )
    session.add(u)
    await session.commit()
    await session.refresh(u)
    return u


# =============================================================================
# Tokens
# =============================================================================
@pytest.fixture
def token_comum(usuario_comum) -> str:
    return criar_access_token(subject=str(usuario_comum.id))


@pytest.fixture
def token_admin(usuario_admin) -> str:
    return criar_access_token(subject=str(usuario_admin.id))


@pytest.fixture
def token_moderador(usuario_moderador) -> str:
    return criar_access_token(subject=str(usuario_moderador.id))


@pytest.fixture
def auth_headers_comum(token_comum) -> dict:
    return {"Authorization": f"Bearer {token_comum}"}


@pytest.fixture
def auth_headers_admin(token_admin) -> dict:
    return {"Authorization": f"Bearer {token_admin}"}


@pytest.fixture
def auth_headers_moderador(token_moderador) -> dict:
    return {"Authorization": f"Bearer {token_moderador}"}


# =============================================================================
# Dados de exemplo
# =============================================================================
@pytest_asyncio.fixture
async def area_exemplo(session: AsyncSession) -> Area:
    """Área temática de exemplo."""
    a = Area(
        slug="saude",
        nome="Saúde",
        descricao="Denúncias relacionadas ao SUS e saúde pública",
        icone="🏥",
        cor="#dc2626",
        ativa=True,
    )
    session.add(a)
    await session.commit()
    await session.refresh(a)
    return a


@pytest_asyncio.fixture
async def denuncia_exemplo(session: AsyncSession, usuario_comum, area_exemplo) -> Denuncia:
    """Denúncia de exemplo."""
    d = Denuncia(
        titulo="Buraco na rua principal",
        descricao="Há um buraco enorme na Rua das Flores que está causando acidentes.",
        categoria=CategoriaDenuncia.TRANSPORTE,
        status=StatusDenuncia.NOVA,
        publica=True,
        autor_id=usuario_comum.id,
        area_id=area_exemplo.id,
        municipio="São Paulo",
        estado="SP",
        latitude=-23.5505,
        longitude=-46.6333,
    )
    session.add(d)
    await session.commit()
    await session.refresh(d)
    return d


@pytest_asyncio.fixture
async def multiplas_denuncias(session: AsyncSession, usuario_comum, area_exemplo) -> list[Denuncia]:
    """Várias denúncias para testes de listagem."""
    denuncias = []
    for i in range(5):
        d = Denuncia(
            titulo=f"Denúncia #{i+1}",
            descricao=f"Descrição da denúncia número {i+1}",
            categoria=CategoriaDenuncia.SAUDE,
            status=StatusDenuncia.NOVA,
            publica=True,
            autor_id=usuario_comum.id,
            area_id=area_exemplo.id,
            municipio="Rio de Janeiro",
            estado="RJ",
        )
        session.add(d)
        denuncias.append(d)
    await session.commit()
    for d in denuncias:
        await session.refresh(d)
    return denuncias
