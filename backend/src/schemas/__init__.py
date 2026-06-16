"""
Schemas Pydantic (DTOs) — entrada e saída da API.
"""
from src.schemas.area import AreaBase, AreaCreate, AreaUpdate, AreaRead
from src.schemas.curso import CursoBase, CursoCreate, CursoUpdate, CursoRead
from src.schemas.usuario import (
    UsuarioBase, UsuarioCreate, UsuarioUpdate, UsuarioRead, UsuarioLogin, Token, TokenPayload
)
from src.schemas.denuncia import (
    DenunciaBase, DenunciaCreate, DenunciaUpdate, DenunciaRead
)
from src.schemas.comentario import (
    ComentarioBase, ComentarioCreate, ComentarioUpdate, ComentarioRead
)
from src.schemas.faro import FaroBase, FaroCreate, FaroUpdate, FaroRead
from src.schemas.voto import (
    VotoBase, VotoCreate, VotoUpdate, VotoRead, RankingItem, VotoStats
)
from src.schemas.anexo import (
    AnexoBase, AnexoCreate, AnexoRead, AnexoUpdate, UploadResponse, AnexoStats
)
from src.schemas.notificacao import (
    NotificacaoBase, NotificacaoCreate, NotificacaoRead, NotificacaoUpdate,
    NotificacaoStats, PreferenciasNotificacao, PreferenciasNotificacaoUpdate,
    TelegramLinkRequest, TelegramLinkResponse,
)

__all__ = [
    "AreaBase", "AreaCreate", "AreaUpdate", "AreaRead",
    "CursoBase", "CursoCreate", "CursoUpdate", "CursoRead",
    "UsuarioBase", "UsuarioCreate", "UsuarioUpdate", "UsuarioRead",
    "UsuarioLogin", "Token", "TokenPayload",
    "DenunciaBase", "DenunciaCreate", "DenunciaUpdate", "DenunciaRead",
    "ComentarioBase", "ComentarioCreate", "ComentarioUpdate", "ComentarioRead",
    "FaroBase", "FaroCreate", "FaroUpdate", "FaroRead",
    "VotoBase", "VotoCreate", "VotoUpdate", "VotoRead", "RankingItem", "VotoStats",
    "AnexoBase", "AnexoCreate", "AnexoRead", "AnexoUpdate", "UploadResponse", "AnexoStats",
    "NotificacaoBase", "NotificacaoCreate", "NotificacaoRead", "NotificacaoUpdate",
    "NotificacaoStats", "PreferenciasNotificacao", "PreferenciasNotificacaoUpdate",
    "TelegramLinkRequest", "TelegramLinkResponse",
]
