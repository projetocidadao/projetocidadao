"""
Farejador de Corrupção — pacote principal.

Componentes:
- heuristicas: 25+ padrões de detecção (regex)
- scoring: sistema de pontuação com multiplicadores contextuais
- fontes: catálogo de 22 fontes de dados públicos
- coleta: workers de coleta automática
"""
from .heuristicas import (
    analisar_texto,
    detectar_padroes_suspeitos,
    calcular_score,
    classificar_score,
    cor_por_severidade,
    HeuristicaResultado,
    SCORE_TETO,
)
from .scoring import (
    analisar_completo,
    aplicar_multiplicadores,
    detectar_fatores_agravantes,
    detectar_fatores_atenuantes,
    gerar_recomendacao,
    ranking_indicios,
    AnaliseCompleta,
    IndicioPonderado,
)
from .fontes import (
    Fonte,
    FONTES,
    get_fontes_ativas,
    get_fontes_por_tipo,
    get_fonte_por_id,
    estatisticas_fontes,
    TipoFonte,
    StatusFonte,
)
from .coleta import (
    executar_coleta,
    job_coleta_periodica,
    ColetorBase,
    COLETORES,
)


__all__ = [
    # Heurísticas
    "analisar_texto",
    "detectar_padroes_suspeitos",
    "calcular_score",
    "classificar_score",
    "cor_por_severidade",
    "HeuristicaResultado",
    "SCORE_TETO",
    # Scoring
    "analisar_completo",
    "aplicar_multiplicadores",
    "detectar_fatores_agravantes",
    "detectar_fatores_atenuantes",
    "gerar_recomendacao",
    "ranking_indicios",
    "AnaliseCompleta",
    "IndicioPonderado",
    # Fontes
    "Fonte",
    "FONTES",
    "get_fontes_ativas",
    "get_fontes_por_tipo",
    "get_fonte_por_id",
    "estatisticas_fontes",
    "TipoFonte",
    "StatusFonte",
    # Coleta
    "executar_coleta",
    "job_coleta_periodica",
    "ColetorBase",
    "COLETORES",
]
