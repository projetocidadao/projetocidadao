"""
Testes de autenticação — registro, login, JWT.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_registrar_usuario_sucesso(client: AsyncClient):
    """Registro de novo usuário deve retornar 201 e token."""
    payload = {
        "email": "novo@test.org",
        "nome": "Novo Usuário",
        "senha": "senhaSegura123",
    }
    resp = await client.post("/api/auth/registrar", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["usuario"]["email"] == "novo@test.org"


@pytest.mark.asyncio
async def test_registrar_email_duplicado(client: AsyncClient, usuario_comum):
    """Registro com email já existente deve retornar 400."""
    payload = {
        "email": usuario_comum.email,
        "nome": "Outro Nome",
        "senha": "outraSenha123",
    }
    resp = await client.post("/api/auth/registrar", json=payload)
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_registrar_senha_curta(client: AsyncClient):
    """Senha com menos de 8 caracteres deve falhar."""
    payload = {
        "email": "fraco@test.org",
        "nome": "Senha Fraca",
        "senha": "123",
    }
    resp = await client.post("/api/auth/registrar", json=payload)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_login_sucesso(client: AsyncClient, usuario_comum):
    """Login com credenciais corretas deve retornar token."""
    payload = {
        "email": usuario_comum.email,
        "senha": "senha12345",
    }
    resp = await client.post("/api/auth/login", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data


@pytest.mark.asyncio
async def test_login_senha_incorreta(client: AsyncClient, usuario_comum):
    """Login com senha errada deve retornar 401."""
    payload = {
        "email": usuario_comum.email,
        "senha": "senhaErrada",
    }
    resp = await client.post("/api/auth/login", json=payload)
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_usuario_inexistente(client: AsyncClient):
    """Login com email não cadastrado deve retornar 401."""
    payload = {
        "email": "naoexiste@test.org",
        "senha": "qualquer123",
    }
    resp = await client.post("/api/auth/login", json=payload)
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_autenticado(client: AsyncClient, usuario_comum, auth_headers_comum):
    """Endpoint /me deve retornar dados do usuário logado."""
    resp = await client.get("/api/auth/me", headers=auth_headers_comum)
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == usuario_comum.email
    assert data["nome"] == usuario_comum.nome


@pytest.mark.asyncio
async def test_me_sem_token(client: AsyncClient):
    """Endpoint /me sem token deve retornar 401."""
    resp = await client.get("/api/auth/me")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_token_invalido(client: AsyncClient):
    """Endpoint /me com token inválido deve retornar 401."""
    headers = {"Authorization": "Bearer token-invalido-aqui"}
    resp = await client.get("/api/auth/me", headers=headers)
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_logout(client: AsyncClient, auth_headers_comum):
    """Logout deve retornar sucesso."""
    resp = await client.post("/api/auth/logout", headers=auth_headers_comum)
    assert resp.status_code in (200, 204)
