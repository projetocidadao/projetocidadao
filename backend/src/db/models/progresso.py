"""
Model de Progresso de Curso
"""
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, Float, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base


class Progresso(Base):
    __tablename__ = "progressos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    curso_id: Mapped[int] = mapped_column(ForeignKey("cursos.id", ondelete="CASCADE"), nullable=False, index=True)
    percentual: Mapped[float] = mapped_column(Float, default=0.0)
    concluido: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    usuario = relationship("Usuario", back_populates="progressos")
    curso = relationship("Curso", back_populates="progressos")

    def __repr__(self) -> str:
        return f"<Progresso {self.percentual}%>"
