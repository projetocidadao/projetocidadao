"""
Farejador de Corrupção — workers e heurísticas automatizadas.

Detecta sinais de risco em:
- Denúncias (texto, palavras-chave, padrões)
- Contratos públicos (valores, vencedores, aditivos)
- Fornecedores (sanções, vínculos)
"""
from src.farejador.heuristicas import (
    ResultadoHeuristica,
    avaliar_texto_denuncia,
    avaliar_padroes_contrato,
    avaliar_fornecedor,
    HEURISTICAS_DISPONIVEIS,
)
from src.farejador.worker import (
    executar_farejador,
    varrer_denuncias_recentes,
    varrer_contratos_publicos,
)
from src.farejador.scheduler import (
    iniciar_scheduler,
    parar_scheduler,
    status_scheduler,
)

__all__ = [
    "ResultadoHeuristica",
    "avaliar_texto_denuncia", "avaliar_padroes_contrato", "avaliar_fornecedor",
    "HEURISTICAS_DISPONIVEIS",
    "executar_farejador", "varrer_denuncias_recentes", "varrer_contratos_publicos",
    "iniciar_scheduler", "parar_scheduler", "status_scheduler",
]
