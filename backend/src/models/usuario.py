"""
Model: Usuario
Cidadãos cadastrados na plataforma.
"""
from datetime import datetime
from typing import List, Optional

from sqlalchemy import String, Boolean, DateTime, Integer, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin
from src.models.enums import UserRole


class Usuario(Base, TimestampMixin):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, name="user_role"),
        default=UserRole.CIDADAO,
        nullable=False,
        index=True,
    )

    # Gamificação
    pontos: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    nivel: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Perfil
    bio: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    cidade: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    estado: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Controle
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    verificado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ultimo_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    denuncias: Mapped[List["Denuncia"]] = relationship(
        "Denuncia", back_populates="autor", foreign_keys="Denuncia.autor_id"
    )
    comentarios: Mapped[List["Comentario"]] = relationship(
        "Comentario", back_populates="autor"
    )
    progressos: Mapped[List["Progresso"]] = relationship(
        "Progresso", back_populates="usuario"
    )
    votos: Mapped[List["Voto"]] = relationship(
        "Voto", back_populates="usuario"
    )
    notificacoes: Mapped[List["Notificacao"]] = relationship(
        "Notificacao", back_populates="usuario", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Usuario id={self.id} email={self.email} role={self.role.value}>"
