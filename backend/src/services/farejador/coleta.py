"""
Worker de coleta automática do farejador.

Coleta dados de fontes públicas em intervalos regulares,
processa-os com as heurísticas, e gera faros/alertas.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import uuid4

import httpx
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .fontes import Fonte, get_fontes_ativas, get_fonte_por_id
from .heuristicas import analisar_texto, calcular_score
from .scoring import analisar_completo


logger = logging.getLogger(__name__)


# =============================================================================
# Coletor base
# =============================================================================
class ColetorBase:
    """Classe base para coletores de fontes específicas."""

    fonte_id: str = ""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.fonte = get_fonte_por_id(self.fonte_id)
        if not self.fonte:
            raise ValueError(f"Fonte '{self.fonte_id}' não encontrada no catálogo")

    async def coletar(self, **kwargs) -> List[Dict[str, Any]]:
        """Coleta dados. Deve ser sobrescrito."""
        raise NotImplementedError

    async def executar(self, **kwargs) -> Dict[str, Any]:
        """Executa a coleta e retorna estatísticas."""
        inicio = datetime.utcnow()
        try:
            dados = await self.coletar(**kwargs)
            processados = 0
            faros_criados = 0
            for item in dados:
                if await self._processar_item(item):
                    faros_criados += 1
                processados += 1
            return {
                "fonte": self.fonte_id,
                "status": "ok",
                "coletados": len(dados),
                "processados": processados,
                "faros_criados": faros_criados,
                "duracao": (datetime.utcnow() - inicio).total_seconds(),
            }
        except Exception as e:
            logger.exception(f"Erro coletando {self.fonte_id}")
            return {
                "fonte": self.fonte_id,
                "status": "erro",
                "erro": str(e),
                "duracao": (datetime.utcnow() - inicio).total_seconds(),
            }

    async def _processar_item(self, item: Dict[str, Any]) -> bool:
        """Processa um item coletado e gera faro se relevante."""
        texto = item.get("texto_analise") or item.get("descricao") or item.get("objeto") or ""
        if not texto or len(texto) < 20:
            return False

        analise = analisar_completo(texto, contexto={
            "fonte_confiavel": True,
            "historico_orgao": item.get("historico_orgao", 0),
        })

        # Só cria faro se score relevante
        if analise.score_ajustado < 30:
            return False

        return await self._criar_faro(item, analise)

    async def _criar_faro(self, item: Dict[str, Any], analise) -> bool:
        """Persiste o faro no banco. Implementação padrão."""
        # Importação tardia pra evitar ciclos
        try:
            from src.models.faro import Faro
            from src.models.enums import NivelRisco
        except ImportError:
            logger.warning("Modelo Faro não disponível — pulando persistência")
            return False

        faro = Faro(
            id=str(uuid4()),
            fonte=self.fonte_id,
            titulo=item.get("titulo") or item.get("objeto") or "Faro automático",
            descricao=analise.texto_original[:2000],
            score=analise.score_ajustado,
            nivel_risco=_mapear_nivel(analise.nivel_risco),
            indicios=[i.heuristica.tipo for i in analise.indicios_ponderados],
            metadata={
                "score_bruto": analise.score_bruto,
                "agravantes": analise.fatores_agravantes,
                "atenuantes": analise.fatores_atenuantes,
                "recomendacao": analise.recomendacao,
                "dados_originais": item,
            },
            dados_externos=item,
            url_fonte=item.get("url"),
            data_publicacao=item.get("data_publicacao") or datetime.utcnow(),
        )
        self.session.add(faro)
        await self.session.commit()
        return True


def _mapear_nivel(nivel: str) -> str:
    """Mapeia nível do scoring para enum NivelRisco."""
    return {
        "critico": "critico",
        "alto": "alto",
        "moderado": "moderado",
        "baixo": "baixo",
        "minimo": "informativo",
    }.get(nivel, "informativo")


# =============================================================================
# Coletores específicos
# =============================================================================
class ColetorPortalTransparencia(ColetorBase):
    """Coleta do Portal da Transparência (CGU)."""

    fonte_id = "cgu_contratos"

    async def coletar(self, dias_atras: int = 7, **kwargs) -> List[Dict[str, Any]]:
        # Implementação de exemplo — em produção usa a API real
        # com token de autenticação
        api_key = kwargs.get("api_key")
        if not api_key:
            logger.info("Coletor CGU: api_key não configurada — pulando")
            return []

        url = self.fonte.url_api
        if not url:
            return []

        itens: List[Dict[str, Any]] = []
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.get(
                    url,
                    params={"dataInicial": (datetime.utcnow() - timedelta(days=dias_atras)).strftime("%d/%m/%Y")},
                    headers={"Accept": "application/json", "chave-api": api_key},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    for item in data if isinstance(data, list) else data.get("data", []):
                        itens.append({
                            "titulo": item.get("nomeOrgao") or item.get("objeto") or "",
                            "descricao": item.get("objeto") or item.get("descricao") or "",
                            "valor": item.get("valorInicial") or item.get("valor"),
                            "data_publicacao": item.get("dataPublicacao"),
                            "url": item.get("linkDetalhamento"),
                        })
            except Exception as e:
                logger.exception(f"Erro coletando CGU: {e}")
        return itens


class ColetorTCU(ColetorBase):
    """Coleta acórdãos do TCU."""

    fonte_id = "tcu_acordaos"

    async def coletar(self, **kwargs) -> List[Dict[str, Any]]:
        # O portal do TCU tem RSS / dados abertos
        # Aqui só esboçamos a estrutura
        url = "https://portal.tcu.gov.br/data.json"
        itens: List[Dict[str, Any]] = []
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    # Adaptar ao schema real
                    for item in data.get("items", [])[:50]:
                        itens.append({
                            "titulo": item.get("title", ""),
                            "descricao": item.get("summary", item.get("content", "")),
                            "url": item.get("link") or item.get("url"),
                            "data_publicacao": item.get("datePublished"),
                        })
            except Exception as e:
                logger.exception(f"Erro coletando TCU: {e}")
        return itens


class ColetorComprasNet(ColetorBase):
    """Coleta de pregões do ComprasNet."""

    fonte_id = "comprasnet_pregoes"

    async def coletar(self, **kwargs) -> List[Dict[str, Any]]:
        url = "https://compras.dados.gov.br/pregoes/v1/pregoes.json"
        itens: List[Dict[str, Any]] = []
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.get(url, params={"offset": 0, "limit": 100})
                if resp.status_code == 200:
                    data = resp.json()
                    for item in data.get("_embedded", {}).get("pregoes", []):
                        itens.append({
                            "titulo": item.get("objeto", ""),
                            "descricao": item.get("descricao", item.get("objeto", "")),
                            "valor": item.get("valor_estimado"),
                            "data_publicacao": item.get("data_abertura"),
                            "url": item.get("link_detalhe"),
                        })
            except Exception as e:
                logger.exception(f"Erro coletando ComprasNet: {e}")
        return itens


class ColetorTSE(ColetorBase):
    """Coleta dados do TSE (candidatos e bens)."""

    fonte_id = "tse_bens"

    async def coletar(self, **kwargs) -> List[Dict[str, Any]]:
        # O TSE tem API em dadosabertos.tse.jus.br
        # Para implementação completa, ver:
        # https://dadosabertos.tse.jus.br/swagger-ui/index.html
        logger.info("Coletor TSE: stub — implementar com chamadas reais")
        return []


# =============================================================================
# Orquestrador
# =============================================================================
COLETORES = {
    "cgu_contratos": ColetorPortalTransparencia,
    "tcu_acordaos": ColetorTCU,
    "comprasnet_pregoes": ColetorComprasNet,
    "tse_bens": ColetorTSE,
}


async def executar_coleta(
    session: AsyncSession,
    fonte_id: Optional[str] = None,
    **kwargs,
) -> Dict[str, Any]:
    """
    Executa a coleta de uma fonte específica ou de todas as ativas.
    """
    if fonte_id:
        coletor_class = COLETORES.get(fonte_id)
        if not coletor_class:
            return {"status": "erro", "erro": f"Coletor '{fonte_id}' não implementado"}
        coletor = coletor_class(session)
        return await coletor.executar(**kwargs)

    # Todas as fontes
    resultados = []
    for fid, coletor_class in COLETORES.items():
        try:
            coletor = coletor_class(session)
            resultado = await coletor.executar(**kwargs)
            resultados.append(resultado)
        except Exception as e:
            logger.exception(f"Erro no coletor {fid}")
            resultados.append({"fonte": fid, "status": "erro", "erro": str(e)})

    return {
        "status": "ok",
        "total_fontes": len(resultados),
        "resultados": resultados,
    }


# =============================================================================
# Job de scheduler (chamado pelo APScheduler)
# =============================================================================
async def job_coleta_periodica():
    """Job executado periodicamente pelo scheduler."""
    from src.db.session import async_session

    async with async_session() as session:
        try:
            resultado = await executar_coleta(session)
            logger.info(f"Coleta periódica: {resultado['total_fontes']} fontes processadas")
            return resultado
        except Exception as e:
            logger.exception(f"Erro na coleta periódica: {e}")
            return {"status": "erro", "erro": str(e)}
