"""
Model de Area Temetica
"""
from datetime import datetime
from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base


class Area(Base):
    __tablename__ = "areas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    descricao: Mapped[str] = mapped_column(String(1000), nullable=False)
    icone: Mapped[str] = mapped_column(String(50), nullable=False)
    cor: Mapped[str | None] = mapped_column(String(7))
    artigo_cf: Mapped[str | None] = mapped_column(String(50))
    ordem: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    denuncias = relationship("Denuncia", back_populates="area")
    cursos = relationship("Curso", back_populates="area")

    def __repr__(self) -> str:
        return f"<Area {self.nome}>"
