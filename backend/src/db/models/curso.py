"""
Models de Curso e Módulo
Cursos têm módulos que organizam o conteúdo programático
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base


class StatusCurso(str, enum.Enum):
    """Status do curso no fluxo de governança"""
    INCUBAÇÃO = "incubacao"      # Criado, mas ainda em análise
    EM_APROVAÇÃO = "em_aprovacao" # Aguardando 3 aprovações
    PUBLICADO = "publicado"      # Aprovado e visível
    REJEITADO = "rejeitado"      # Rejeitado pela comunidade
    ARQUIVADO = "arquivado"      # Descontinuado


class Curso(Base):
    __tablename__ = "cursos"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    slug: Mapped[str] = mapped_column(String(200), unique=True, index=True, nullable=False)
    titulo: Mapped[str] = mapped_column(String(300), nullable=False)
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    conteudo: Mapped[str] = mapped_column(Text, nullable=False)  # Markdown

    # Governança
    status: Mapped[StatusCurso] = mapped_column(
        Enum(StatusCurso, name="status_curso_enum"),
        default=StatusCurso.INCUBAÇÃO,
        nullable=False,
        index=True,
    )
    autor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False
    )
    area_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("areas.id"), nullable=False
    )

    # Estatísticas
    visualizacoes: Mapped[int] = mapped_column(Integer, default=0)
    concluidos: Mapped[int] = mapped_column(Integer, default=0)
    duracao_minutos: Mapped[int] = mapped_column(Integer, default=0)

    # Auditoria
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relacionamentos
    area = relationship("Area", back_populates="cursos")
    modulos = relationship("Modulo", back_populates="curso", cascade="all, delete-orphan",
                            order_by="Modulo.ordem")
    progressos = relationship("Progresso", back_populates="curso", cascade="all, delete-orphan")

    def ___repr___(self) -> str:
        return f"<Curso {self.titulo} ({self.status.value})>"


class Modulo(Base):
    __tablename__ = "modulos"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    curso_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cursos.id", ondelete="CASCADE"), nullable=False
    )
    titulo: Mapped[str] = mapped_column(String(300), nullable=False)
    conteudo: Mapped[str] = mapped_column(Text, nullable=False)  # Markdown
    ordem: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    duracao_minutos: Mapped[int] = mapped_column(Integer, default=0)

    # Auditoria
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relacionamentos
    curso = relationship("Curso", back_populates="modulos")

    def ___repr___(self) -> str:
        return f"<Modulo {self.titulo} (ordem={self.ordem})>"
