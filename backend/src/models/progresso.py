"""
Model: Progresso
Progresso de um usuário em um curso.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, Integer, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin


class Progresso(Base, TimestampMixin):
    __tablename__ = "progressos"
    __table_args__ = (
        UniqueConstraint("usuario_id", "curso_id", name="uq_progresso_usuario_curso"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True
    )
    curso_id: Mapped[int] = mapped_column(
        ForeignKey("cursos.id", ondelete="CASCADE"), nullable=False, index=True
    )
    percentual: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    concluido: Mapped[bool] = mapped_column(default=False, nullable=False)
    data_conclusao: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    pontos_ganhos: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    usuario: Mapped["Usuario"] = relationship("Usuario", back_populates="progressos")
    curso: Mapped["Curso"] = relationship("Curso", back_populates="progressos")

    def __repr__(self) -> str:
        return f"<Progresso usuario_id={self.usuario_id} curso_id={self.curso_id} {self.percentual}%>"
