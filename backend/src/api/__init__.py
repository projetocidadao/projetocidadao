"""
Pacote api: routers FastAPI.
"""
from src.api import auth, users, areas, cursos, denuncias, comentarios, faros, votos

__all__ = ["auth", "users", "areas", "cursos", "denuncias", "comentarios", "faros", "votos"]
