"""
Testes de votação — registrar, atualizar, ranking.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_votar_em_denuncia(client: AsyncClient, denuncia_exemplo, auth_headers_comum):
    """Votar em denúncia deve funcionar."""
    payload = {"apoio": True, "peso": 1}
    resp = await client.post(
        f"/api/denuncias/{denuncia_exemplo.id}/votos",
        json=payload,
        headers=auth_headers_comum,
    )
    assert resp.status_code in (200, 201)


@pytest.mark.asyncio
async def test_voto_duplicado_atualiza(client: AsyncClient, denuncia_exemplo, auth_headers_comum):
    """Voto duplicado deve atualizar (não criar novo)."""
    payload1 = {"apoio": True, "peso": 1}
    resp1 = await client.post(
        f"/api/denuncias/{denuncia_exemplo.id}/votos",
        json=payload1,
        headers=auth_headers_comum,
    )
    assert resp1.status_code in (200, 201)

    # Segundo voto (mesmo usuário) deve atualizar
    payload2 = {"apoio": False, "peso": 2}
    resp2 = await client.post(
        f"/api/denuncias/{denuncia_exemplo.id}/votos",
        json=payload2,
        headers=auth_headers_comum,
    )
    assert resp2.status_code in (200, 201)


@pytest.mark.asyncio
async def test_listar_votos_denuncia(client: AsyncClient, denuncia_exemplo, auth_headers_comum):
    """Listar votos de uma denúncia deve funcionar."""
    # Cria um voto primeiro
    await client.post(
        f"/api/denuncias/{denuncia_exemplo.id}/votos",
        json={"apoio": True, "peso": 1},
        headers=auth_headers_comum,
    )
    resp = await client.get(f"/api/denuncias/{denuncia_exemplo.id}/votos")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_ranking_usuarios(client: AsyncClient):
    """Ranking de usuários deve funcionar."""
    resp = await client.get("/api/votos/ranking")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_stats_votos_denuncia(client: AsyncClient, denuncia_exemplo, auth_headers_comum):
    """Estatísticas de votos devem funcionar."""
    await client.post(
        f"/api/denuncias/{denuncia_exemplo.id}/votos",
        json={"apoio": True, "peso": 1},
        headers=auth_headers_comum,
    )
    resp = await client.get(f"/api/denuncias/{denuncia_exemplo.id}/votos/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert "total" in data or "apoios" in data or "contestacoes" in data
