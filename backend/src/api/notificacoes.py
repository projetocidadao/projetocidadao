"""
Rotas de Notificações — listar, marcar como lida, configurar preferências.
"""
import secrets
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_async_session
from src.db.models.notificacao import Notificacao
from src.db.models.usuario import Usuario
from src.db.models.enums import StatusNotificacao, TipoNotificacao
from src.core.deps import get_current_active_user
from src.schemas.notificacao import (
    NotificacaoRead, NotificacaoUpdate, NotificacaoStats,
    PreferenciasNotificacao, PreferenciasNotificacaoUpdate,
    TelegramLinkResponse,
)
from src.notificacoes.worker import processar_fila_pendentes


router = APIRouter(prefix="/api/notificacoes", tags=["notificacoes"])


# =============================================================================
# Listagem
# =============================================================================
@router.get("", response_model=List[NotificacaoRead], summary="Minhas notificações")
async def listar_notificacoes(
    apenas_nao_lidas: bool = False,
    tipo: Optional[TipoNotificacao] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: Usuario = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> list[NotificacaoRead]:
    stmt = select(Notificacao).where(Notificacao.usuario_id == current_user.id)
    if apenas_nao_lidas:
        stmt = stmt.where(Notificacao.lida == False)
    if tipo:
        stmt = stmt.where(Notificacao.tipo == tipo)
    stmt = stmt.order_by(Notificacao.created_at.desc()).offset(offset).limit(limit)
    result = await session.execute(stmt)
    return list(result.scalars().all())


@router.get("/stats", response_model=NotificacaoStats, summary="Estatísticas")
async def stats(
    current_user: Usuario = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> NotificacaoStats:
    base = select(Notificacao).where(Notificacao.usuario_id == current_user.id)
    result_total = await session.execute(
        select(func.count(Notificacao.id)).where(Notificacao.usuario_id == current_user.id)
    )
    result_nao_lidas = await session.execute(
        select(func.count(Notificacao.id)).where(
            and_(Notificacao.usuario_id == current_user.id, Notificacao.lida == False)
        )
    )
    result_tipo = await session.execute(
        select(Notificacao.tipo, func.count(Notificacao.id))
        .where(Notificacao.usuario_id == current_user.id)
        .group_by(Notificacao.tipo)
    )
    result_canal = await session.execute(
        select(Notificacao.canal, func.count(Notificacao.id))
        .where(Notificacao.usuario_id == current_user.id)
        .group_by(Notificacao.canal)
    )
    return NotificacaoStats(
        total=result_total.scalar() or 0,
        nao_lidas=result_nao_lidas.scalar() or 0,
        por_tipo={t.value: c for t, c in result_tipo.all()},
        por_canal={c.value: n for c, n in result_canal.all()},
    )


# =============================================================================
# Marcar como lida
# =============================================================================
@router.patch(
    "/{notificacao_id}",
    response_model=NotificacaoRead,
    summary="Marcar como lida/não lida",
)
async def atualizar(
    notificacao_id: int,
    dados: NotificacaoUpdate,
    current_user: Usuario = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> NotificacaoRead:
    n = await session.get(Notificacao, notificacao_id)
    if not n or n.usuario_id != current_user.id:
        raise HTTPException(status_code=404, detail="Notificação não encontrada")
    if dados.lida is not None:
        n.lida = dados.lida
        n.lida_em = datetime.now(timezone.utc) if dados.lida else None
    await session.commit()
    await session.refresh(n)
    return n


@router.post(
    "/marcar-todas-lidas",
    summary="Marcar todas como lidas",
)
async def marcar_todas_lidas(
    current_user: Usuario = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    agora = datetime.now(timezone.utc)
    result = await session.execute(
        select(Notificacao).where(
            and_(Notificacao.usuario_id == current_user.id, Notificacao.lida == False)
        )
    )
    notificacoes = list(result.scalars().all())
    for n in notificacoes:
        n.lida = True
        n.lida_em = agora
    await session.commit()
    return {"marcadas": len(notificacoes)}


# =============================================================================
# Preferências
# =============================================================================
@router.get(
    "/preferencias",
    response_model=PreferenciasNotificacao,
    summary="Preferências de notificação",
)
async def get_preferencias(
    current_user: Usuario = Depends(get_current_active_user),
) -> PreferenciasNotificacao:
    return PreferenciasNotificacao(
        **(current_user.preferencias_notificacao or {})
    )


@router.put(
    "/preferencias",
    response_model=PreferenciasNotificacao,
    summary="Atualizar preferências",
)
async def update_preferencias(
    dados: PreferenciasNotificacaoUpdate,
    current_user: Usuario = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> PreferenciasNotificacao:
    current_user.preferencias_notificacao = dados.model_dump()
    await session.commit()
    await session.refresh(current_user)
    return PreferenciasNotificacao(**dados.model_dump())


# =============================================================================
# Telegram linking
# =============================================================================
@router.post(
    "/telegram/gerar-codigo",
    response_model=TelegramLinkResponse,
    summary="Gerar código para vincular Telegram",
)
async def gerar_codigo_telegram(
    current_user: Usuario = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> TelegramLinkResponse:
    """
    Gera um código de 8 caracteres que o usuário envia ao bot do Telegram.
    O bot vincula chat_id ao usuário.
    """
    codigo = secrets.token_urlsafe(6)[:8].upper()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)

    prefs = current_user.preferencias_notificacao or {}
    prefs["_telegram_link_code"] = codigo
    prefs["_telegram_link_expires"] = expires_at.isoformat()
    current_user.preferencias_notificacao = prefs
    await session.commit()

    bot_username = "ProjetoCidadaoBot"  # configurável
    instrucoes = (
        f"1. Abra o Telegram e procure @{bot_username}\n"
        f"2. Envie: /start {codigo}\n"
        f"3. O código expira em 15 minutos"
    )

    return TelegramLinkResponse(
        codigo=codigo,
        expires_at=expires_at,
        bot_username=bot_username,
        instrucoes=instrucoes,
    )


# =============================================================================
# Admin — processar fila manualmente
# =============================================================================
@router.post(
    "/admin/processar-fila",
    summary="Forçar processamento da fila (admin)",
)
async def processar_fila(
    limit: int = 100,
    current_user: Usuario = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    if current_user.role.value not in ("moderador", "admin"):
        raise HTTPException(status_code=403, detail="Sem permissão")
    return await processar_fila_pendentes(session, limite=limit)
