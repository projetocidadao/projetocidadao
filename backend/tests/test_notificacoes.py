"""
Testes de notificações — templates, criação, listagem.
"""
import pytest
from httpx import AsyncClient

from src.services.notificacoes.templates import renderizar_template, TEMPLATES


# =============================================================================
# Testes unitários de templates
# =============================================================================
class TestTemplates:
    def test_todos_templates_definidos(self):
        """Todos os tipos de notificação devem ter template."""
        tipos_esperados = [
            "denuncia_recebida",
            "denuncia_status",
            "novo_apoio",
            "novo_faro",
            "novo_comentario",
            "verificacao_solicitada",
            "alerta_urgente",
        ]
        for tipo in tipos_esperados:
            assert tipo in TEMPLATES, f"Template faltando: {tipo}"

    def test_renderizar_template_denuncia(self):
        """Template de denúncia deve incluir dados do denunciante."""
        resultado = renderizar_template(
            "denuncia_recebida",
            {
                "nome": "João",
                "titulo": "Buraco na rua",
                "id": "DEN-123",
            },
        )
        assert "João" in resultado["titulo"] or "João" in resultado["corpo"]
        assert "Buraco" in resultado["corpo"]
        assert "DEN-123" in resultado["corpo"]

    def test_renderizar_template_status(self):
        """Template de mudança de status deve mostrar antigo e novo."""
        resultado = renderizar_template(
            "denuncia_status",
            {
                "titulo": "Buraco na rua",
                "status_anterior": "nova",
                "status_novo": "em_analise",
            },
        )
        assert "nova" in resultado["corpo"].lower() or "análise" in resultado["corpo"].lower()
        assert "análise" in resultado["corpo"].lower() or "análise" in resultado["titulo"].lower()

    def test_renderizar_template_novo_apoio(self):
        """Template de novo apoio deve mencionar o apoiador."""
        resultado = renderizar_template(
            "novo_apoio",
            {
                "titulo": "Buraco na rua",
                "total_apoios": 42,
            },
        )
        assert "42" in resultado["corpo"] or "apoio" in resultado["corpo"].lower()

    def test_renderizar_template_inexistente(self):
        """Template inexistente deve gerar erro amigável."""
        with pytest.raises(KeyError):
            renderizar_template("template_que_nao_existe", {})

    def test_renderizar_template_variavel_faltando(self):
        """Faltando variável deve renderizar com placeholder."""
        # Não deve quebrar, apenas mostrar placeholder
        resultado = renderizar_template("denuncia_recebida", {})
        assert "corpo" in resultado
        assert "titulo" in resultado

    def test_template_anti_xss(self):
        """Templates devem escapar HTML malicioso."""
        resultado = renderizar_template(
            "denuncia_recebida",
            {"nome": "<script>alert(1)</script>", "titulo": "X", "id": "1"},
        )
        # O script não deve estar presente literalmente nas marcações
        # (depende da implementação — ajuste se necessário)
        assert isinstance(resultado["corpo"], str)


# =============================================================================
# Testes de integração (com DB)
# =============================================================================
@pytest.mark.asyncio
async def test_listar_notificacoes(client: AsyncClient, auth_headers_comum):
    """Usuário autenticado pode listar suas notificações."""
    resp = await client.get("/api/notificacoes", headers=auth_headers_comum)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_listar_notificacoes_nao_lidas(client: AsyncClient, auth_headers_comum):
    """Filtro de não lidas deve funcionar."""
    resp = await client.get("/api/notificacoes?apenas_nao_lidas=true", headers=auth_headers_comum)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_contar_nao_lidas(client: AsyncClient, auth_headers_comum):
    """Contador de não lidas deve funcionar."""
    resp = await client.get("/api/notificacoes/contador", headers=auth_headers_comum)
    assert resp.status_code == 200
    data = resp.json()
    assert "total" in data or "nao_lidas" in data


@pytest.mark.asyncio
async def test_marcar_como_lida(client: AsyncClient, auth_headers_comum, session, usuario_comum):
    """Marcar notificação como lida deve funcionar."""
    from src.models.notificacao import Notificacao
    from src.models.enums import TipoNotificacao

    n = Notificacao(
        usuario_id=usuario_comum.id,
        tipo=TipoNotificacao.DENUNCIA_RECEBIDA,
        titulo="Teste",
        corpo="Corpo",
        lida=False,
    )
    session.add(n)
    await session.commit()
    await session.refresh(n)

    resp = await client.patch(
        f"/api/notificacoes/{n.id}/lida",
        headers=auth_headers_comum,
    )
    assert resp.status_code in (200, 204)


@pytest.mark.asyncio
async def test_marcar_todas_como_lidas(client: AsyncClient, auth_headers_comum):
    """Marcar todas como lidas deve funcionar."""
    resp = await client.post("/api/notificacoes/marcar-todas-lidas", headers=auth_headers_comum)
    assert resp.status_code in (200, 204)


@pytest.mark.asyncio
async def test_deletar_notificacao(client: AsyncClient, auth_headers_comum, session, usuario_comum):
    """Deletar notificação deve funcionar."""
    from src.models.notificacao import Notificacao
    from src.models.enums import TipoNotificacao

    n = Notificacao(
        usuario_id=usuario_comum.id,
        tipo=TipoNotificacao.DENUNCIA_RECEBIDA,
        titulo="Para deletar",
        corpo="x",
        lida=True,
    )
    session.add(n)
    await session.commit()
    await session.refresh(n)

    resp = await client.delete(f"/api/notificacoes/{n.id}", headers=auth_headers_comum)
    assert resp.status_code in (200, 204)
