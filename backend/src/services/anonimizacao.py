"""
Service de anonimizacao de denuncias (issue #9).
NUNCA faz hard delete. Mesmo admin nao tem esse poder.
"""
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.db.models.denuncia import Denuncia
from src.db.models.usuario import Usuario


STATUS_RETIRADA_PELO_AUTOR = "retirada_pelo_autor"
STATUS_CANCELADA_POR_COACAO = "cancelada_por_coacao"

NOTA_RETIRADA = (
    "\n\n---\n\n"
    "AVISO: Esta denuncia foi retirada a pedido do autor em {data}. "
    "O fato relatado permanece publico para fins de transparencia publica. "
    "Para mais informacoes, consulte o codigo de rastreamento."
)


async def anonimizar_denuncia(db, denuncia, moderador, motivo):
    if denuncia.status_remocao == STATUS_RETIRADA_PELO_AUTOR:
        return denuncia
    agora = datetime.now(timezone.utc)
    denuncia.autor_id = None
    denuncia.anonima = True
    denuncia.status_remocao = STATUS_RETIRADA_PELO_AUTOR
    denuncia.removida_em = agora
    denuncia.removida_por = moderador.id
    denuncia.motivo_remocao = motivo
    nota = NOTA_RETIRADA.format(data=agora.strftime("%d/%m/%Y"))
    if nota not in denuncia.descricao:
        denuncia.descricao = denuncia.descricao + nota
    await db.commit()
    await db.refresh(denuncia)
    return denuncia


async def marcar_cancelada_por_coacao(db, denuncia, moderador, motivo):
    agora = datetime.now(timezone.utc)
    denuncia.status_remocao = STATUS_CANCELADA_POR_COACAO
    denuncia.removida_em = agora
    denuncia.removida_por = moderador.id
    denuncia.motivo_remocao = "[CANCELADA POR COACAO] " + motivo
    await db.commit()
    await db.refresh(denuncia)
    return denuncia


async def pedir_retirada(db, denuncia, autor, justificativa):
    if denuncia.autor_id != autor.id:
        raise PermissionError("Apenas o autor pode pedir retirada da propria denuncia")
    if denuncia.status_remocao is not None:
        raise ValueError("Denuncia ja tem decisao de remocao: " + str(denuncia.status_remocao))
    agora = datetime.now(timezone.utc)
    denuncia.pedido_retirada_em = agora
    denuncia.pedido_retirada_justificativa = justificativa
    await db.commit()
    await db.refresh(denuncia)
    return denuncia


async def listar_pedidos_pendentes(db):
    result = await db.execute(
        select(Denuncia)
        .where(Denuncia.pedido_retirada_em.isnot(None))
        .where(Denuncia.status_remocao.is_(None))
        .order_by(Denuncia.pedido_retirada_em.asc())
    )
    return list(result.scalars().all())


def is_moderador(usuario):
    if usuario is None:
        return False
    role = getattr(usuario, "role", None)
    if role is None:
        return False
    role_value = role.value if hasattr(role, "value") else str(role)
    return role_value in ("admin", "moderador")
