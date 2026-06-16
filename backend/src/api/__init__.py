"""
Pacote api: routers FastAPI.
"""
from src.api import auth, users, areas, cursos, denuncias, comentarios, faros, votos, anexos
from src.api import admin_farejador, notificacoes

__all__ = [
    "auth", "users", "areas", "cursos",
    "denuncias", "comentarios", "faros", "votos", "anexos",
    "admin_farejador", "notificacoes",
]
