"""
Testes de denúncias — CRUD, listagem, filtros.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_criar_denuncia_sucesso(client: AsyncClient, auth_headers_comum, area_exemplo):
    """Criar denúncia autenticado deve retornar 201."""
    payload = {
        "titulo": "Postes sem iluminação",
        "descricao": "A rua está sem luz há 3 meses, causando insegurança.",
        "categoria": "seguranca",
        "area_id": area_exemplo.id,
        "municipio": "São Paulo",
        "estado": "SP",
        "latitude": -23.5505,
        "longitude": -46.6333,
    }
    resp = await client.post("/api/denuncias", json=payload, headers=auth_headers_comum)
    assert resp.status_code == 201
    data = resp.json()
    assert data["titulo"] == payload["titulo"]
    assert data["autor_id"] is not None
    assert data["status"] == "nova"


@pytest.mark.asyncio
async def test_criar_denuncia_sem_auth(client: AsyncClient, area_exemplo):
    """Criar denúncia sem autenticação deve retornar 401."""
    payload = {
        "titulo": "Teste",
        "descricao": "Descrição",
        "categoria": "saude",
        "area_id": area_exemplo.id,
    }
    resp = await client.post("/api/denuncias", json=payload)
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_listar_denuncias(client: AsyncClient, multiplas_denuncias):
    """Listar denúncias públicas deve funcionar sem auth."""
    resp = await client.get("/api/denuncias")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= len(multiplas_denuncias)


@pytest.mark.asyncio
async def test_listar_denuncias_paginacao(client: AsyncClient, multiplas_denuncias):
    """Paginação deve funcionar."""
    resp = await client.get("/api/denuncias?limit=2&offset=0")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) <= 2


@pytest.mark.asyncio
async def test_listar_denuncias_filtro_categoria(client: AsyncClient, multiplas_denuncias):
    """Filtro por categoria deve funcionar."""
    resp = await client.get("/api/denuncias?categoria=saude")
    assert resp.status_code == 200
    data = resp.json()
    for d in data:
        assert d["categoria"] == "saude"


@pytest.mark.asyncio
async def test_obter_denuncia_por_id(client: AsyncClient, denuncia_exemplo):
    """Obter denúncia específica deve funcionar."""
    resp = await client.get(f"/api/denuncias/{denuncia_exemplo.id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == denuncia_exemplo.id
    assert data["titulo"] == denuncia_exemplo.titulo


@pytest.mark.asyncio
async def test_obter_denuncia_inexistente(client: AsyncClient):
    """Denúncia inexistente deve retornar 404."""
    resp = await client.get("/api/denuncias/99999")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_atualizar_denuncia_autor(client: AsyncClient, denuncia_exemplo, auth_headers_comum):
    """Autor pode atualizar sua denúncia."""
    payload = {"titulo": "Título atualizado"}
    resp = await client.patch(
        f"/api/denuncias/{denuncia_exemplo.id}",
        json=payload,
        headers=auth_headers_comum,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["titulo"] == "Título atualizado"


@pytest.mark.asyncio
async def test_deletar_denuncia_autor(client: AsyncClient, denuncia_exemplo, auth_headers_comum):
    """Autor pode deletar sua denúncia."""
    resp = await client.delete(
        f"/api/denuncias/{denuncia_exemplo.id}",
        headers=auth_headers_comum,
    )
    assert resp.status_code in (200, 204)


@pytest.mark.asyncio
async def test_denuncias_proximas(client: AsyncClient, denuncia_exemplo):
    """Busca por proximidade (raio em km) deve funcionar."""
    # Coordenadas próximas (~1km de distância)
    resp = await client.get(
        "/api/denuncias/proximas?lat=-23.5505&lng=-46.6333&raio_km=5"
    )
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
