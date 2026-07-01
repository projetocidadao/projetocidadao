"""
Models do banco de dados
"""
from src.db.models.usuario import Usuario
from src.db.models.area import Area
from src.db.models.curso import Curso, Modulo
from src.db.models.progresso import Progresso
from src.db.models.denuncia import Denuncia, Anexo
from src.db.models.comentario import Comentario
from src.db.models.farejador import CasoSuspeito, Heuristica
from src.db.models.faro import Faro
from src.db.models.voto import Voto
from src.db.models.notificacao import Notificacao

__all__ = [
    "Usuario",
    "Area",
    "Curso",
    "Modulo",
    "Progresso",
    "Denuncia",
    "Anexo",
    "Comentario",
    "CasoSuspeito",
    "Heuristica",
]
