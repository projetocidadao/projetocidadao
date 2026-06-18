"""
Testes de anexos — upload, listagem, validação.
"""
import io
import pytest
from httpx import AsyncClient


def _fake_image(filename: str = "foto.jpg", content_type: str = "image/jpeg") -> tuple:
    """Gera um arquivo de imagem falso em memória."""
    # Bytes mínimos válidos pra um JPEG
    data = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
    return (filename, io.BytesIO(data), content_type)


@pytest.mark.asyncio
async def test_upload_anexo_denuncia(client: AsyncClient, auth_headers_comum, denuncia_exemplo):
    """Upload de anexo deve funcionar."""
    files = {"arquivo": _fake_image()}
    data = {"descricao": "Foto do buraco"}
    resp = await client.post(
        f"/api/denuncias/{denuncia_exemplo.id}/anexos",
        files=files,
        data=data,
        headers=auth_headers_comum,
    )
    assert resp.status_code in (200, 201)
    body = resp.json()
    assert "id" in body
    assert body["tipo_arquivo"].startswith("image/")


@pytest.mark.asyncio
async def test_upload_multiplos_anexos(client: AsyncClient, auth_headers_comum, denuncia_exemplo):
    """Upload de múltiplos anexos deve funcionar."""
    files = [
        ("arquivos", _fake_image("a.jpg")),
        ("arquivos", _fake_image("b.jpg")),
        ("arquivos", _fake_image("c.jpg")),
    ]
    resp = await client.post(
        f"/api/denuncias/{denuncia_exemplo.id}/anexos/multiplos",
        files=files,
        headers=auth_headers_comum,
    )
    assert resp.status_code in (200, 201)


@pytest.mark.asyncio
async def test_listar_anexos_denuncia(client: AsyncClient, auth_headers_comum, denuncia_exemplo):
    """Listagem de anexos de uma denúncia deve funcionar."""
    # Primeiro faz um upload
    files = {"arquivo": _fake_image()}
    await client.post(
        f"/api/denuncias/{denuncia_exemplo.id}/anexos",
        files=files,
        headers=auth_headers_comum,
    )

    # Depois lista
    resp = await client.get(f"/api/denuncias/{denuncia_exemplo.id}/anexos")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_upload_sem_auth(client: AsyncClient, denuncia_exemplo):
    """Upload sem autenticação deve falhar."""
    files = {"arquivo": _fake_image()}
    resp = await client.post(
        f"/api/denuncias/{denuncia_exemplo.id}/anexos",
        files=files,
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_upload_arquivo_muito_grande(client: AsyncClient, auth_headers_comum, denuncia_exemplo):
    """Arquivo acima do limite deve ser rejeitado."""
    # 60 MB (acima do limite de 50 MB)
    big = b"\x00" * (60 * 1024 * 1024)
    files = {"arquivo": ("enorme.jpg", io.BytesIO(big), "image/jpeg")}
    resp = await client.post(
        f"/api/denuncias/{denuncia_exemplo.id}/anexos",
        files=files,
        headers=auth_headers_comum,
    )
    assert resp.status_code in (400, 413, 422)


@pytest.mark.asyncio
async def test_upload_tipo_invalido(client: AsyncClient, auth_headers_comum, denuncia_exemplo):
    """Tipo de arquivo não permitido deve ser rejeitado."""
    # .exe disfarçado
    files = {"arquivo": ("malware.exe", io.BytesIO(b"MZ\x90\x00"), "application/octet-stream")}
    resp = await client.post(
        f"/api/denuncias/{denuncia_exemplo.id}/anexos",
        files=files,
        headers=auth_headers_comum,
    )
    assert resp.status_code in (400, 415, 422)


@pytest.mark.asyncio
async def test_deletar_anexo(client: AsyncClient, auth_headers_comum, denuncia_exemplo, session):
    """Autor da denúncia pode deletar anexo."""
    from src.models.anexo import Anexo

    anexo = Anexo(
        denuncia_id=denuncia_exemplo.id,
        nome_arquivo="foto.jpg",
        caminho="/media/foto.jpg",
        tamanho=1024,
        tipo_arquivo="image/jpeg",
        autor_id=denuncia_exemplo.autor_id,
    )
    session.add(anexo)
    await session.commit()
    await session.refresh(anexo)

    resp = await client.delete(
        f"/api/anexos/{anexo.id}",
        headers=auth_headers_comum,
    )
    assert resp.status_code in (200, 204)
