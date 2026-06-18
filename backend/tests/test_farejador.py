"""
Testes do farejador de corrupção — heurísticas, scoring, worker.
"""
import pytest
from datetime import datetime, timedelta
from httpx import AsyncClient

from src.services.farejador.heuristicas import (
    analisar_texto,
    detectar_padroes_suspeitos,
    calcular_score,
    HeuristicaResultado,
)


# =============================================================================
# Testes unitários das heurísticas (puros, sem DB)
# =============================================================================
class TestHeuristicas:
    """Testes das funções puras de análise."""

    def test_detectar_menciona_valor_alto(self):
        """Texto mencionando valor muito alto deve gerar alerta."""
        texto = "A obra custou R$ 50 milhões com apenas 3 empresas participantes."
        resultado = analisar_texto(texto)
        assert any(r.tipo == "valor_alto" for r in resultado)

    def test_detectar_poucas_empresas(self):
        """Licitação com poucas empresas participantes é suspeito."""
        texto = "Licitação com apenas 1 empresa participante."
        resultado = analisar_texto(texto)
        assert any(r.tipo == "pouco_participantes" for r in resultado)

    def test_detectar_urgencia_injustificada(self):
        """Urgência sem justificativa clara deve ser flagada."""
        texto = "Dispensa de licitação URGENTÍSSIMA sem justificativa técnica detalhada."
        resultado = analisar_texto(texto)
        assert any(r.tipo == "urgencia_injustificada" for r in resultado)

    def test_detectar_sobrepreco(self):
        """Comparação de preços com sobrepreço deve ser detectada."""
        texto = "O valor contratado está 80% acima da média de mercado para o mesmo objeto."
        resultado = analisar_texto(texto)
        assert any(r.tipo == "sobrepreco" for r in resultado)

    def test_detectar_empresa_recem_criada(self):
        """Empresa recém-criada em contrato milionário é suspeito."""
        texto = "Empresa fundada há 6 meses ganhou contrato de R$ 10 milhões."
        resultado = analisar_texto(texto)
        assert any(r.tipo == "empresa_recem_criada" for r in resultado)

    def test_detectar_dirigente_servidor(self):
        """Dirigente que é também servidor público é conflito de interesse."""
        texto = "O dirigente da empresa contratada ocupa cargo de servidor público federal."
        resultado = analisar_texto(texto)
        assert any(r.tipo == "conflito_interesse" for r in resultado)

    def test_detectar_pagamento_atipico(self):
        """Pagamento adiantado ou parcelamento atípico é flagado."""
        texto = "Pagamento de 100% do valor antecipado, sem entrega comprovada."
        resultado = analisar_texto(texto)
        assert any(r.tipo == "pagamento_atipico" for r in resultado)

    def test_detectar_jogo_planilha(self):
        """Fracionamento / jogo de planilha é detectado."""
        texto = "Houve fracionamento da licitação em 3 processos para evitar o limite legal."
        resultado = analisar_texto(texto)
        assert any(r.tipo == "fracionamento" for r in resultado)

    def test_texto_limpo_sem_alertas(self):
        """Texto sem indícios não deve gerar alertas críticos."""
        texto = "A compra de 50 cadeiras para a escola municipal foi homologada normalmente."
        resultado = analisar_texto(texto)
        # Pode ter heurísticas leves, mas nada crítico
        criticos = [r for r in resultado if r.severidade == "critica"]
        assert len(criticos) == 0

    def test_calcular_score_zero(self):
        """Score deve ser 0 quando não há indícios."""
        resultados = []
        assert calcular_score(resultados) == 0

    def test_calcular_score_acumula(self):
        """Score deve acumular baseado na severidade."""
        resultados = [
            HeuristicaResultado(tipo="x", severidade="baixa", descricao="", peso=10),
            HeuristicaResultado(tipo="y", severidade="media", descricao="", peso=25),
            HeuristicaResultado(tipo="z", severidade="alta", descricao="", peso=50),
            HeuristicaResultado(tipo="w", severidade="critica", descricao="", peso=100),
        ]
        score = calcular_score(resultados)
        assert score == 185

    def test_calcular_score_com_cap(self):
        """Score deve ter um teto máximo (ex: 1000)."""
        resultados = [
            HeuristicaResultado(tipo="x", severidade="critica", descricao="", peso=9999)
        ]
        score = calcular_score(resultados)
        assert score <= 1000

    def test_detectar_padroes_texto_curto(self):
        """Textos muito curtos não devem ser analisados."""
        resultado = analisar_texto("buraco")
        assert resultado == []

    def test_detectar_padroes_texto_vazio(self):
        """Texto vazio deve retornar lista vazia sem erro."""
        resultado = analisar_texto("")
        assert resultado == []

    def test_sumarizar_para_humanos(self):
        """Resultado deve ter descrição legível para humanos."""
        texto = "Dispensa de licitação urgente com pagamento antecipado de R$ 1 milhão."
        resultado = analisar_texto(texto)
        assert len(resultado) > 0
        for r in resultado:
            assert r.descricao  # não vazio
            assert len(r.descricao) > 10  # descritivo


# =============================================================================
# Testes de integração (com DB)
# =============================================================================
@pytest.mark.asyncio
async def test_farejador_endpoint_analisar(client: AsyncClient, auth_headers_comum):
    """Endpoint de análise manual deve funcionar."""
    payload = {
        "texto": "Licitação com 1 empresa participante, valor de R$ 5 milhões, pagamento antecipado.",
        "contexto": {"fonte": "manual", "orgao": "PREFEITURA TESTE"},
    }
    resp = await client.post(
        "/api/farejador/analisar",
        json=payload,
        headers=auth_headers_comum,
    )
    assert resp.status_code in (200, 201)
    data = resp.json()
    assert "score" in data
    assert "indicios" in data
    assert data["score"] > 0  # tem indícios


@pytest.mark.asyncio
async def test_farejador_endpoint_texto_limpo(client: AsyncClient, auth_headers_comum):
    """Texto sem indícios deve ter score baixo."""
    payload = {
        "texto": "A escola recebeu 30 novas carteiras para os alunos do ensino fundamental.",
    }
    resp = await client.post(
        "/api/farejador/analisar",
        json=payload,
        headers=auth_headers_comum,
    )
    assert resp.status_code in (200, 201)
    data = resp.json()
    assert data["score"] < 50


@pytest.mark.asyncio
async def test_farejador_listar_fontes(client: AsyncClient):
    """Listagem de fontes ativas deve ser pública."""
    resp = await client.get("/api/farejador/fontes")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    # Deve ter pelo menos as fontes padrão
    nomes = [f["nome"] for f in data]
    assert any("Transparência" in n or "CGU" in n or "TCU" in n for n in nomes)


@pytest.mark.asyncio
async def test_farejador_dashboard_stats(client: AsyncClient, auth_headers_admin):
    """Dashboard do admin deve mostrar estatísticas."""
    resp = await client.get("/api/farejador/dashboard", headers=auth_headers_admin)
    assert resp.status_code == 200
    data = resp.json()
    assert "total_analises" in data or "total_indicios" in data


@pytest.mark.asyncio
async def test_farejador_rodar_coleta_manual(client: AsyncClient, auth_headers_admin):
    """Admin pode disparar coleta manual (em modo de teste não faz nada)."""
    resp = await client.post(
        "/api/farejador/coletar",
        headers=auth_headers_admin,
    )
    assert resp.status_code in (200, 202)
