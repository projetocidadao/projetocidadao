"""
Model: Curso
Cursos educacionais sobre transparência e fiscalização.
"""
from typing import List, Optional

from sqlalchemy import String, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin


class Curso(Base, TimestampMixin):
    __tablename__ = "cursos"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    descricao: Mapped[str] = mapped_column(String(1000), nullable=False)
    conteudo: Mapped[str] = mapped_column(Text, nullable=False)  # markdown

    # Metadados
    duracao_minutos: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    nivel: Mapped[str] = mapped_column(String(20), default="iniciante", nullable=False)
    publico_alvo: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Governança
    status: Mapped[str] = mapped_column(
        String(20), default="publicado", nullable=False
    )  # rascunho | em_aprovacao | publicado | arquivado
    autor_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )
    total_modulos: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    ordem: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Vínculo com área temática
    area_id: Mapped[int] = mapped_column(
        ForeignKey("areas.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Relationships
    area: Mapped["Area"] = relationship("Area", back_populates="cursos")
    progressos: Mapped[List["Progresso"]] = relationship(
        "Progresso", back_populates="curso", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Curso id={self.id} slug={self.slug}>"
