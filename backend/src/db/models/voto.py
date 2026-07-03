"""
Model de Voto
"""
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base


class Voto(Base):
    __tablename__ = "votos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    denuncia_id: Mapped[int] = mapped_column(ForeignKey("denuncias.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    usuario = relationship("Usuario", back_populates="votos")
    denuncia = relationship("Denuncia", back_populates="votos_usuarios")

    def __repr__(self) -> str:
        return f"<Voto {self.id}>"
