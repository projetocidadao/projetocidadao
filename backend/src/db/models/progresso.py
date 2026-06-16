"""
Model de Progresso do Usuário em Cursos
"""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base


class Progresso(Base):
    __tablename__ = "progressos"
    __table_args__ = (
        UniqueConstraint("usuario_id", "curso_id", name="uq_progresso_usuario_curso"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False
    )
    curso_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cursos.id", ondelete="CASCADE"), nullable=False
    )

    percent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    concluido: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relacionamentos
    usuario = relationship("Usuario", back_populates="progressos")
    curso = relationship("Curso", back_populates="progressos")

    def __repr__(self) -> str:
        return f"<Progresso usuario={self.usuario_id} curso={self.curso_id} {self.percent}%>"
