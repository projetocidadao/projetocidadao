"""
Model de Comentario
"""
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base


class Comentario(Base):
    __tablename__ = "comentarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    conteudo: Mapped[str] = mapped_column(Text, nullable=False)
    autor_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id", ondelete="SET NULL"))
    denuncia_id: Mapped[int] = mapped_column(ForeignKey("denuncias.id", ondelete="CASCADE"), nullable=False, index=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("comentarios.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    autor = relationship("Usuario", back_populates="comentarios")
    denuncia = relationship("Denuncia", back_populates="comentarios")

    def __repr__(self) -> str:
        return f"<Comentario {self.id}>"
