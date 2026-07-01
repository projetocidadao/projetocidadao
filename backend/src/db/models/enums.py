"""
Enums do domínio.
"""
import enum


class UserRole(str, enum.Enum):
    CIDADAO = "cidadao"
    AVANCADO = "avancado"
    MODERADOR = "moderador"
    ADMIN = "admin"


class CategoriaDenuncia(str, enum.Enum):
    SAUDE = "saude"
    EDUCACAO = "educacao"
    ALIMENTACAO = "alimentacao"
    TRANSPORTE = "transporte"
    SEGURANCA = "seguranca"
    SANEAMENTO = "saneamento"
    FINANCAS = "financas"
    MEIO_AMBIENTE = "meio-ambiente"
    CULTURA = "cultura"
    OUTRO = "outro"


class StatusDenuncia(str, enum.Enum):
    NOVA = "nova"
    EM_ANALISE = "em_analise"
    VERIFICADA = "verificada"
    EM_INVESTIGACAO = "em_investigacao"
    RESOLVIDA = "resolvida"
    REJEITADA = "rejeitada"
    ARQUIVADA = "arquivada"


class StatusFaro(str, enum.Enum):
    NOVO = "novo"
    EM_REVISAO = "em_revisao"
    CONFIRMADO = "confirmado"
    FALSO_POSITIVO = "falso_positivo"
    ENCAMINHADO = "encaminhado"
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


class CanalNotificacao(str, enum.Enum):
    IN_APP = "in_app"
    TELEGRAM = "telegram"
    EMAIL = "email"


class StatusNotificacao(str, enum.Enum):
    PENDENTE = "pendente"
    ENVIADA = "enviada"
    FALHOU = "falhou"
    CANCELADA = "cancelada"
