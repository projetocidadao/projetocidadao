"""
Heurísticas de detecção de indícios de irregularidade.

O sistema combina análise textual (regex + NLP básico) com cruzamento
de dados para identificar padrões de risco em:
- Licitações e contratos
- Patrimônio de agentes
- Viagens e gastos
- Doações eleitorais
- Etc.

Severidades:
- critica (100 pts): forte indício de irregularidade
- alta     (50 pts)  : padrão atípico significativo
- media    (25 pts)  : merece atenção
- baixa    (10 pts)  : ponto de atenção
"""
import re
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from decimal import Decimal


# Teto máximo de score (evita outliers infinitos)
SCORE_TETO = 1000

# Tamanho mínimo de texto para análise
TAMANHO_MINIMO_TEXTO = 20


@dataclass
class HeuristicaResultado:
    """Um indício identificado pela análise."""
    tipo: str
    severidade: str  # 'critica', 'alta', 'media', 'baixa'
    descricao: str
    peso: int
    trecho: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Padrões (regex) e palavras-chave
# =============================================================================
PADROES = {
    # Valores monetários
    "valor_milhao": re.compile(
        r"R\$\s*(\d+[.,]?\d*)\s*(milh(ões|oes)|mi)\b", re.IGNORECASE
    ),
    "valor_bilhao": re.compile(
        r"R\$\s*(\d+[.,]?\d*)\s*(bilh(ões|oes)|bi)\b", re.IGNORECASE
    ),
    "valor_porcentagem": re.compile(
        r"(\d+)\s*%\s*(acima|maior|encima)", re.IGNORECASE
    ),

    # Frases suspeitas em licitações
    "dispensa": re.compile(r"\bdispensa\s+de\s+licita(ç|c)ão\b", re.IGNORECASE),
    "inexigibilidade": re.compile(r"\binexigibilidade\b", re.IGNORECASE),
    "urgencia": re.compile(r"\burgent(e|í?ssima)\b", re.IGNORECASE),
    "sem_justificativa": re.compile(r"sem\s+justificativ", re.IGNORECASE),
    "fracionamento": re.compile(r"\bfracion(a|amento)\w*", re.IGNORECASE),
    "jogo_planilha": re.compile(r"jogo\s+de\s+planilha", re.IGNORECASE),

    # Quantidades suspeitas
    "uma_empresa": re.compile(r"\b(uma|1|única|sozinha|sozinho)\s+empresa\s+particip", re.IGNORECASE),
    "duas_empresas": re.compile(r"\b(duas|2)\s+empresas\s+particip", re.IGNORECASE),
    "tres_empresas": re.compile(r"\b(três|3)\s+empresas\s+particip", re.IGNORECASE),

    # Temporalidade suspeita
    "empresa_recem": re.compile(
        r"(criada?|constitu(í?da?)|fundada?|aberta?)\s+(h[áa])\s+(\d+)\s+(meses?|dias?)", re.IGNORECASE
    ),
    "contrato_emergencial": re.compile(r"\bcontrato\s+emergencial\b", re.IGNORECASE),

    # Conflito de interesse
    "servidor_socio": re.compile(
        r"(sócio|dirigente|administrador)\s+(tamb[ée]m\s+)?(é|e\s+um)\s+servidor", re.IGNORECASE
    ),
    "parente_contratado": re.compile(
        r"(parente|cônjuge|filho|irmão|esposa)\s+(de|do|da)\s+(secretário|prefeito|gestor)", re.IGNORECASE
    ),

    # Pagamentos
    "antecipado": re.compile(r"\bantecipad[oa]\b", re.IGNORECASE),
    "pagamento_antecipado_100": re.compile(
        r"pagamento\s+antecipado\s+de\s+100\s*%", re.IGNORECASE
    ),
    "saque_alto": re.compile(r"\bsaque\s+(de\s+)?R\$\s*\d+[.,]?\d*\s*(mil|milh)", re.IGNORECASE),

    # Sobrepreço
    "sobrepreco": re.compile(r"\bsobrepre(ç|c)o\b", re.IGNORECASE),
    "acima_mercado": re.compile(r"(\d+)\s*%\s*acima\s+(do|da)\s+m[ée]dia", re.IGNORECASE),
    "superfaturamento": re.compile(r"\bsuperfatur", re.IGNORECASE),

    # Aditivos
    "aditivo_alto": re.compile(
        r"aditivo\s+(de\s+|contratual\s+de\s+)?(\d+)\s*%", re.IGNORECASE
    ),
    "aditivo_acima_limite": re.compile(
        r"aditivo\s+(acima|excede|ultrapassa)\s+(o\s+)?limite", re.IGNORECASE
    ),

    # Patrimônio
    "patrimonio_incompativel": re.compile(
        r"patrimônio\s+(incompat(í?vel|ível)|desproporcional|acima)", re.IGNORECASE
    ),
    "aumento_patrimonio": re.compile(
        r"(aumento|crescimento)\s+patrimonial\s+de\s+(\d+)\s*%", re.IGNORECASE
    ),

    # Outros
    "recurso_particular": re.compile(
        r"recurso\s+(particular|privado|externo)\s+(em|para|usado)", re.IGNORECASE
    ),
    "caixa_dois": re.compile(r"\bcaixa\s+(dois|2)\b", re.IGNORECASE),
    "propina": re.compile(r"\bpropina\b", re.IGNORECASE),
    "propina_suborno": re.compile(r"\b(suborno|mesada|mensalinho)\b", re.IGNORECASE),
}


