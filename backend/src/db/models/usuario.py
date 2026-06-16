"""
Model de Usuário
Sistema de pontos pioneiros (3-2-1) + roles
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base


class Role(str, enum.Enum):
    """Níveis de participação no Projeto Cidadão"""
    CIDADAO = "cidadao"          # Nível 1 — apenas consome
    AVANCADO = "avancado"        # Nível 2 — pode comentar, sugerir
    PIONEIRO = "pioneiro"        # Nível 3 — pode criar áreas/cursos
    MODERADOR = "moderador"      # Nível 4 — pode aprovar contribuições
    ADMIN = "admin"              # Nível 5 — controle total


class Usuario(Base):
    __tablename__ = "usuarios"

    # Identificação
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # Perfil
    avatar_url: Mapped[str | None] = mapped_column(String(500))
    biografia: Mapped[str | None] = mapped_column(String(500))
    cidade: Mapped[str | None] = mapped_column(String(100))
    estado: Mapped[str | None] = mapped_column(String(2))

    # Gamificação (sistema de pontos pioneiros)
    pontos: Mapped[int] = mapped_column(Integer, default=0, index=True)
    role: Mapped[Role] = mapped_column(
        Enum(Role, name="role_enum"), default=Role.CIDADAO, nullable=False
    )
    # Período de incubação — só pode criar conteúdo após N dias
    data_primeira_contribuicao: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    apto_a_criar: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # LGPD
    consentimento_lgpd: Mapped[bool] = mapped_column(Boolean, default=False)
    data_consentimento: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Auditoria
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relacionamentos
    denuncias = relationship("Denuncia", back_populates="autor", cascade="all, delete-orphan")
    comentarios = relationship("Comentario", back_populates="autor", cascade="all, delete-orphan")
    progressos = relationship("Progresso", back_populates="usuario", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Usuario {self.nome} ({self.role.value}, {self.pontos}pts)>"
