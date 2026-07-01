"""Reexporta todos os models para o Alembic."""
from src.db.base import Base  # noqa: F401
import src.db.models  # noqa: F401,F403
