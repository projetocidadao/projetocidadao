"""
Model de Notificacao
"""
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base


class Notificacao(Base):
    __tablename__ = "notificacoes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    tipo: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    conteudo: Mapped[str | None] = mapped_column(Text)
    link: Mapped[str | None] = mapped_column(String(500))
    lida: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    usuario = relationship("Usuario", back_populates="notificacoes")

    def __repr__(self) -> str:
        return f"<Notificacao {self.titulo[:30]}>"
