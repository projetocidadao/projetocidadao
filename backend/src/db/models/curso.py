"""
Model de Curso
"""
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base


class Curso(Base):
    __tablename__ = "cursos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    descricao: Mapped[str] = mapped_column(String(1000), nullable=False)
    conteudo: Mapped[str] = mapped_column(Text, nullable=False)
    duracao_minutos: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
    nivel: Mapped[str] = mapped_column(String(20), nullable=False, default="iniciante")
    publico_alvo: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="publicado", index=True)
    autor_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id", ondelete="SET NULL"))
    total_modulos: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    ordem: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    area_id: Mapped[int] = mapped_column(ForeignKey("areas.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    area = relationship("Area", back_populates="cursos")
    progressos = relationship("Progresso", back_populates="curso")
    autor = relationship("Usuario", foreign_keys=[autor_id])

    def __repr__(self) -> str:
        return f"<Curso {self.titulo}>"
