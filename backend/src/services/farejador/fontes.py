"""
Catálogo de fontes de dados públicos usadas pelo Farejador.

Cada fonte define:
- Identificador único
- URL base da API pública
- Tipo de dados coletados
- Frequência de coleta
- Métodos de coleta
- Termos de uso / limites conhecidos
- Heurísticas aplicáveis

Fontes integradas:
- Portal da Transparência (CGU)
- TCU (Tribunal de Contas da União)
- DataSUS / DATASUS
- TSE (Tribunal Superior Eleitoral)
- contratos.gov.br
- ComprasNet / Compras.gov
- IBGE
- ANVISA
- ANATEL
- ANA (Agência Nacional de Águas)
- DNIT
- ANAC
- Diário Oficial da União
- Câmara dos Deputados (API de proposições)
- Senado Federal
- Portal de Dados Abertos
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional


class TipoFonte(str, Enum):
    LICITACAO = "licitacao"
    CONTRATO = "contrato"
    SERVIDOR = "servidor"
    PATRIMONIO = "patrimonio"
    SANCAO = "sancao"
    DESAPARECIDO = "desaparecido"
    CARTAO_CORPORATIVO = "cartao_corporativo"
    VIAGEM = "viagem"
    ELEITORAL = "eleitoral"
    SANEAMENTO = "saneamento"
    SAUDE = "saude"
    EDUCACAO = "educacao"
    OUTROS = "outros"


class StatusFonte(str, Enum):
    ATIVA = "ativa"
    EXPERIMENTAL = "experimental"
    DESABILITADA = "desabilitada"
    INDISPONIVEL = "indisponivel"


@dataclass
class Fonte:
    """Definição de uma fonte de dados."""
    id: str
    nome: str
    descricao: str
    tipo: TipoFonte
    url_base: str
    url_api: Optional[str] = None
    status: StatusFonte = StatusFonte.ATIVA
    autenticacao: bool = False
    rate_limit_per_min: int = 60
    escopo: str = "federal"  # federal, estadual, municipal
    orgao_responsavel: str = ""
    termos_uso_url: str = ""
    termos_busca: List[str] = field(default_factory=list)
    heuristicas_aplicaveis: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Catálogo de fontes
# =============================================================================
FONTES: List[Fonte] = [
    # -------------------------------------------------------------------------
    # PORTAL DA TRANSPARÊNCIA (CGU)
    # -------------------------------------------------------------------------
    Fonte(
        id="cgu_licitacoes",
        nome="CGU - Licitações",
        descricao="Licitações de órgãos federais",
        tipo=TipoFonte.LICITACAO,
        url_base="http://portaldatransparencia.gov.br",
        url_api="https://api.portaldatransparencia.gov.br/api-de-dados/licitacoes",
        status=StatusFonte.ATIVA,
        autenticacao=True,
        rate_limit_per_min=30,
        escopo="federal",
        orgao_responsavel="CGU",
        termos_uso_url="http://portaldatransparencia.gov.br/sobre/perguntas-frequentes",
        termos_busca=["dispensa", "inexigibilidade", "pregão", "concorrência"],
        heuristicas_aplicaveis=["valor_alto", "pouco_participantes", "fracionamento"],
    ),
    Fonte(
        id="cgu_contratos",
        nome="CGU - Contratos",
        descricao="Contratos firmados por órgãos federais",
        tipo=TipoFonte.CONTRATO,
        url_base="http://portaldatransparencia.gov.br",
        url_api="https://api.portaldatransparencia.gov.br/api-de-dados/contratos",
        status=StatusFonte.ATIVA,
        autenticacao=True,
        rate_limit_per_min=30,
        escopo="federal",
        orgao_responsavel="CGU",
        termos_busca=["contrato", "aditivo", "supressão"],
        heuristicas_aplicaveis=["valor_alto", "pagamento_atipico", "empresa_recem_criada"],
    ),
    Fonte(
        id="cgu_servidores",
        nome="CGU - Servidores Federais",
        descricao="Remuneração de servidores públicos federais",
        tipo=TipoFonte.SERVIDOR,
        url_base="http://portaldatransparencia.gov.br",
        url_api="https://api.portaldatransparencia.gov.br/api-de-dados/servidores",
        status=StatusFonte.ATIVA,
        autenticacao=True,
        rate_limit_per_min=30,
        escopo="federal",
        orgao_responsavel="CGU",
        heuristicas_aplicaveis=["conflito_interesse"],
    ),
    Fonte(
        id="cgu_sancoes",
        nome="CGU - CEIS / CNEP",
        descricao="Cadastros de empresas inidôneas e punidas",
        tipo=TipoFonte.SANCAO,
        url_base="http://portaldatransparencia.gov.br",
        url_api="https://api.portaldatransparencia.gov.br/api-de-dados/ceis",
        status=StatusFonte.ATIVA,
        autenticacao=True,
        rate_limit_per_min=30,
        escopo="federal",
        orgao_responsavel="CGU",
        heuristicas_aplicaveis=["empresa_sancionada"],
    ),
    Fonte(
        id="cgu_viagens",
        nome="CGU - Viagens a Serviço",
        descricao="Viagens oficiais de servidores",
        tipo=TipoFonte.VIAGEM,
        url_base="http://portaldatransparencia.gov.br",
        url_api="https://api.portaldatransparencia.gov.br/api-de-dados/viagens",
        status=StatusFonte.ATIVA,
        autenticacao=True,
        rate_limit_per_min=30,
        escopo="federal",
        orgao_responsavel="CGU",
        heuristicas_aplicaveis=["viagem_injustificada"],
    ),
    Fonte(
        id="cgu_cartao_corporativo",
        nome="CGU - Cartão Corporativo",
        descricao="Gastos com cartão corporativo do governo federal",
        tipo=TipoFonte.CARTAO_CORPORATIVO,
        url_base="http://portaldatransparencia.gov.br",
        url_api="https://api.portaldatransparencia.gov.br/api-de-dados/cartao-corporativo",
        status=StatusFonte.ATIVA,
        autenticacao=True,
        rate_limit_per_min=30,
        escopo="federal",
        orgao_responsavel="CGU",
        heuristicas_aplicaveis=["gasto_atipico", "saque_alto"],
    ),
    Fonte(
        id="cgu_patrimonio",
        nome="CGU - Patrimônio de Agentes",
        descricao="Patrimônio declarado por agentes públicos",
        tipo=TipoFonte.PATRIMONIO,
        url_base="http://portaldatransparencia.gov.br",
        url_api="https://api.portaldatransparencia.gov.br/api-de-dados/patrimonio",
        status=StatusFonte.ATIVA,
        autenticacao=True,
        rate_limit_per_min=30,
        escopo="federal",
        orgao_responsavel="CGU",
        heuristicas_aplicaveis=["patrimonio_incompativel"],
    ),

    # -------------------------------------------------------------------------
    # TCU
    # -------------------------------------------------------------------------
    Fonte(
        id="tcu_acordaos",
        nome="TCU - Acórdãos",
        descricao="Acórdãos do Tribunal de Contas da União",
        tipo=TipoFonte.CONTRATO,
        url_base="https://portal.tcu.gov.br",
        url_api="https://portal.tcu.gov.br/data.json",
        status=StatusFonte.ATIVA,
        autenticacao=False,
        rate_limit_per_min=120,
        escopo="federal",
        orgao_responsavel="TCU",
        termos_busca=["sobrepreço", "superfaturamento", "irregularidade"],
        heuristicas_aplicaveis=["sobrepreco", "fracionamento"],
    ),
    Fonte(
        id="tcu_pessoal",
        nome="TCU - Auditoria de Pessoal",
        descricao="Decisões sobre pessoal do serviço público",
        tipo=TipoFonte.SERVIDOR,
        url_base="https://portal.tcu.gov.br",
        status=StatusFonte.ATIVA,
        escopo="federal",
        orgao_responsavel="TCU",
    ),

    # -------------------------------------------------------------------------
    # COMPRAS GOVERNAMENTAIS
    # -------------------------------------------------------------------------
    Fonte(
        id="comprasnet_pregoes",
        nome="ComprasNet - Pregões",
        descricao="Pregões eletrônicos do governo federal",
        tipo=TipoFonte.LICITACAO,
        url_base="https://www.gov.br/compras",
        url_api="https://compras.dados.gov.br/pregoes/v1/pregoes.json",
        status=StatusFonte.ATIVA,
        autenticacao=False,
        rate_limit_per_min=60,
        escopo="federal",
        orgao_responsavel="ME / Compras.gov",
        termos_busca=["pregão eletrônico", "pregão presencial"],
        heuristicas_aplicaveis=["pouco_participantes", "valor_alto"],
    ),
    Fonte(
        id="contratos_gov",
        nome="Contratos.gov.br",
        descricao="Contratos do governo federal",
        tipo=TipoFonte.CONTRATO,
        url_base="https://contratos.compras.gov.br",
        url_api="https://contratos.compras.gov.br/api/v1/contratos",
        status=StatusFonte.ATIVA,
        autenticacao=False,
        rate_limit_per_min=60,
        escopo="federal",
        orgao_responsavel="ME / Compras.gov",
        heuristicas_aplicaveis=["valor_alto", "pagamento_atipico"],
    ),

    # -------------------------------------------------------------------------
    # TSE
    # -------------------------------------------------------------------------
    Fonte(
        id="tse_candidatos",
        nome="TSE - Candidatos",
        descricao="Dados de candidatos e prestações de contas eleitorais",
        tipo=TipoFonte.ELEITORAL,
        url_base="https://www.tse.jus.br",
        url_api="https://dadosabertos.tse.jus.br/api/3/action",
        status=StatusFonte.ATIVA,
        autenticacao=False,
        rate_limit_per_min=120,
        escopo="federal",
        orgao_responsavel="TSE",
        heuristicas_aplicaveis=["doacao_acima_limite", "doacao_frigideira"],
    ),
    Fonte(
        id="tse_bens",
        nome="TSE - Bens Declarados",
        descricao="Bens declarados por candidatos e eleitos",
        tipo=TipoFonte.PATRIMONIO,
        url_base="https://www.tse.jus.br",
        status=StatusFonte.ATIVA,
        escopo="federal",
        orgao_responsavel="TSE",
        heuristicas_aplicaveis=["patrimonio_incompativel"],
    ),

    # -------------------------------------------------------------------------
    # SAÚDE
    # -------------------------------------------------------------------------
    Fonte(
        id="datasus_epidemiologico",
        nome="DataSUS - Epidemiológico",
        descricao="Dados epidemiológicos do SUS",
        tipo=TipoFonte.SAUDE,
        url_base="https://datasus.saude.gov.br",
        url_api="https://opendatasus.saude.gov.br",
        status=StatusFonte.ATIVA,
        autenticacao=False,
        rate_limit_per_min=60,
        escopo="federal",
        orgao_responsavel="Ministério da Saúde",
        heuristicas_aplicaveis=["subnotificacao", "irregularidade_saude"],
    ),

    # -------------------------------------------------------------------------
    # LEGISLATIVO
    # -------------------------------------------------------------------------
    Fonte(
        id="camara_proposicoes",
        nome="Câmara dos Deputados - Proposições",
        descricao="Projetos de lei e outras proposições",
        tipo=TipoFonte.OUTROS,
        url_base="https://www.camara.leg.br",
        url_api="https://dadosabertos.camara.leg.br/api/v2",
        status=StatusFonte.ATIVA,
        autenticacao=False,
        rate_limit_per_min=300,
        escopo="federal",
        orgao_responsavel="Câmara dos Deputados",
    ),
    Fonte(
        id="senado_proposicoes",
        nome="Senado - Proposições",
        descricao="Matérias legislativas do Senado",
        tipo=TipoFonte.OUTROS,
        url_base="https://www12.senado.leg.br",
        url_api="https://legis.senado.leg.br/dadosabertos",
        status=StatusFonte.ATIVA,
        autenticacao=False,
        rate_limit_per_min=120,
        escopo="federal",
        orgao_responsavel="Senado Federal",
    ),

    # -------------------------------------------------------------------------
    # DIÁRIO OFICIAL
    # -------------------------------------------------------------------------
    Fonte(
        id="dou_federal",
        nome="DOU - Diário Oficial da União",
        descricao="Diário Oficial da União",
        tipo=TipoFonte.OUTROS,
        url_base="https://www.in.gov.br",
        url_api="https://queridodiario.ok.org.br/api/gazettes",
        status=StatusFonte.ATIVA,
        autenticacao=False,
        rate_limit_per_min=60,
        escopo="federal",
        orgao_responsavel="Imprensa Nacional",
        heuristicas_aplicaveis=["nomeacao_suspeita", "sem_concurso"],
    ),

    # -------------------------------------------------------------------------
    # IBGE / ESTATÍSTICAS
    # -------------------------------------------------------------------------
    Fonte(
        id="ibge_indicadores",
        nome="IBGE - Indicadores Sociais",
        descricao="Indicadores sociais e demográficos",
        tipo=TipoFonte.OUTROS,
        url_base="https://www.ibge.gov.br",
        url_api="https://servicodados.ibge.gov.br/api/v1",
        status=StatusFonte.ATIVA,
        autenticacao=False,
        rate_limit_per_min=120,
        escopo="federal",
        orgao_responsavel="IBGE",
    ),

    # -------------------------------------------------------------------------
    # INFRAESTRUTURA
    # -------------------------------------------------------------------------
    Fonte(
        id="dnit_obras",
        nome="DNIT - Obras Rodoviárias",
        descricao="Obras de infraestrutura rodoviária",
        tipo=TipoFonte.CONTRATO,
        url_base="https://www.gov.br/dnit",
        status=StatusFonte.ATIVA,
        escopo="federal",
        orgao_responsavel="DNIT",
        heuristicas_aplicaveis=["valor_alto", "atraso_obra"],
    ),
    Fonte(
        id="anat_telecom",
        nome="ANATEL - Telecomunicações",
        descricao="Dados do setor de telecomunicações",
        tipo=TipoFonte.OUTROS,
        url_base="https://www.gov.br/anatel",
        status=StatusFonte.ATIVA,
        escopo="federal",
        orgao_responsavel="ANATEL",
    ),

    # -------------------------------------------------------------------------
    # REGULADORAS
    # -------------------------------------------------------------------------
    Fonte(
        id="ana_recursos_hidricos",
        nome="ANA - Recursos Hídricos",
        descricao="Dados de recursos hídricos e saneamento",
        tipo=TipoFonte.SANEAMENTO,
        url_base="https://www.gov.br/ana",
        url_api="https://www.ana.gov.br/snirh/snirh-1",
        status=StatusFonte.ATIVA,
        autenticacao=False,
        rate_limit_per_min=60,
        escopo="federal",
        orgao_responsavel="ANA",
        heuristicas_aplicaveis=["poluicao_irregular", "outorga_vencida"],
    ),
    Fonte(
        id="anvisa_sancoes",
        nome="ANVISA - Sanções",
        descricao="Sanções aplicadas a empresas do setor regulado",
        tipo=TipoFonte.SANCAO,
        url_base="https://www.gov.br/anvisa",
        status=StatusFonte.ATIVA,
        escopo="federal",
        orgao_responsavel="ANVISA",
    ),

    # -------------------------------------------------------------------------
    # PORTAIS ESTADUAIS (exemplos, facilmente extensíveis)
    # -------------------------------------------------------------------------
    Fonte(
        id="transparencia_sp",
        nome="Portal da Transparência SP",
        descricao="Portal estadual de São Paulo",
        tipo=TipoFonte.OUTROS,
        url_base="https://www.transparencia.sp.gov.br",
        status=StatusFonte.EXPERIMENTAL,
        escopo="estadual",
        orgao_responsavel="Governo do Estado de SP",
    ),
    Fonte(
        id="transparencia_rj",
        nome="Portal da Transparência RJ",
        descricao="Portal estadual do Rio de Janeiro",
        tipo=TipoFonte.OUTROS,
        url_base="http://www.transparencia.rj.gov.br",
        status=StatusFonte.EXPERIMENTAL,
        escopo="estadual",
        orgao_responsavel="Governo do Estado do RJ",
    ),

    # -------------------------------------------------------------------------
    # LEI DE ACESSO À INFORMAÇÃO
    # -------------------------------------------------------------------------
    Fonte(
        id="esic_federal",
        nome="e-SIC Federal",
        descricao="Pedidos de informação via LAI",
        tipo=TipoFonte.OUTROS,
        url_base="https://esic.cgu.gov.br",
        status=StatusFonte.EXPERIMENTAL,
        escopo="federal",
        orgao_responsavel="CGU",
    ),
]


def get_fontes_ativas() -> List[Fonte]:
    """Retorna apenas fontes ativas."""
    return [f for f in FONTES if f.status == StatusFonte.ATIVA]


def get_fontes_por_tipo(tipo: TipoFonte) -> List[Fonte]:
    """Retorna fontes de um tipo específico."""
    return [f for f in get_fontes_ativas() if f.tipo == tipo]


def get_fonte_por_id(fonte_id: str) -> Optional[Fonte]:
    """Busca uma fonte pelo ID."""
    for f in FONTES:
        if f.id == fonte_id:
            return f
    return None


def estatisticas_fontes() -> Dict[str, int]:
    """Retorna estatísticas do catálogo de fontes."""
    return {
        "total": len(FONTES),
        "ativas": len(get_fontes_ativas()),
        "federais": sum(1 for f in FONTES if f.escopo == "federal"),
        "estaduais": sum(1 for f in FONTES if f.escopo == "estadual"),
        "municipais": sum(1 for f in FONTES if f.escopo == "municipal"),
        "experimental": sum(1 for f in FONTES if f.status == StatusFonte.EXPERIMENTAL),
    }
