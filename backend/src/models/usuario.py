"""
Model de Usuário.
"""
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import Integer, String, DateTime, Boolean, Enum as SQLEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base
from src.models.enums import UserRole


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    cpf: Mapped[Optional[str]] = mapped_column(String(14), unique=True, nullable=True, index=True)
    telefone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Gamificação
    pontos: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    nivel: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Permissões
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole, name="user_role"), default=UserRole.CIDADAO, nullable=False
    )
    verificado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Telegram
    telegram_id: Mapped[Optional[int]] = mapped_column(
        Integer, unique=True, nullable=True, index=True
    )
    telegram_username: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    # Preferências de notificação
    preferencias_notificacao: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # Estrutura esperada:
    # {
    #   "in_app": {"faro_critico": true, ...},
    #   "telegram": {"faro_critico": true, ...},
    #   "email": {"faro_critico": false, ...}
    # }

    # Localização
    estado: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    municipio: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Avatar
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relacionamentos
    denuncias = relationship("Denuncia", back_populates="autor", foreign_keys="Denuncia.autor_id")
    comentarios = relationship("Comentario", back_populates="autor", foreign_keys="Comentario.autor_id")
    notificacoes = relationship("Notificacao", back_populates="usuario", cascade="all, delete-orphan", foreign_keys="Notificacao.usuario_id")

    def __repr__(self) -> str:
        return f"<Usuario(id={self.id}, email={self.email}, role={self.role})>"
