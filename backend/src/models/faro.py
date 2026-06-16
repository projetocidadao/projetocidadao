"""
Model: Faro
Sinalização do Farejador de Corrupção — caso suspeito detectado.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, Integer, ForeignKey, DateTime, Enum as SAEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base, TimestampMixin
from src.models.enums import StatusFaro


class Faro(Base, TimestampMixin):
    __tablename__ = "faros"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Identificação da entidade sinalizada
    tipo_entidade: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    referencia_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    entidade_nome: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Heurísticas acionadas e evidências
    heuristicas: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    evidencia: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    # Score e classificação
    score_risco: Mapped[int] = mapped_column(Integer, default=0, nullable=False, index=True)
    severidade: Mapped[str] = mapped_column(
        String(20), default="MEDIA", nullable=False, index=True
    )  # BAIXA | MEDIA | ALTA | CRITICA

    # Status e desfecho
    status: Mapped[StatusFaro] = mapped_column(
        SAEnum(StatusFaro, name="status_faro"),
        default=StatusFaro.NOVO,
        nullable=False,
        index=True,
    )
    data_deteccao: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    data_investigacao: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    desfecho: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Vínculo opcional com denúncia
    denuncia_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("denuncias.id", ondelete="SET NULL"), nullable=True
    )

    def __repr__(self) -> str:
        return f"<Faro id={self.id} score={self.score_risco} status={self.status.value}>"
