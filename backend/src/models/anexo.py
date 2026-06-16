"""
Model: Anexo
Arquivos anexados a uma denúncia (foto, vídeo, PDF, áudio).
"""
from typing import Optional

from sqlalchemy import String, Integer, BigInteger, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin
from src.models.enums import TipoAnexo


class Anexo(Base, TimestampMixin):
    __tablename__ = "anexos"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    url: Mapped[str] = mapped_column(String(1000), nullable=False)
    nome_original: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    mime_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    tamanho_bytes: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    tipo: Mapped[TipoAnexo] = mapped_column(
        SAEnum(TipoAnexo, name="tipo_anexo"), nullable=False
    )
    hash_sha256: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)

    denuncia_id: Mapped[int] = mapped_column(
        ForeignKey("denuncias.id", ondelete="CASCADE"), nullable=False, index=True
    )
    denuncia: Mapped["Denuncia"] = relationship("Denuncia", back_populates="anexos")

    def __repr__(self) -> str:
        return f"<Anexo id={self.id} tipo={self.tipo.value}>"
