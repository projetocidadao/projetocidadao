"""
Model de Notificação — alertas in-app e via Telegram.
"""
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Integer, String, DateTime, Boolean, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from src.db.base import Base
from src.db.models.enums import TipoNotificacao, CanalNotificacao, StatusNotificacao


class Notificacao(Base):
    """
    Notificação para um usuário.
    Pode ser entregue por múltiplos canais (in-app, Telegram, email).
    """
    __tablename__ = "notificacoes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Destinatário
    usuario_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Conteúdo
    tipo: Mapped[TipoNotificacao] = mapped_column(
        SQLEnum(TipoNotificacao, name="tipo_notificacao"), nullable=False, index=True
    )
    canal: Mapped[CanalNotificacao] = mapped_column(
        SQLEnum(CanalNotificacao, name="canal_notificacao"), nullable=False
    )
    status: Mapped[StatusNotificacao] = mapped_column(
        SQLEnum(StatusNotificacao, name="status_notificacao"),
        default=StatusNotificacao.PENDENTE,
        nullable=False,
        index=True,
    )

    titulo: Mapped[str] = mapped_column(String(255), nullable=False)
    mensagem: Mapped[str] = mapped_column(Text, nullable=False)

    # Contexto (opcional)
    referencia_tipo: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # denuncia, faro, comentario
    referencia_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Dados extras (flex)
    dados_extras: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Telegram
    telegram_message_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Controle
    lida: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    lida_em: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    tentativas: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    erro_ultimo: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    enviado_em: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relacionamento
    usuario = relationship("Usuario", back_populates="notificacoes", foreign_keys=[usuario_id])

    def ___repr___(self) -> str:
        return f"<Notificacao(id={self.id}, tipo={self.tipo}, status={self.status})>"
