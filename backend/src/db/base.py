"""
Base declarativa do SQLAlchemy
Importa todos os models para que o Alembic consiga detectá-los
"""
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData

# Convenção de nomes para migrations mais limpas
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Classe base para todos os models"""
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


# Importa todos os models para registro no metadata
# (essencial para o Alembic autogenerate)
from src.db.models.usuario import Usuario  # noqa: E402,F401
from src.db.models.area import Area  # noqa: E402,F401
from src.db.models.curso import Curso, Modulo  # noqa: E402,F401
from src.db.models.progresso import Progresso  # noqa: E402,F401
from src.db.models.denuncia import Denuncia, Anexo  # noqa: E402,F401
from src.db.models.comentario import Comentario  # noqa: E402,F401
from src.db.models.farejador import CasoSuspeito, Heuristica  # noqa: E402,F401
