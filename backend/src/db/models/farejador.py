"""
Models do Farejador de Corrupção
Casos suspeitos detectados automaticamente + heurísticas acionadas
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime, Enum, Float, ForeignKey, Integer, String, Text, func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base


class StatusCaso(str, enum.Enum):
    NOVO = "novo"
    EM_ANALISE = "em_analise"
    INVESTIGADO = "investigado"
    CONFIRMADO = "confirmado"
    FALSO_POSITIVO = "falso_positivo"
    ARQUIVADO = "arquivado"


class TipoCaso(str, enum.Enum):
    LICITACAO = "licitacao"
    CONTRATO = "contrato"
    FOLHA = "folha"
    TRANSFERENCIA = "transferencia"
    CRUZAMENTO = "cruzamento"
    EMPRESA = "empresa"
    PESSOA = "pessoa"


class CasoSuspeito(Base):
    __tablename__ = "casos_suspeitos"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tipo: Mapped[TipoCaso] = mapped_column(
        Enum(TipoCaso, name="tipo_caso_enum"), nullable=False, index=True
    )
    referencia_id: Mapped[str | None] = mapped_column(String(200), index=True)  # ID original
    titulo: Mapped[str] = mapped_column(String(500), nullable=False)
    descricao: Mapped[str] = mapped_column(Text, nullable=False)

    # Score de risco (0-100)
    score_risco: Mapped[float] = mapped_column(Float, default=0.0, index=True)
    severidade: Mapped[str] = mapped_column(String(20), default="BAIXA", index=True)

    # Dados completos em JSON (evidências, contexto, etc.)
    dados: Mapped[dict] = mapped_column(JSONB, default=dict)

    # Status
    status: Mapped[StatusCaso] = mapped_column(
        Enum(StatusCaso, name="status_caso_enum"),
        default=StatusCaso.NOVO,
        nullable=False,
        index=True,
    )

    # Vinculação opcional a uma denúncia
    denuncia_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("denuncias.id")
    )

    # Auditoria
    detectado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relacionamentos
    heuristicas = relationship(
        "Heuristica", back_populates="caso", cascade="all, delete-orphan"
    )

    def ___repr___(self) -> str:
        return f"<CasoSuspeito {self.tipo.value} score={self.score_risco}>"


class Heuristica(Base):
    """Heurísticas que foram acionadas em um caso"""
    __tablename__ = "heuristicas"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    caso_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("casos_suspeitos.id", ondelete="CASCADE"), nullable=False
    )
    codigo: Mapped[str] = mapped_column(String(10), nullable=False)  # H1, H2, etc.
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    peso: Mapped[float] = mapped_column(Float, default=1.0)
    evidencia: Mapped[dict] = mapped_column(JSONB, default=dict)

    detectado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relacionamentos
    caso = relationship("CasoSuspeito", back_populates="heuristicas")

    def ___repr___(self) -> str:
        return f"<Heuristica {self.codigo} - {self.nome[:30]}>"
