"""
Models de Denúncia e Anexo
Denúncias podem ser anônimas, georreferenciadas e ter anexos
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, Text, func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base


class StatusDenuncia(str, enum.Enum):
    AGUARDANDO = "aguardando"
    EM_ANALISE = "em_analise"
    EM_ANDAMENTO = "em_andamento"
    RESOLVIDA = "resolvida"
    REJEITADA = "rejeitada"
    ARQUIVADA = "arquivada"


class CanalDenuncia(str, enum.Enum):
    """Canal para o qual a denúncia foi roteada"""
    CGU = "cgu"
    MINISTERIO_PUBLICO = "ministerio_publico"
    TCU = "tcu"
    TCE = "tce"
    OUVIDORIA_FEDERAL = "ouvidoria_federal"
    OUVIDORIA_ESTADUAL = "ouvidoria_estadual"
    OUVIDORIA_MUNICIPAL = "ouvidoria_municipal"
    DEFENSORIA = "defensoria"
    IBAMA = "ibama"
    POLICIA_FEDERAL = "policia_federal"
    OUTRO = "outro"


class Denuncia(Base):
    __tablename__ = "denuncias"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    titulo: Mapped[str] = mapped_column(String(300), nullable=False)
    descricao: Mapped[str] = mapped_column(Text, nullable=False)

    # Categoria (espelha as áreas temáticas + extras)
    categoria: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    area_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("areas.id"), nullable=False, index=True
    )

    # Status e canal
    status: Mapped[StatusDenuncia] = mapped_column(
        Enum(StatusDenuncia, name="status_denuncia_enum"),
        default=StatusDenuncia.AGUARDANDO,
        nullable=False,
        index=True,
    )
    canal_destino: Mapped[CanalDenuncia | None] = mapped_column(
        Enum(CanalDenuncia, name="canal_denuncia_enum"), index=True
    )
    codigo_rastreio: Mapped[str] = mapped_column(
        String(20), unique=True, index=True, nullable=False
    )

    # Anonimato e autoria
    anonima: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    autor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), index=True
    )

    # Localização (georreferenciamento opcional)
    lat: Mapped[float | None] = mapped_column(Float)
    lng: Mapped[float | None] = mapped_column(Float)
    endereco: Mapped[str | None] = mapped_column(String(500))
    municipio: Mapped[str | None] = mapped_column(String(100), index=True)
    estado: Mapped[str | None] = mapped_column(String(2), index=True)

    # Contexto
    data_fato: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    valor_dano_estimado: Mapped[float | None] = mapped_column(Float)

    # Engajamento
    votos: Mapped[int] = mapped_column(Integer, default=0, index=True)
    visualizacoes: Mapped[int] = mapped_column(Integer, default=0)

    # Resposta do poder público
    resposta_oficial: Mapped[str | None] = mapped_column(Text)
    data_resposta: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Auditoria
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relacionamentos
    autor = relationship("Usuario", back_populates="denuncias")
    area = relationship("Area", back_populates="denuncias")
    anexos = relationship("Anexo", back_populates="denuncia", cascade="all, delete-orphan")
    comentarios = relationship("Comentario", back_populates="denuncia", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Denuncia {self.titulo[:50]} ({self.status.value})>"


class Anexo(Base):
    __tablename__ = "anexos"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    denuncia_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("denuncias.id", ondelete="CASCADE"), nullable=False
    )
    url: Mapped[str] = mapped_column(String(1000), nullable=False)
    tipo: Mapped[str] = mapped_column(String(50), nullable=False)  # foto, video, pdf, audio
    tamanho_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    hash_sha256: Mapped[str | None] = mapped_column(String(64))  # integridade
    descricao: Mapped[str | None] = mapped_column(String(300))

    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relacionamentos
    denuncia = relationship("Denuncia", back_populates="anexos")

    def __repr__(self) -> str:
        return f"<Anexo {self.tipo} ({self.tamanho_bytes} bytes)>"
