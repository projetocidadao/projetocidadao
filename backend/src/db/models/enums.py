"""
Enums do dominio - alinhados ao schema do banco
"""
import enum


class UserRole(str, enum.Enum):
    CIDADAO = "cidadao"
    AVANCADO = "avancado"
    MODERADOR = "moderador"
    ADMIN = "admin"


class StatusDenuncia(str, enum.Enum):
    AGUARDANDO = "aguardando"
    EM_ANALISE = "em_analise"
    EM_ANDAMENTO = "em_andamento"
    RESOLVIDA = "resolvida"
    REJEITADA = "rejeitada"


class CanalDenuncia(str, enum.Enum):
    CGU = "cgu"
    MINISTERIO_PUBLICO = "ministerio_publico"
    TCU = "tcu"
    TCE = "tce"
    OUVIDORIA_FEDERAL = "ouvidoria_federal"
    OUVIDORIA_ESTADUAL = "ouvidoria_estadual"
    OUVIDORIA_MUNICIPAL = "ouvidoria_municipal"
    DEFENSORIA = "defensoria"
    IBAMA = "ibama"
    POLICIA_FEDERAL = "policia_federal"
    OUTRO = "outro"


class CategoriaDenuncia(str, enum.Enum):
    SAUDE = "saude"
    EDUCACAO = "educacao"
    ALIMENTACAO = "alimentacao"
    TRANSPORTE = "transporte"
    SEGURANCA = "seguranca"
    SANEAMENTO = "saneamento"
    FINANCAS = "financas"
    MEIO_AMBIENTE = "meio_ambiente"
    CULTURA = "cultura"
    OUTRO = "outro"


class StatusFaro(str, enum.Enum):
    NOVO = "novo"
    EM_ANALISE = "em_analise"
    INVESTIGADO = "investigado"
    CONFIRMADO = "confirmado"
    ARQUIVADO = "arquivado"


class SeveridadeFaro(str, enum.Enum):
    BAIXA = "BAIXA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"
    CRITICA = "CRITICA"


class TipoAnexo(str, enum.Enum):
    IMAGEM = "IMAGEM"
    VIDEO = "VIDEO"
    AUDIO = "AUDIO"
    DOCUMENTO = "DOCUMENTO"
    PLANILHA = "PLANILHA"
    OUTRO = "OUTRO"


class TipoNotificacao(str, enum.Enum):
    NOVA_DENUNCIA = "nova_denuncia"
    FARO_CRITICO = "faro_critico"
    FARO_NOVO = "faro_novo"
    DENUNCIA_STATUS = "denuncia_status"
    COMENTARIO_RESPOSTA = "comentario_resposta"
    VOTO_RECEBIDO = "voto_recebido"
    NIVEL_UP = "nivel_up"
    CURSO_CONCLUIDO = "curso_concluido"
    SISTEMA = "sistema"


class StatusCurso(str, enum.Enum):
    INCUBACAO = "incubacao"
    EM_APROVACAO = "em_aprovacao"
    PUBLICADO = "publicado"
    REJEITADO = "rejeitado"
    ARQUIVADO = "arquivado"


class CanalNotificacao(str, enum.Enum):
    IN_APP = "in_app"
    EMAIL = "email"
    PUSH = "push"
    SMS = "sms"


class StatusNotificacao(str, enum.Enum):
    PENDENTE = "pendente"
    ENVIADA = "enviada"
    ENTREGUE = "entregue"
    LIDA = "lida"
    FALHADA = "falhada"
