"""
Model de Usuario
"""
from datetime import datetime
from sqlalchemy import Boolean, DateTime, Enum, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base
from src.db.models.enums import UserRole


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role", create_type=False, values_callable=lambda x: [e.value for e in x]),
        default=UserRole.CIDADAO, nullable=False, index=True,
    )
    biografia: Mapped[str | None] = mapped_column(Text)
    cidade: Mapped[str | None] = mapped_column(String(100))
    estado: Mapped[str | None] = mapped_column(String(2))
    avatar_url: Mapped[str | None] = mapped_column(String(500))
    pontos: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    nivel: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    verificado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    apto_a_criar: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    consentimento_lgpd: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    data_consentimento: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    ultimo_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    data_primeira_contribuicao: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    denuncias = relationship("Denuncia", back_populates="autor")
    comentarios = relationship("Comentario", back_populates="autor")
    votos = relationship("Voto", back_populates="usuario")
    progressos = relationship("Progresso", back_populates="usuario")
    notificacoes = relationship("Notificacao", back_populates="usuario")

    def __repr__(self) -> str:
        return f"<Usuario {self.email}>"
