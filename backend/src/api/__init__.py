"""
Pacote api: routers FastAPI.
"""
from src.api import auth, users, areas, cursos, denuncias, comentarios, faros

__all__ = ["auth", "users", "areas", "cursos", "denuncias", "comentarios", "faros"]
