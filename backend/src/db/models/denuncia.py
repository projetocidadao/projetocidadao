"""
Models de Denuncia e Anexo
"""
from datetime import datetime
from sqlalchemy import (
    BigInteger, Boolean, DateTime, Enum, Float, ForeignKey, Integer,
    String, Text, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base
from src.db.models.enums import StatusDenuncia, TipoAnexo


class Denuncia(Base):
    __tablename__  = "denuncias"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    categoria: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )
    status: Mapped[StatusDenuncia] = mapped_column(
        Enum(
            StatusDenuncia,
            name="status_denuncia_enum",
            create_type=False,
            values_callable=lambda x: [e.value for e in x],
        ),
        default=StatusDenuncia.AGUARDANDO, nullable=False, index=True,
    )
    canal_destino: Mapped[str | None] = mapped_column(
        String(100), index=True
    )
    codigo_rastreio: Mapped[str] = mapped_column(
        String(20), unique=True, index=True, nullable=False
    )
    anonima: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    publica: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    autor_id: Mapped[int | None] = mapped_column(
        ForeignKey("usuarios.id", ondelete="SET NULL"), index=True
    )
    area_id: Mapped[int] = mapped_column(
        ForeignKey("areas.id"), nullable=False, index=True
    )
    lat: Mapped[float | None] = mapped_column(Float)
    lng: Mapped[float | None] = mapped_column(Float)
    endereco: Mapped[str | None] = mapped_column(String(500))
    municipio: Mapped[str | None] = mapped_column(String(100), index=True)
    estado: Mapped[str | None] = mapped_column(String(2), index=True)
    cep: Mapped[str | None] = mapped_column(String(10), index=True)
    data_fato: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    valor_dano_estimado: Mapped[float | None] = mapped_column(Float)
    envolvidos: Mapped[str | None] = mapped_column(Text)
    votos: Mapped[int] = mapped_column(Integer, default=0, nullable=False, index=True)
    visualizacoes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    autor = relationship("Usuario", back_populates="denuncias")
    area = relationship("Area", back_populates="denuncias")
    anexos = relationship("Anexo", back_populates="denuncia", cascade="all, delete-orphan")
    votos_usuarios = relationship("Voto", back_populates="denuncia", cascade="all, delete-orphan")
    comentarios = relationship("Comentario", back_populates="denuncia", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Denuncia {self.titulo[:50]} ({self.status.value})>"


class Anexo(Base):
    __tablename__  = "anexos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    url: Mapped[str] = mapped_column(String(1000), nullable=False)
    nome_original: Mapped[str | None] = mapped_column(String(255))
    mime_type: Mapped[str | None] = mapped_column(String(100))
    tamanho_bytes: Mapped[int | None] = mapped_column(BigInteger)
    tipo: Mapped[TipoAnexo] = mapped_column(
        Enum(
            TipoAnexo,
            name="tipo_anexo",
            create_type=False,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
    )
    hash_sha256: Mapped[str | None] = mapped_column(String(64), index=True)
    descricao: Mapped[str | None] = mapped_column(String(300))
    denuncia_id: Mapped[int] = mapped_column(
        ForeignKey("denuncias.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    denuncia = relationship("Denuncia", back_populates="anexos")

    def __repr__(self) -> str:
        return f"<Anexo {self.url} ({self.tipo.value})>"
