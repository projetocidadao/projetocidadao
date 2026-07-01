"""
Model: Voto
Voto de um usuário em uma denúncia (apoio ou contra).
"""
from sqlalchemy import ForeignKey, Integer, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin


class Voto(Base, TimestampMixin):
    __tablename__ = "votos"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False
    )
    denuncia_id: Mapped[int] = mapped_column(
        ForeignKey("denuncias.id", ondelete="CASCADE"), nullable=False
    )
    apoio: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    pontos: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    ___table_args___ = (
        UniqueConstraint("usuario_id", "denuncia_id", name="uq_voto_usuario_denuncia"),
    )

    usuario: Mapped["Usuario"] = relationship("Usuario", back_populates="votos")
    denuncia: Mapped["Denuncia"] = relationship("Denuncia", back_populates="votos_usuarios")

    def ___repr___(self) -> str:
        return f"<Voto usuario_id={self.usuario_id} denuncia_id={self.denuncia_id} apoio={self.apoio}>"
