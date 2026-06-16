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
from src.core.storage import (
    calcular_hash_sha256,
    detectar_mime,
    mime_para_tipo,
    gerar_chave_arquivo,
    validar_arquivo,
    salvar_arquivo,
    gerar_url_publica,
    deletar_arquivo,
    abrir_arquivo_local,
    MIME_ALLOWED,
)

__all__ = [
    "hash_senha", "verificar_senha", "criar_access_token", "decodificar_token",
    "get_current_user", "get_current_active_user", "require_role",
    "require_admin", "require_moderator", "require_avancado",
    "calcular_hash_sha256", "detectar_mime", "mime_para_tipo",
    "gerar_chave_arquivo", "validar_arquivo", "salvar_arquivo",
    "gerar_url_publica", "deletar_arquivo", "abrir_arquivo_local", "MIME_ALLOWED",
]
