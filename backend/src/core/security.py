"""
Funções de segurança: hash de senha e JWT.
"""
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from src.db.config import settings


# Contexto de hash de senha (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_senha(senha: str) -> str:
    """Gera hash bcrypt da senha."""
    return pwd_context.hash(senha)


def verificar_senha(senha: str, senha_hash: str) -> bool:
    """Verifica se a senha corresponde ao hash."""
    return pwd_context.verify(senha, senha_hash)


def criar_access_token(
    subject: str | int,
    role: str,
    expires_delta: Optional[timedelta] = None,
    extra: Optional[dict[str, Any]] = None,
) -> str:
    """
    Cria um JWT.
    subject: identificador (geralmente o user id)
    role: papel do usuário (cidadao, avancado, moderador, admin)
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.jwt_expires_minutes
        )

    payload: dict[str, Any] = {
        "sub": str(subject),
        "role": role,
        "iat": int(datetime.now(timezone.utc).timestamp()),
        "exp": int(expire.timestamp()),
    }
    if extra:
        payload.update(extra)

    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decodificar_token(token: str) -> dict[str, Any]:
    """
    Decodifica e valida um JWT. Retorna o payload.
    Lança JWTError se inválido ou expirado.
    """
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
