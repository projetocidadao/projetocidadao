"""
Pacote core: segurança, dependências, configurações transversais.
"""
from src.core.security import hash_senha, verificar_senha, criar_access_token, decodificar_token
from src.core.deps import (
    get_current_user,
    get_current_active_user,
    require_role,
    require_admin,
    require_moderator,
    require_avancado,
)

__all__ = [
    "hash_senha",
    "verificar_senha",
    "criar_access_token",
    "decodificar_token",
    "get_current_user",
    "get_current_active_user",
    "require_role",
    "require_admin",
    "require_moderator",
    "require_avancado",
]
