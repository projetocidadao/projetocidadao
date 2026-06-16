"""
Model: Denuncia
Denúncias enviadas pelos cidadãos.
"""
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    String, Text, Integer, Float, Boolean, ForeignKey, DateTime, Enum as SAEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin
from src.models.enums import CategoriaDenuncia, StatusDenuncia


class Denuncia(Base, TimestampMixin):
    __tablename__ = "denuncias"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Conteúdo
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    categoria: Mapped[CategoriaDenuncia] = mapped_column(
        SAEnum(CategoriaDenuncia, name="categoria_denuncia"),
        nullable=False,
        index=True,
    )

    # Status e privacidade
    status: Mapped[StatusDenuncia] = mapped_column(
        SAEnum(StatusDenuncia, name="status_denuncia"),
        default=StatusDenuncia.AGUARDANDO,
        nullable=False,
        index=True,
    )
    anonima: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    publica: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Geolocalização
    lat: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    lng: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    endereco: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    municipio: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    estado: Mapped[Optional[str]] = mapped_column(String(2), nullable=True, index=True)
    cep: Mapped[Optional[str]] = mapped_column(String(10), nullable=True, index=True)

    # Contexto
    data_fato: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    valor_dano_estimado: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    envolvidos: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Encaminhamento automático
    canal_destino: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    codigo_rastreio: Mapped[str] = mapped_column(
        String(20), unique=True, index=True, nullable=False
    )

    # Engajamento
    votos: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    visualizacoes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Foreign keys
    autor_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True, index=True
    )
    area_id: Mapped[int] = mapped_column(
        ForeignKey("areas.id", ondelete="RESTRICT"), nullable=False, index=True
    )

    # Relationships
    autor: Mapped[Optional["Usuario"]] = relationship(
        "Usuario", back_populates="denuncias", foreign_keys=[autor_id]
    )
    area: Mapped["Area"] = relationship("Area", back_populates="denuncias")
    anexos: Mapped[List["Anexo"]] = relationship(
        "Anexo", back_populates="denuncia", cascade="all, delete-orphan"
    )
    comentarios: Mapped[List["Comentario"]] = relationship(
        "Comentario", back_populates="denuncia", cascade="all, delete-orphan"
    )
    votos_usuarios: Mapped[List["Voto"]] = relationship(
        "Voto", back_populates="denuncia", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Denuncia id={self.id} status={self.status.value} categoria={self.categoria.value}>"
