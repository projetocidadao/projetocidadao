"""
Model: Comentario
Comentários em denúncias (e respostas em thread).
"""
from typing import List, Optional

from sqlalchemy import String, Text, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin


class Comentario(Base, TimestampMixin):
    __tablename__ = "comentarios"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    texto: Mapped[str] = mapped_column(Text, nullable=False)
    editado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Thread (comentários aninhados)
    parent_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("comentarios.id", ondelete="CASCADE"), nullable=True, index=True
    )

    # Foreign keys
    autor_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True
    )
    denuncia_id: Mapped[int] = mapped_column(
        ForeignKey("denuncias.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Relationships
    autor: Mapped["Usuario"] = relationship("Usuario", back_populates="comentarios")
    denuncia: Mapped["Denuncia"] = relationship("Denuncia", back_populates="comentarios")
    parent: Mapped[Optional["Comentario"]] = relationship(
        "Comentario", remote_side="Comentario.id", back_populates="respostas"
    )
    respostas: Mapped[List["Comentario"]] = relationship(
        "Comentario", back_populates="parent", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Comentario id={self.id} autor_id={self.autor_id}>"
