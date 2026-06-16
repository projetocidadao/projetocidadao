"""
Model: Notificacao
Notificações enviadas aos usuários.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, Boolean, ForeignKey, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin
from src.models.enums import TipoNotificacao


class Notificacao(Base, TimestampMixin):
    __tablename__ = "notificacoes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    mensagem: Mapped[str] = mapped_column(Text, nullable=False)
    tipo: Mapped[TipoNotificacao] = mapped_column(
        SAEnum(TipoNotificacao, name="tipo_notificacao"), nullable=False
    )
    lida: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    data_leitura: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Link interno para a entidade relacionada (denúncia, curso, etc)
    link: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True
    )
    usuario: Mapped["Usuario"] = relationship("Usuario", back_populates="notificacoes")

    def __repr__(self) -> str:
        return f"<Notificacao id={self.id} tipo={self.tipo.value} lida={self.lida}>"
