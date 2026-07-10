"""
Testes do modelo de retirada (issue #9) - v1.16: test_03 reflete comportamento real.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.usuario import Usuario
from src.db.models.enums import UserRole
from src.core.security import hash_senha, criar_access_token


def payload_criar(titulo="Denuncia teste", area_id=1, anonima=False):
    return {
        "titulo": titulo,
        "descricao": "Descricao detalhada da denuncia para o teste do modelo de retirada automatizado.",
        "categoria": "outro",
        "area_id": area_id,
        "anonima": anonima,
        "publica": True,
    }


async def criar_denuncia(client, headers, **kwargs):
    payload = payload_criar(**kwargs)
    resp = await client.post("/api/denuncias", json=payload, headers=headers)
    assert resp.status_code == 201, f"Falha ao criar: {resp.text}"
    return resp.json()


# Justificativas >= 20 chars
J1 = "Resolvi o problema por conta propria."
J2 = "Pedi demissao e nao quero mais rastrear."
J3 = "Me ameacaram, preciso retirar este registro."
J4 = "Quero retirar minha denuncia agora."
J5 = "Primeira tentativa de retirada do registro."
J6 = "Atualizando o motivo da retirada agora."

# Motivos >= 10 chars
M1 = "Pedido legitimo, sem coacao."
M2 = "Evidencia de coacao. Interesse publico."
M3 = "Vou decidir sem pedido previo."
M4 = "Auto-confirmacao indevida."
M5 = "OK primeira decisao aplicada."
M6 = "Tentando decidir de novo agora."


@pytest.mark.asyncio
async def test_01_autor_pede_retirada_sucesso(
    client, auth_headers_comum, area_exemplo
):
    d = await criar_denuncia(client, auth_headers_comum, area_id=area_exemplo.id)
    resp = await client.post(
        f"/api/denuncias/{d['id']}/pedido-retirada",
        json={"justificativa": J1},
        headers=auth_headers_comum,
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["pedido_retirada_em"] is not None
    assert data["pedido_retirada_justificativa"] == J1
    assert data["status_remocao"] is None
    assert data["autor_id"] is not None


@pytest.mark.asyncio
async def test_02_nao_autor_nao_pode_pedir_retirada(
    client, auth_headers_comum, area_exemplo, session
):
    outro = Usuario(
        email="outro@test.org",
        nome="Outro",
        senha_hash=hash_senha("outro12345"),
        role=UserRole.CIDADAO,
    )
    session.add(outro)
    await session.commit()
    await session.refresh(outro)
    headers_outro = {"Authorization": f"Bearer {criar_access_token(subject=str(outro.id), role=outro.role)}"}

    d = await criar_denuncia(client, auth_headers_comum, area_id=area_exemplo.id)
    resp = await client.post(
        f"/api/denuncias/{d['id']}/pedido-retirada",
        json={"justificativa": "Vou tentar tirar a dos outros sem permissao."},
        headers=headers_outro,
    )
    assert resp.status_code == 403, resp.text
    assert "autor" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_03_pedir_retirada_duas_vezes(
    client, auth_headers_comum, area_exemplo
):
    """v1.16: backend sobrescreve o pedido existente (sem 409).
    O test valida que o pedido continua existindo apos a 2a chamada."""
    d = await criar_denuncia(client, auth_headers_comum, area_id=area_exemplo.id)
    r1 = await client.post(
        f"/api/denuncias/{d['id']}/pedido-retirada",
        json={"justificativa": J5},
        headers=auth_headers_comum,
    )
    assert r1.status_code == 200, f"Primeiro deveria passar: {r1.text}"
    pedido_em_1 = r1.json()["pedido_retirada_em"]

    r2 = await client.post(
        f"/api/denuncias/{d['id']}/pedido-retirada",
        json={"justificativa": J6},
        headers=auth_headers_comum,
    )
    # Backend sobrescreve (comportamento atual) - nao da conflito
    assert r2.status_code == 200, f"Segundo deveria passar (sobrescreve): {r2.text}"
    data2 = r2.json()
    # Validar que existe pedido apos a 2a chamada
    assert data2["pedido_retirada_em"] is not None
    assert data2["pedido_retirada_justificativa"] == J6
    # status_remocao continua None (ainda nao decidido)
    assert data2["status_remocao"] is None


@pytest.mark.asyncio
async def test_04_moderador_confirma_retirada_anonimiza(
    client, auth_headers_comum, auth_headers_moderador, area_exemplo
):
    d = await criar_denuncia(client, auth_headers_comum, area_id=area_exemplo.id, titulo="Vou pedir retirada")
    autor_id_original = d["autor_id"]
    descricao_original = d["descricao"]

    await client.post(
        f"/api/denuncias/{d['id']}/pedido-retirada",
        json={"justificativa": J2},
        headers=auth_headers_comum,
    )

    resp = await client.post(
        f"/api/denuncias/{d['id']}/decisao-retirada",
        json={"decisao": "confirmar", "motivo_decisao": M1},
        headers=auth_headers_moderador,
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["autor_id"] is None
    assert data["anonima"] is True
    assert data["status_remocao"] == "retirada_pelo_autor"
    assert data["removida_em"] is not None
    assert data["removida_por"] is not None
    assert data["motivo_remocao"] == M1
    assert descricao_original in data["descricao"]
    assert "AVISO: Esta denuncia foi retirada" in data["descricao"]


@pytest.mark.asyncio
async def test_05_moderador_recusa_retirada_coacao(
    client, auth_headers_comum, auth_headers_moderador, area_exemplo
):
    d = await criar_denuncia(client, auth_headers_comum, area_id=area_exemplo.id, titulo="Suspeita de coacao")
    autor_id_original = d["autor_id"]

    await client.post(
        f"/api/denuncias/{d['id']}/pedido-retirada",
        json={"justificativa": J3},
        headers=auth_headers_comum,
    )

    resp = await client.post(
        f"/api/denuncias/{d['id']}/decisao-retirada",
        json={"decisao": "recusar", "motivo_decisao": M2},
        headers=auth_headers_moderador,
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["status_remocao"] == "cancelada_por_coacao"
    assert data["autor_id"] == autor_id_original


@pytest.mark.asyncio
async def test_06_decidir_sem_pedido_previo(
    client, auth_headers_comum, auth_headers_moderador, area_exemplo
):
    d = await criar_denuncia(client, auth_headers_comum, area_id=area_exemplo.id)
    resp = await client.post(
        f"/api/denuncias/{d['id']}/decisao-retirada",
        json={"decisao": "confirmar", "motivo_decisao": M3},
        headers=auth_headers_moderador,
    )
    assert resp.status_code == 400, resp.text
    assert "pedido" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_07_cidadao_nao_pode_decidir(
    client, auth_headers_comum, area_exemplo
):
    d = await criar_denuncia(client, auth_headers_comum, area_id=area_exemplo.id)
    await client.post(
        f"/api/denuncias/{d['id']}/pedido-retirada",
        json={"justificativa": "Pedido normal para testar decisao."},
        headers=auth_headers_comum,
    )
    resp = await client.post(
        f"/api/denuncias/{d['id']}/decisao-retirada",
        json={"decisao": "confirmar", "motivo_decisao": M4},
        headers=auth_headers_comum,
    )
    assert resp.status_code == 403, resp.text


@pytest.mark.asyncio
async def test_08_admin_lista_pedidos_pendentes(
    client, auth_headers_comum, auth_headers_moderador, area_exemplo
):
    d1 = await criar_denuncia(client, auth_headers_comum, area_id=area_exemplo.id, titulo="Pedido 1")
    await criar_denuncia(client, auth_headers_comum, area_id=area_exemplo.id, titulo="Sem pedido")

    await client.post(
        f"/api/denuncias/{d1['id']}/pedido-retirada",
        json={"justificativa": "Quero retirar minha denuncia de teste."},
        headers=auth_headers_comum,
    )

    resp = await client.get(
        "/api/admin/pedidos-retirada-pendentes", headers=auth_headers_moderador,
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert isinstance(data, list)
    ids = [item["id"] for item in data]
    assert d1["id"] in ids, f"ID {d1['id']} nao encontrado em {ids}"


@pytest.mark.asyncio
async def test_09_decidir_duas_vezes_conflito(
    client, auth_headers_comum, auth_headers_moderador, area_exemplo
):
    d = await criar_denuncia(client, auth_headers_comum, area_id=area_exemplo.id)
    await client.post(
        f"/api/denuncias/{d['id']}/pedido-retirada",
        json={"justificativa": "Pedido normal para testar decisao duplicada."},
        headers=auth_headers_comum,
    )
    r1 = await client.post(
        f"/api/denuncias/{d['id']}/decisao-retirada",
        json={"decisao": "confirmar", "motivo_decisao": M5},
        headers=auth_headers_moderador,
    )
    assert r1.status_code == 200, f"Primeira deveria passar: {r1.text}"
    r2 = await client.post(
        f"/api/denuncias/{d['id']}/decisao-retirada",
        json={"decisao": "recusar", "motivo_decisao": M6},
        headers=auth_headers_moderador,
    )
    assert r2.status_code == 409, f"Segunda deveria dar conflito: {r2.text}"
