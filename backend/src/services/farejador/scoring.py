"""
Sistema de scoring e ranking de indícios.

Combina:
- Severidade da heurística
- Confiabilidade da fonte
- Recorrência (mesmo padrão repetido)
- Cruzamento com outras denúncias
- Contexto histórico (orgão, agente, etc.)
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from .heuristicas import HeuristicaResultado, calcular_score, classificar_score, cor_por_severidade


@dataclass
class IndicioPonderado:
    """Indício com peso ajustado por contexto."""
    heuristica: HeuristicaResultado
    peso_original: int
    peso_ajustado: int
    multiplicador: float
    justificativa_ajuste: str
    metadata_extras: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnaliseCompleta:
    """Resultado consolidado de uma análise."""
    texto_original: str
    indicios_brutos: List[HeuristicaResultado]
    indicios_ponderados: List[IndicioPonderado]
    score_bruto: int
    score_ajustado: int
    nivel_risco: str
    cor_risco: str
    recomendacao: str
    fatores_agravantes: List[str]
    fatores_atenuantes: List[str]
    cruza_com_outras_denuncias: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


def aplicar_multiplicadores(
    indicio: HeuristicaResultado,
    contexto: Dict[str, Any],
) -> IndicioPonderado:
    """
    Aplica multiplicadores ao peso de um indício baseado em contexto.

    Contexto esperado:
    - orgao: nome do órgão (alguns órgãos têm mais ocorrências históricas)
    - valor_contrato: valor em reais (valores muito altos recebem bônus)
    - historico_orgao: número de irregularidades anteriores do órgão
    - agente_recorrente: True se o mesmo agente já apareceu
    - fonte_confiavel: True se a fonte tem alta confiabilidade
    """
    multiplicador = 1.0
    justificativas: List[str] = []
    metadata: Dict[str, Any] = {}

    # Multiplicador por histórico do órgão
    historico = contexto.get("historico_orgao", 0)
    if historico >= 10:
        multiplicador *= 1.5
        justificativas.append(f"Órgão com {historico} ocorrências anteriores (+50%)")
    elif historico >= 5:
        multiplicador *= 1.25
        justificativas.append(f"Órgão com {historico} ocorrências anteriores (+25%)")
    elif historico >= 2:
        multiplicador *= 1.1
        justificativas.append(f"Órgão com {historico} ocorrências anteriores (+10%)")

    # Multiplicador por valor do contrato
    valor = contexto.get("valor_contrato", 0)
    if valor >= 100_000_000:  # R$ 100 milhões
        multiplicador *= 1.3
        justificativas.append(f"Contrato de R$ {valor/1_000_000:.0f} milhões (+30%)")
    elif valor >= 10_000_000:  # R$ 10 milhões
        multiplicador *= 1.15
        justificativas.append(f"Contrato de R$ {valor/1_000_000:.0f} milhões (+15%)")

    # Multiplicador por agente recorrente
    if contexto.get("agente_recorrente"):
        multiplicador *= 1.4
        justificativas.append("Agente já envolvido em outras denúncias (+40%)")

    # Multiplicador por fonte confiável
    if contexto.get("fonte_confiavel"):
        multiplicador *= 1.1
        justificativas.append("Fonte com alta confiabilidade (+10%)")

    # Atenuante: se houver auditoria recente sem apontamentos
    if contexto.get("auditoria_recente_ok"):
        multiplicador *= 0.7
        justificativas.append("Auditoria recente sem apontamentos (-30%)")

    peso_ajustado = int(indicio.peso * multiplicador)

    return IndicioPonderado(
        heuristica=indicio,
        peso_original=indicio.peso,
        peso_ajustado=peso_ajustado,
        multiplicador=multiplicador,
        justificativa_ajuste="; ".join(justificativas) if justificativas else "Sem ajustes",
        metadata_extras=metadata,
    )


def detectar_fatores_agravantes(
    indicios: List[HeuristicaResultado],
    contexto: Dict[str, Any],
) -> List[str]:
    """Detecta fatores que agravam o risco."""
    agravantes = []

    tipos = {i.tipo for i in indicios}

    # Combinações de indícios que se reforçam
    if "pouco_participantes" in tipos and "valor_alto" in tipos:
        agravantes.append("Combinação de poucos participantes + valor alto")

    if "fracionamento" in tipos and "urgencia_injustificada" in tipos:
        agravantes.append("Fracionamento combinado com urgência injustificada")

    if "empresa_recem_criada" in tipos and "valor_alto" in tipos:
        agravantes.append("Empresa recém-criada com contrato de valor alto")

    if "conflito_interesse" in tipos and "valor_alto" in tipos:
        agravantes.append("Conflito de interesse em contrato de alto valor")

    if "pagamento_antecipado_total" in tipos and "fracionamento" in tipos:
        agravantes.append("Pagamento antecipado total com fracionamento")

    if contexto.get("historico_orgao", 0) >= 5:
        agravantes.append(f"Órgão com {contexto['historico_orgao']} ocorrências anteriores")

    if len([i for i in indicios if i.severidade == "critica"]) >= 2:
        agravantes.append(f"{len([i for i in indicios if i.severidade == 'critica'])} indícios críticos simultâneos")

    return agravantes


def detectar_fatores_atenuantes(
    indicios: List[HeuristicaResultado],
    contexto: Dict[str, Any],
) -> List[str]:
    """Detecta fatores que atenuam o risco."""
    atenuantes = []

    if contexto.get("auditoria_recente_ok"):
        atenuantes.append("Auditoria recente sem apontamentos")

    if contexto.get("licitacao_eletronica"):
        atenuantes.append("Pregão eletrônico (maior transparência)")

    if contexto.get("publicacao_edital_ampla"):
        atenuantes.append("Edital publicado com ampla antecedência")

    if contexto.get("valor_contrato", 0) < 50_000:
        atenuantes.append("Valor baixo do contrato")

    tipos = {i.tipo for i in indicios}
    if "pouco_participantes" not in tipos and "fracionamento" not in tipos:
        atenuantes.append("Sem indícios de direcionamento ou fracionamento")

    if "conflito_interesse" not in tipos and "nepotismo" not in tipos:
        atenuantes.append("Sem indícios de conflito de interesse")

    return atenuantes


def gerar_recomendacao(
    nivel_risco: str,
    indicios: List[HeuristicaResultado],
    agravantes: List[str],
) -> str:
    """Gera recomendação de ação baseada no risco."""
    if nivel_risco == "critico":
        return (
            "🚨 RISCO CRÍTICO — Recomenda-se: "
            "(1) Denúncia imediata aos órgãos de controle (CGU/MP/TCU); "
            "(2) Notificação ao Ministério Público; "
            "(3) Publicação em veículos de imprensa; "
            "(4) Acompanhamento próximo."
        )
    if nivel_risco == "alto":
        return (
            "⚠️ RISCO ALTO — Recomenda-se: "
            "(1) Verificação detalhada com pedido LAI; "
            "(2) Notificação à CGU e ao TCU; "
            "(3) Acompanhamento público do caso."
        )
    if nivel_risco == "moderado":
        return (
            "🟡 RISCO MODERADO — Recomenda-se: "
            "(1) Acompanhamento próximo; "
            "(2) Verificação de documentos complementares; "
            "(3) Notificação à ouvidoria do órgão."
        )
    if nivel_risco == "baixo":
        return "🟢 Risco baixo. Manter monitoramento regular."
    return "⚪ Risco mínimo. Arquivar como informativo."


def analisar_completo(
    texto: str,
    contexto: Optional[Dict[str, Any]] = None,
) -> AnaliseCompleta:
    """
    Análise completa de um texto com ponderação e recomendação.
    """
    from .heuristicas import analisar_texto

    contexto = contexto or {}

    # 1) Detectar indícios brutos
    indicios_brutos = analisar_texto(texto)
    score_bruto = calcular_score(indicios_brutos)

    # 2) Aplicar multiplicadores contextuais
    indicios_ponderados = [
        aplicar_multiplicadores(i, contexto) for i in indicios_brutos
    ]

    # 3) Calcular score ajustado
    score_ajustado = sum(ip.peso_ajustado for ip in indicios_ponderados)
    score_ajustado = min(score_ajustado, 1000)

    # 4) Classificar risco
    nivel = classificar_score(score_ajustado)
    cor = cor_por_severidade({
        "critico": "critica",
        "alto": "alta",
        "moderado": "media",
        "baixo": "baixa",
        "minimo": "baixa",
    }.get(nivel, "baixa"))

    # 5) Detectar fatores agravantes/atenuantes
    agravantes = detectar_fatores_agravantes(indicios_brutos, contexto)
    atenuantes = detectar_fatores_atenuantes(indicios_brutos, contexto)

    # 6) Gerar recomendação
    recomendacao = gerar_recomendacao(nivel, indicios_brutos, agravantes)

    return AnaliseCompleta(
        texto_original=texto,
        indicios_brutos=indicios_brutos,
        indicios_ponderados=indicios_ponderados,
        score_bruto=score_bruto,
        score_ajustado=score_ajustado,
        nivel_risco=nivel,
        cor_risco=cor,
        recomendacao=recomendacao,
        fatores_agravantes=agravantes,
        fatores_atenuantes=atenuantes,
        cruza_com_outras_denuncias=contexto.get("cruza_denuncias", False),
        metadata={"contexto": contexto},
    )


def ranking_indicios(analises: List[AnaliseCompleta]) -> List[Dict[str, Any]]:
    """
    Gera ranking agregado de indícios a partir de várias análises.
    Útil para dashboard / relatórios.
    """
    contador: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
        "tipo": "",
        "total": 0,
        "score_total": 0,
        "severidade_max": "baixa",
        "descricao": "",
    })

    ordem_severidade = {"baixa": 1, "media": 2, "alta": 3, "critica": 4}

    for analise in analises:
        for ind in analise.indicios_brutos:
            key = ind.tipo
            contador[key]["tipo"] = ind.tipo
            contador[key]["total"] += 1
            contador[key]["score_total"] += ind.peso
            contador[key]["descricao"] = ind.descricao
            if ordem_severidade.get(ind.severidade, 0) > ordem_severidade.get(contador[key]["severidade_max"], 0):
                contador[key]["severidade_max"] = ind.severidade

    ranking = sorted(
        contador.values(),
        key=lambda x: (-x["score_total"], -x["total"]),
    )
    return ranking
