"""
Model de Faro (alerta de cidadania)
"""
from datetime import datetime
from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSON

from src.db.base import Base
from src.db.models.enums import StatusFaro, SeveridadeFaro


class Faro(Base):
    __tablename__  = "faros"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tipo_entidade: Mapped[str] = mapped_column(String(30), nullable=False)
    referencia_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    entidade_nome: Mapped[str | None] = mapped_column(String(255))
    heuristicas: Mapped[dict] = mapped_column(JSON, default=list, nullable=False)
    evidencia: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    score_risco: Mapped[int] = mapped_column(Integer, default=0, nullable=False, index=True)
    severidade: Mapped[SeveridadeFaro] = mapped_column(
        Enum(
            SeveridadeFaro,
            name="severidade_faro",
            create_type=False,
            values_callable=lambda x: [e.value for e in x],
        ),
        default=SeveridadeFaro.MEDIA, nullable=False, index=True
    )
    status: Mapped[StatusFaro] = mapped_column(
        Enum(
            StatusFaro,
            name="status_faro",
            create_type=False,
            values_callable=lambda x: [e.value for e in x],
        ),
        default=StatusFaro.NOVO, nullable=False, index=True
    )
    data_deteccao: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    data_investigacao: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    desfecho: Mapped[str | None] = mapped_column(Text)
    denuncia_id: Mapped[int | None] = mapped_column(
        ForeignKey("denuncias.id", ondelete="SET NULL")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<Faro {self.tipo_entidade} score={self.score_risco}>"
