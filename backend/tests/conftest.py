"""
Fixtures globais - v1.16: igual v1.15 (engine function-scoped).
"""
import asyncio
import os
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy import text

os.environ["APP_ENV"] = "test"
os.environ["DATABASE_URL"] = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://cidadao:cidadao_123@db:5432/projetocidadao_test"
)
os.environ["JWT_SECRET"] = "test-secret-key-for-testing-only-32-chars-min"

from src.db.base import Base
from src.db.session import get_async_session
from src.core.security import hash_senha, criar_access_token
from src.db.models.usuario import Usuario
from src.db.models.enums import UserRole, CategoriaDenuncia, StatusDenuncia
from src.db.models.denuncia import Denuncia
from src.db.models.area import Area
from main import app


TEST_DATABASE_URL = os.environ["DATABASE_URL"]


@pytest_asyncio.fixture
async def engine():
    eng = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    await eng.dispose()


async def _truncate_all(engine):
    async with engine.begin() as conn:
        rows = await conn.execute(text(
            "SELECT tablename FROM pg_tables WHERE schemaname='public'"
        ))
        tabelas = [r[0] for r in rows.fetchall()]
        if not tabelas:
            return
        lista = ", ".join(f'"{t}"' for t in tabelas)
        await conn.execute(text(f"TRUNCATE TABLE {lista} RESTART IDENTITY CASCADE"))


@pytest_asyncio.fixture
async def session(engine) -> AsyncGenerator[AsyncSession, None]:
    await _truncate_all(engine)
    async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session_maker() as session:
        yield session


@pytest_asyncio.fixture
async def client(session) -> AsyncGenerator[AsyncClient, None]:
    async def _override_session():
        yield session
    app.dependency_overrides[get_async_session] = _override_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def usuario_comum(session):
    u = Usuario(
        email="cidadao@test.org",
        nome="Cidadao Teste",
        senha_hash=hash_senha("senha12345"),
        role=UserRole.CIDADAO,
    )
    session.add(u)
    await session.commit()
    await session.refresh(u)
    return u


@pytest_asyncio.fixture
async def usuario_admin(session):
    u = Usuario(
        email="admin@test.org",
        nome="Admin Teste",
        senha_hash=hash_senha("admin12345"),
        role=UserRole.ADMIN,
    )
    session.add(u)
    await session.commit()
    await session.refresh(u)
    return u


@pytest_asyncio.fixture
async def usuario_moderador(session):
    u = Usuario(
        email="moderador@test.org",
        nome="Moderador Teste",
        senha_hash=hash_senha("mod12345"),
        role=UserRole.MODERADOR,
    )
    session.add(u)
    await session.commit()
    await session.refresh(u)
    return u


def _make_token(usuario):
    return criar_access_token(subject=str(usuario.id), role=usuario.role)


@pytest.fixture
def token_comum(usuario_comum) -> str:
    return _make_token(usuario_comum)


@pytest.fixture
def token_admin(usuario_admin) -> str:
    return _make_token(usuario_admin)


@pytest.fixture
def token_moderador(usuario_moderador) -> str:
    return _make_token(usuario_moderador)


@pytest.fixture
def auth_headers_comum(token_comum) -> dict:
    return {"Authorization": f"Bearer {token_comum}"}


@pytest.fixture
def auth_headers_admin(token_admin) -> dict:
    return {"Authorization": f"Bearer {token_admin}"}


@pytest.fixture
def auth_headers_moderador(token_moderador) -> dict:
    return {"Authorization": f"Bearer {token_moderador}"}


@pytest_asyncio.fixture
async def area_exemplo(session):
    sql = text(
        "INSERT INTO areas (slug, nome, descricao, icone, cor, artigo_cf, ordem, ativo) "
        "VALUES (:slug, :nome, :descricao, :icone, :cor, :artigo_cf, :ordem, :ativo) RETURNING id"
    )
    result = await session.execute(sql, {
        "slug": "saude",
        "nome": "Saude",
        "descricao": "Denuncias do SUS",
        "icone": "hospital",
        "cor": "#dc2626",
        "artigo_cf": "Art. 196 CF",
        "ordem": 0,
        "ativo": True,
    })
    area_id = result.scalar()

    from sqlalchemy import select
    a = (await session.execute(select(Area).where(Area.id == area_id))).scalar_one()
    return a


@pytest_asyncio.fixture
async def denuncia_exemplo(session, usuario_comum, area_exemplo):
    d = Denuncia(
        titulo="Buraco na rua",
        descricao="Ha um buraco enorme.",
        categoria=CategoriaDenuncia.TRANSPORTE.value,
        status=StatusDenuncia.AGUARDANDO,
        publica=True,
        autor_id=usuario_comum.id,
        area_id=area_exemplo.id,
    )
    session.add(d)
    await session.commit()
    await session.refresh(d)
    return d