# =============================================================================
# Função principal de análise
# =============================================================================
def analisar_texto(texto: str) -> List[HeuristicaResultado]:
    """
    Analisa um texto e retorna lista de indícios identificados.
    """
    resultados: List[HeuristicaResultado] = []

    if not texto or len(texto.strip()) < TAMANHO_MINIMO_TEXTO:
        return resultados

    texto_lower = texto.lower()

    # -- Valores --
    if PADROES["valor_bilhao"].search(texto):
        resultados.append(HeuristicaResultado(
            tipo="valor_bilhao",
            severidade="alta",
            descricao="Texto menciona valor na casa dos bilhões. Valores muito altos merecem atenção especial.",
            peso=50,
            trecho=PADROES["valor_bilhao"].search(texto).group(0),
        ))

    if PADROES["valor_milhao"].search(texto):
        m = PADROES["valor_milhao"].search(texto)
        try:
            valor = float(m.group(1).replace(",", "."))
            if valor >= 50:
                resultados.append(HeuristicaResultado(
                    tipo="valor_alto",
                    severidade="alta",
                    descricao=f"Contrato/valor de R$ {valor} milhões — valor significativo que merece análise.",
                    peso=40,
                    trecho=m.group(0),
                    metadata={"valor_milhoes": valor},
                ))
            elif valor >= 10:
                resultados.append(HeuristicaResultado(
                    tipo="valor_significativo",
                    severidade="media",
                    descricao=f"Contrato/valor de R$ {valor} milhões — expressivo.",
                    peso=20,
                    trecho=m.group(0),
                    metadata={"valor_milhoes": valor},
                ))
        except (ValueError, IndexError):
            pass

    # -- Licitação --
    if PADROES["dispensa"].search(texto):
        resultados.append(HeuristicaResultado(
            tipo="dispensa_licitacao",
            severidade="media",
            descricao="Há menção a dispensa de licitação. Verificar se os requisitos legais foram atendidos.",
            peso=25,
            trecho=PADROES["dispensa"].search(texto).group(0),
        ))

    if PADROES["inexigibilidade"].search(texto):
        resultados.append(HeuristicaResultado(
            tipo="inexigibilidade",
            severidade="media",
            descricao="Há menção a inexigibilidade. Verificar se a fundamentação é adequada.",
            peso=25,
        ))

    # -- Urgência --
    if PADROES["urgencia"].search(texto) and PADROES["sem_justificativa"].search(texto):
        resultados.append(HeuristicaResultado(
            tipo="urgencia_injustificada",
            severidade="alta",
            descricao="Menciona urgência sem justificativa clara — combinação típica de irregularidades.",
            peso=50,
        ))
    elif PADROES["urgencia"].search(texto):
        resultados.append(HeuristicaResultado(
            tipo="urgencia",
            severidade="baixa",
            descricao="Há menção a urgência. Verificar se há justificativa formal.",
            peso=10,
        ))

    # -- Fracionamento / jogo de planilha --
    if PADROES["fracionamento"].search(texto) or PADROES["jogo_planilha"].search(texto):
        resultados.append(HeuristicaResultado(
            tipo="fracionamento",
            severidade="critica",
            descricao="Fracionamento de licitação ou jogo de planilha — prática ilegal para burlar limites.",
            peso=100,
        ))

    # -- Concentração de participantes --
    if PADROES["uma_empresa"].search(texto):
        resultados.append(HeuristicaResultado(
            tipo="pouco_participantes",
            severidade="critica",
            descricao="Licitação com apenas 1 empresa participante — forte indício de direcionamento.",
            peso=100,
        ))
    elif PADROES["duas_empresas"].search(texto):
        resultados.append(HeuristicaResultado(
            tipo="pouco_participantes",
            severidade="alta",
            descricao="Licitação com apenas 2 empresas participantes — competitividade duvidosa.",
            peso=50,
        ))
    elif PADROES["tres_empresas"].search(texto):
        resultados.append(HeuristicaResultado(
            tipo="pouco_participantes",
            severidade="media",
            descricao="Licitação com apenas 3 empresas participantes.",
            peso=20,
        ))

    # -- Sobrepreço --
    if PADROES["sobrepreco"].search(texto) or PADROES["superfaturamento"].search(texto):
        m = PADROES["valor_porcentagem"].search(texto)
        porcentagem = int(m.group(1)) if m else None
        if porcentagem and porcentagem >= 50:
            resultados.append(HeuristicaResultado(
                tipo="sobrepreco_grave",
                severidade="critica",
                descricao=f"Sobrepreço de {porcentagem}% detectado — diferença muito acima do aceitável.",
                peso=100,
                metadata={"porcentagem": porcentagem},
            ))
        else:
            resultados.append(HeuristicaResultado(
                tipo="sobrepreco",
                severidade="alta",
                descricao="Sobrepreço detectado — valor acima da média de mercado.",
                peso=50,
                metadata={"porcentagem": porcentagem} if porcentagem else {},
            ))

    if PADROES["acima_mercado"].search(texto):
        m = PADROES["acima_mercado"].search(texto)
        resultados.append(HeuristicaResultado(
            tipo="acima_mercado",
            severidade="alta",
            descricao=f"Valor {m.group(1)}% acima da média de mercado.",
            peso=50,
        ))

    # -- Empresa recém-criada --
    if PADROES["empresa_recem"].search(texto):
        m = PADROES["empresa_recem"].search(texto)
        try:
            qtd = int(m.group(4))
            unidade = m.group(5).lower()
            # Converter para meses
            meses = qtd if "mes" in unidade else (qtd / 30)

            if meses <= 12:
                resultados.append(HeuristicaResultado(
                    tipo="empresa_recem_criada",
                    severidade="critica",
                    descricao=f"Empresa criada há {qtd} {unidade} ({meses:.0f} meses) — muito nova para contratos relevantes.",
                    peso=100,
                ))
            elif meses <= 24:
                resultados.append(HeuristicaResultado(
                    tipo="empresa_jovem",
                    severidade="media",
                    descricao=f"Empresa criada há {qtd} {unidade} — relativamente nova.",
                    peso=20,
                ))
        except (ValueError, IndexError):
            pass

    # -- Conflito de interesse --
    if PADROES["servidor_socio"].search(texto):
        resultados.append(HeuristicaResultado(
            tipo="conflito_interesse",
            severidade="critica",
            descricao="Sócio/dirigente que é também servidor público — conflito de interesse direto.",
            peso=100,
        ))

    if PADROES["parente_contratado"].search(texto):
        resultados.append(HeuristicaResultado(
            tipo="nepotismo",
            severidade="critica",
            descricao="Possível caso de nepotismo — parente de autoridade em contratação.",
            peso=100,
        ))

    # -- Pagamentos --
    if PADROES["pagamento_antecipado_100"].search(texto):
        resultados.append(HeuristicaResultado(
            tipo="pagamento_antecipado_total",
            severidade="critica",
            descricao="Pagamento de 100% antecipado sem entrega comprovada — altíssimo risco.",
            peso=100,
        ))
    elif PADROES["antecipado"].search(texto):
        resultados.append(HeuristicaResultado(
            tipo="pagamento_antecipado",
            severidade="media",
            descricao="Pagamento antecipado mencionado — verificar se há garantia de entrega.",
            peso=20,
        ))

    if PADROES["saque_alto"].search(texto):
        resultados.append(HeuristicaResultado(
            tipo="saque_alto",
            severidade="alta",
            descricao="Saque alto em espécie — padrão atípico de gastos públicos.",
            peso=50,
        ))

    # -- Aditivos --
    if PADROES["aditivo_acima_limite"].search(texto):
        resultados.append(HeuristicaResultado(
            tipo="aditivo_irregular",
            severidade="critica",
            descricao="Aditivo contratual acima do limite legal — irregularidade grave.",
            peso=100,
        ))
    elif PADROES["aditivo_alto"].search(texto):
        m = PADROES["aditivo_alto"].search(texto)
        try:
            pct = int(m.group(2))
            if pct >= 25:
                resultados.append(HeuristicaResultado(
                    tipo="aditivo_alto",
                    severidade="alta",
                    descricao=f"Aditivo contratual de {pct}% — acréscimo significativo.",
                    peso=50,
                    metadata={"porcentagem": pct},
                ))
            elif pct >= 10:
                resultados.append(HeuristicaResultado(
                    tipo="aditivo_significativo",
                    severidade="media",
                    descricao=f"Aditivo contratual de {pct}%.",
                    peso=20,
                ))
        except (ValueError, IndexError):
            pass

    # -- Patrimônio --
    if PADROES["patrimonio_incompativel"].search(texto):
        resultados.append(HeuristicaResultado(
            tipo="patrimonio_incompativel",
            severidade="alta",
            descricao="Patrimônio declarado incompatível com a renda.",
            peso=50,
        ))

    if PADROES["aumento_patrimonio"].search(texto):
        m = PADROES["aumento_patrimonio"].search(texto)
        try:
            pct = int(m.group(2))
            if pct >= 100:
                resultados.append(HeuristicaResultado(
                    tipo="aumento_patrimonial_anormal",
                    severidade="critica",
                    descricao=f"Aumento patrimonial de {pct}% — variação anormalmente alta.",
                    peso=100,
                ))
        except (ValueError, IndexError):
            pass

    # -- Palavras-chave explícitas --
    if PADROES["caixa_dois"].search(texto):
        resultados.append(HeuristicaResultado(
            tipo="caixa_dois",
            severidade="critica",
            descricao="Menção explícita a 'caixa dois'.",
            peso=100,
        ))

    if PADROES["propina"].search(texto) or PADROES["propina_suborno"].search(texto):
        resultados.append(HeuristicaResultado(
            tipo="propina_suborno",
            severidade="critica",
            descricao="Menção a propina ou suborno.",
            peso=100,
        ))

    if PADROES["recurso_particular"].search(texto):
        resultados.append(HeuristicaResultado(
            tipo="recurso_particular",
            severidade="alta",
            descricao="Uso de recursos públicos para fins particulares.",
            peso=50,
        ))

    if PADROES["contrato_emergencial"].search(texto):
        resultados.append(HeuristicaResultado(
            tipo="contrato_emergencial",
            severidade="baixa",
            descricao="Contrato emergencial — verificar se enquadra nas hipóteses legais.",
            peso=10,
        ))

    return resultados


def calcular_score(indicios: List[HeuristicaResultado]) -> int:
    """Calcula score consolidado a partir dos indícios."""
    total = sum(i.peso for i in indicios)
    return min(total, SCORE_TETO)


def classificar_score(score: int) -> str:
    """Classifica um score em nível de risco."""
    if score >= 200:
        return "critico"
    if score >= 100:
        return "alto"
    if score >= 50:
        return "moderado"
    if score >= 20:
        return "baixo"
    return "minimo"


def cor_por_severidade(severidade: str) -> str:
    """Retorna cor associada a uma severidade (hex)."""
    return {
        "critica": "#dc2626",  # red-600
        "alta": "#ea580c",     # orange-600
        "media": "#ca8a04",    # yellow-600
        "baixa": "#2563eb",    # blue-600
    }.get(severidade, "#6b7280")  # gray-500


# Compatibilidade com nome antigo
detectar_padroes_suspeitos = analisar_texto
