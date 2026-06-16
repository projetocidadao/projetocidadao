"""
Models do SQLAlchemy 2.0.

Importar este módulo registra todos os models na Base.metadata,
necessário para o Alembic gerar as migrations corretamente.
"""
from src.db.base import Base, TimestampMixin
from src.models.enums import (
    UserRole,
    StatusDenuncia,
    CategoriaDenuncia,
    TipoAnexo,
    TipoNotificacao,
    StatusFaro,
)
from src.models.usuario import Usuario
from src.models.area import Area
from src.models.curso import Curso
from src.models.denuncia import Denuncia
from src.models.anexo import Anexo
from src.models.comentario import Comentario
from src.models.progresso import Progresso
from src.models.voto import Voto
from src.models.faro import Faro
from src.models.notificacao import Notificacao

__all__ = [
    "Base",
    "TimestampMixin",
    "UserRole",
    "StatusDenuncia",
    "CategoriaDenuncia",
    "TipoAnexo",
    "TipoNotificacao",
    "StatusFaro",
    "Usuario",
    "Area",
    "Curso",
    "Denuncia",
    "Anexo",
    "Comentario",
    "Progresso",
    "Voto",
    "Faro",
    "Notificacao",
]
