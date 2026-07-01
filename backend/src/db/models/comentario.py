"""
Model de Comentário
Polimórfico — pode ser em denúncia, curso, etc.
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base


class TipoAlvo(str, enum.Enum):
    DENUNCIA = "denuncia"
    CURSO = "curso"
    AREA = "area"
    CASO_SUSPEITO = "caso_suspeito"


class Comentario(Base):
    __tablename__ = "comentarios"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    autor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False
    )
    texto: Mapped[str] = mapped_column(Text, nullable=False)

    # Polimorfismo
    tipo_alvo: Mapped[TipoAlvo] = mapped_column(
        Enum(TipoAlvo, name="tipo_alvo_enum"), nullable=False, index=True
    )
    alvo_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)

    # Resposta aninhada (thread)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("comentarios.id")
    )

    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relacionamentos
    autor = relationship("Usuario", back_populates="comentarios")
    denuncia = relationship(
        "Denuncia", back_populates="comentarios",
        primaryjoin="and_(Comentario.tipo_alvo=='denuncia', foreign(Comentario.alvo_id)==Denuncia.id)",
        viewonly=True,
    )
    respostas = relationship("Comentario", remote_side="Comentario.parent_id")

    def ___repr___(self) -> str:
        return f"<Comentario {self.tipo_alvo.value}:{self.alvo_id}>"
