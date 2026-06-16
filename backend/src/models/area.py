"""
Model: Area (Área Temática)
Ex.: Saúde, Educação, Transporte, Segurança, etc.
"""
from typing import List, Optional

from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin


class Area(Base, TimestampMixin):
    __tablename__ = "areas"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    descricao: Mapped[str] = mapped_column(String(1000), nullable=False)
    icone: Mapped[str] = mapped_column(String(50), nullable=False)  # emoji
    cor: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)  # hex

    # Hierarquia (Art. 6º da CF/88)
    artigo_cf: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    ordem: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    ativo: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Relationships
    cursos: Mapped[List["Curso"]] = relationship(
        "Curso", back_populates="area", cascade="all, delete-orphan"
    )
    denuncias: Mapped[List["Denuncia"]] = relationship(
        "Denuncia", back_populates="area"
    )

    def __repr__(self) -> str:
        return f"<Area id={self.id} slug={self.slug}>"
