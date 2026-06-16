"""
Models do domínio.
"""
from src.models.usuario import Usuario
from src.models.area import Area
from src.models.curso import Curso
from src.models.denuncia import Denuncia
from src.models.comentario import Comentario
from src.models.faro import Faro
from src.models.anexo import Anexo
from src.models.voto import Voto
from src.models.notificacao import Notificacao

__all__ = [
    "Usuario", "Area", "Curso", "Denuncia",
    "Comentario", "Faro", "Anexo", "Voto", "Notificacao",
]
