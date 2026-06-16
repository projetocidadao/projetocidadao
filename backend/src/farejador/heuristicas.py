"""
Heurísticas do Farejador — funções puras de detecção de sinais.

Cada heurística recebe dados e retorna um ResultadoHeuristica com:
- score_risco: 0 a 100
- severidade: BAIXA, MEDIA, ALTA, CRITICA
- heuristicas: lista de códigos das regras que dispararam
- evidencia: dict com os trechos que motivaram o alerta
"""
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Protocol


# =============================================================================
# Estruturas
# =============================================================================
@dataclass
class ResultadoHeuristica:
    """Resultado de uma avaliação heurística."""
    score_risco: int = 0
    severidade: str = "BAIXA"
    heuristicas: List[str] = field(default_factory=list)
    evidencia: Dict[str, Any] = field(default_factory=dict)
    peso: int = 1


class Heuristica(Protocol):
    """Interface de uma heurística."""
    codigo: str
    descricao: str
    def avaliar(self, dados: dict) -> ResultadoHeuristica: ...


# =============================================================================
# Dicionários de palavras-chave
# =============================================================================
PALAVRAS_GATILHO = {
    "propina": 25, "suborno": 25, "rachadinha": 20, "desvio": 20, "fraude": 25,
    "falsific": 20, "falsid": 20, "lavagem": 20, "sonegação": 18, "sonegar": 18,
    "caixa dois": 25, "caixa-preta": 20, "favorec": 15, "superfatur": 25,
    "sobrepreço": 20, "sobrepreco": 20, "emenda pix": 15, "emenda secreta": 18,
    "lobby": 5, "trafic": 20, "peculato": 25, "improbidade": 18,
    "licitação fraudada": 25, "direcionamento": 18, "cartel": 18, "conluio": 18,
    "mesada": 12, "voto de cabresto": 18, "nomeação irregular": 12,
    "fantasma": 10, "laranja": 12, "empresa de fachada": 18,
}

REGEX_CNPJ = re.compile(r"\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}")
REGEX_CPF = re.compile(r"\d{3}\.?\d{3}\.?\d{3}-?\d{2}")
REGEX_VALOR_ALTO = re.compile(r"R\$\s*(\d{1,3}(?:\.\d{3}){2,})")
REGEX_DINHEIRO = re.compile(r"(\d+)\s*(milhões?|milhões|mi|bi\b)", re.IGNORECASE)


# =============================================================================
# HEURÍSTICA 1 — Análise de Texto de Denúncia
# =============================================================================
def avaliar_texto_denuncia(
    titulo: str,
    descricao: str,
    categoria: Optional[str] = None,
) -> ResultadoHeuristica:
    """Analisa texto de denúncia em busca de palavras suspeitas e padrões."""
    texto = f"{titulo} {descricao}".lower()
    resultado = ResultadoHeuristica()
    palavras_encontradas: Dict[str, int] = {}
    valores_encontrados: List[str] = []

    for palavra, peso in PALAVRAS_GATILHO.items():
        if palavra in texto:
            palavras_encontradas[palavra] = peso
            resultado.heuristicas.append(f"palavra:{palavra}")
            resultado.score_risco += peso

    for match in REGEX_VALOR_ALTO.finditer(texto):
        valores_encontrados.append(match.group(0))
    if valores_encontrados:
        resultado.heuristicas.append("valores_altos_mencionados")
        resultado.score_risco += min(15, len(valores_encontrados) * 5)

    cnpjs = REGEX_CNPJ.findall(texto)
    cpfs = REGEX_CPF.findall(texto)
    if cnpjs or cpfs:
        resultado.heuristicas.append("documentos_identificados")
        resultado.score_risco += 8

    if categoria in ("financas", "saude", "transporte"):
        resultado.heuristicas.append(f"categoria_sensivel:{categoria}")
        resultado.score_risco += 5

    if len(descricao) > 2000:
        resultado.heuristicas.append("descricao_detalhada")
        resultado.score_risco += 5

    resultado.score_risco = min(100, resultado.score_risco)
    resultado.evidencia = {
        "palavras_gatilho": palavras_encontradas,
        "valores": valores_encontrados,
        "cnpjs": cnpjs,
        "cpfs": cpfs,
        "comprimento_texto": len(descricao),
    }
    resultado.severidade = _classificar_severidade(resultado.score_risco)
    return resultado


