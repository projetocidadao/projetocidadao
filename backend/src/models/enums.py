"""
Enums do projeto.
Definidos em um único local para serem reutilizados por models e schemas.
"""
import enum


class UserRole(str, enum.Enum):
    """Papéis de usuário no sistema."""
    CIDADAO = "cidadao"
    AVANCADO = "avancado"  # pode aprovar denúncias/cursos
    MODERADOR = "moderador"  # pode moderar comentários
    ADMIN = "admin"  # acesso total


class StatusDenuncia(str, enum.Enum):
    """Status de uma denúncia no fluxo."""
    AGUARDANDO = "aguardando"
    EM_ANALISE = "em_analise"
    EM_ANDAMENTO = "em_andamento"
    RESOLVIDA = "resolvida"
    REJEITADA = "rejeitada"


class CategoriaDenuncia(str, enum.Enum):
    """Categorias de denúncia (vinculadas a uma área temática)."""
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


class TipoAnexo(str, enum.Enum):
    """Tipos de arquivo que podem ser anexados."""
    FOTO = "foto"
    VIDEO = "video"
    PDF = "pdf"
    AUDIO = "audio"
    OUTRO = "outro"


class TipoNotificacao(str, enum.Enum):
    """Tipos de notificação."""
    DENUNCIA_CRIADA = "denuncia_criada"
    DENUNCIA_ATUALIZADA = "denuncia_atualizada"
    COMENTARIO_NOVO = "comentario_novo"
    CURSO_CONCLUIDO = "curso_concluido"
    FAREJADOR_ALERTA = "farejador_alerta"
    SISTEMA = "sistema"


class StatusFaro(str, enum.Enum):
    """Status de um sinal de farejador (caso suspeito detectado)."""
    NOVO = "novo"
    EM_ANALISE = "em_analise"
    INVESTIGADO = "investigado"
    ARQUIVADO = "arquivado"
    CONFIRMADO = "confirmado"
