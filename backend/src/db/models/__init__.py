"""
Models do banco de dados

Este __init__.py importa TODOS os models para garantir que sejam
registrados em Base.metadata antes de qualquer operacao do Alembic
ou SQLAlchemy.
"""
from src.db.models.usuario import Usuario  # noqa: F401
from src.db.models.area import Area  # noqa: F401
from src.db.models.curso import Curso  # noqa: F401
from src.db.models.denuncia import Denuncia, Anexo  # noqa: F401
from src.db.models.comentario import Comentario  # noqa: F401
from src.db.models.faro import Faro  # noqa: F401
from src.db.models.voto import Voto  # noqa: F401
from src.db.models.notificacao import Notificacao  # noqa: F401
from src.db.models.progresso import Progresso  # noqa: F401
from src.db.models.enums import UserRole, StatusDenuncia, StatusFaro  # noqa: F401

__all__ = [
    "Usuario", "Area", "Curso", "Denuncia", "Anexo", "Comentario",
    "Faro", "Voto", "Notificacao", "Progresso",
    "UserRole", "StatusDenuncia", "StatusFaro",
]