# =============================================================================
# HEURÍSTICA 2 — Padrões em Contratos Públicos
# =============================================================================
def avaliar_padroes_contrato(contrato: dict) -> ResultadoHeuristica:
    """Detecta padrões suspeitos em contratos públicos."""
    resultado = ResultadoHeuristica()

    valor_original = float(contrato.get("valor_original", 0) or 0)
    valor_total = float(contrato.get("valor_total", 0) or 0)
    qtd_aditivos = int(contrato.get("qtd_aditivos", 0) or 0)
    prazo_dias = int(contrato.get("prazo_dias", 0) or 0)
    empresa_id = contrato.get("empresa_id")
    contratos_ano = int(contrato.get("contratos_mesma_empresa_ano", 0) or 0)
    objeto = (contrato.get("objeto", "") or "").lower()

    if valor_original > 0 and valor_total > valor_original * 1.25:
        resultado.heuristicas.append("aditivos_acima_25pct")
        resultado.score_risco += 20
        resultado.evidencia["aditivos_pct"] = round(
            (valor_total - valor_original) / valor_original * 100, 2
        )

    if qtd_aditivos >= 3:
        resultado.heuristicas.append("muitos_aditivos")
        resultado.score_risco += 10
        resultado.evidencia["qtd_aditivos"] = qtd_aditivos

    if 0 < prazo_dias < 15 and valor_original > 100_000:
        resultado.heuristicas.append("prazo_urgente_baixo_valor")
        resultado.score_risco += 12

    if contratos_ano >= 5:
        resultado.heuristicas.append("concentracao_contratos")
        resultado.score_risco += min(20, contratos_ano * 2)
        resultado.evidencia["contratos_mesma_empresa_ano"] = contratos_ano

    objetos_genericos = [
        "prestação de serviços", "serviços diversos", "fornecimento de materiais",
        "locação", "consultoria",
    ]
    if any(o in objeto for o in objetos_genericos) and valor_original > 500_000:
        resultado.heuristicas.append("objeto_generico_alto_valor")
        resultado.score_risco += 8

    if valor_original > 0 and valor_original == round(valor_original, -4):
        resultado.heuristicas.append("valor_arredondado")
        resultado.score_risco += 5

    resultado.score_risco = min(100, resultado.score_risco)
    resultado.evidencia["empresa_id"] = empresa_id
    resultado.evidencia["valor_original"] = valor_original
    resultado.evidencia["valor_total"] = valor_total
    resultado.severidade = _classificar_severidade(resultado.score_risco)
    return resultado


# =============================================================================
# HEURÍSTICA 3 — Análise de Fornecedor
# =============================================================================
def avaliar_fornecedor(fornecedor: dict) -> ResultadoHeuristica:
    """Avalia fornecedor buscando sinais de risco."""
    resultado = ResultadoHeuristica()

    tempo_aberta_meses = int(fornecedor.get("tempo_aberta_meses", 0) or 0)
    capital_social = float(fornecedor.get("capital_social", 0) or 0)
    maior_contrato = float(fornecedor.get("maior_contrato_valor", 0) or 0)
    socios_sancionados = int(fornecedor.get("socios_sancionados", 0) or 0)
    mesmo_endereco_outras = int(fornecedor.get("mesmo_endereco_outras", 0) or 0)
    socios_servidores = int(fornecedor.get("socios_servidores_publicos", 0) or 0)

    if socios_sancionados > 0:
        resultado.heuristicas.append("socios_sancionados")
        resultado.score_risco += 30

    if 0 < tempo_aberta_meses < 6 and maior_contrato > 500_000:
        resultado.heuristicas.append("empresa_recente_contrato_alto")
        resultado.score_risco += 20
        resultado.evidencia["tempo_aberta_meses"] = tempo_aberta_meses
        resultado.evidencia["maior_contrato"] = maior_contrato

    if capital_social > 0 and maior_contrato > capital_social * 50:
        resultado.heuristicas.append("capital_incompativel")
        resultado.score_risco += 15

    if mesmo_endereco_outras >= 3:
        resultado.heuristicas.append("mesmo_endereco_multiplas")
        resultado.score_risco += 18
        resultado.evidencia["mesmo_endereco_outras"] = mesmo_endereco_outras

    if socios_servidores > 0:
        resultado.heuristicas.append("socio_servidor_publico")
        resultado.score_risco += 25

    resultado.score_risco = min(100, resultado.score_risco)
    resultado.evidencia["capital_social"] = capital_social
    resultado.severidade = _classificar_severidade(resultado.score_risco)
    return resultado


# =============================================================================
# Catálogo
# =============================================================================
HEURISTICAS_DISPONIVEIS = {
    "texto_denuncia": {
        "nome": "Análise de Texto de Denúncia",
        "funcao": avaliar_texto_denuncia,
        "peso": 1,
        "descricao": "Detecta palavras-chave suspeitas e padrões em denúncias",
    },
    "contrato_publico": {
        "nome": "Padrões em Contratos Públicos",
        "funcao": avaliar_padroes_contrato,
        "peso": 2,
        "descricao": "Detecta aditivos excessivos, prazos urgentes, concentração",
    },
    "fornecedor": {
        "nome": "Análise de Fornecedor",
        "funcao": avaliar_fornecedor,
        "peso": 2,
        "descricao": "Detecta empresas com sinais de risco",
    },
}


def _classificar_severidade(score: int) -> str:
    if score >= 70:
        return "CRITICA"
    if score >= 50:
        return "ALTA"
    if score >= 25:
        return "MEDIA"
    return "BAIXA"
