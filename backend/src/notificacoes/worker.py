"""
Worker de Notificações — entrega in-app e via Telegram.

Funções principais:
- criar_notificacao: cria a notificação no banco (status=PENDENTE)
- enviar_notificacao: tenta entregar via canal configurado
- processar_fila_pendentes: processa notificações pendentes em batch
- hooks: helpers chamados por outras partes do sistema
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import async_session
from src.models.notificacao import Notificacao
from src.models.usuario import Usuario
from src.models.enums import (
    TipoNotificacao, CanalNotificacao, StatusNotificacao, UserRole
)
from src.notificacoes.telegram import enviar_mensagem_telegram
from src.notificacoes.templates import renderizar_mensagem


logger = logging.getLogger(__name__)


# =============================================================================
# Criar e enviar
# =============================================================================
async def criar_notificacao(
    session: AsyncSession,
    usuario_id: int,
    tipo: TipoNotificacao,
    dados: Dict[str, Any],
    canais: Optional[List[CanalNotificacao]] = None,
) -> List[Notificacao]:
    """
    Cria uma notificação para um usuário em um ou mais canais.
    Respeita as preferências do usuário.
    """
    # Carrega usuário
    usuario = await session.get(Usuario, usuario_id)
    if not usuario:
        return []

    canais = canais or [CanalNotificacao.IN_APP]

    # Filtra pelas preferências do usuário
    preferencias = usuario.preferencias_notificacao or {}
    canais_ativos: list[CanalNotificacao] = []
    for canal in canais:
        pref_canal = preferencias.get(canal.value, {})
        if isinstance(pref_canal, dict):
            habilitado = pref_canal.get(tipo.value, True)
        else:
            habilitado = bool(pref_canal)
        if habilitado:
            canais_ativos.append(canal)

    if not canais_ativos:
        canais_ativos = [CanalNotificacao.IN_APP]  # fallback

    # Renderiza a mensagem uma vez
    template_in_app = renderizar_mensagem(tipo, dados, canal="in_app")
    template_telegram = renderizar_mensagem(tipo, dados, canal="telegram")

    notificacoes: list[Notificacao] = []
    for canal in canais_ativos:
        tpl = template_telegram if canal == CanalNotificacao.TELEGRAM else template_in_app
        n = Notificacao(
            usuario_id=usuario_id,
            tipo=tipo,
            canal=canal,
            status=StatusNotificacao.PENDENTE,
            titulo=tpl["titulo"],
            mensagem=tpl["mensagem"],
            referencia_tipo=dados.get("referencia_tipo"),
            referencia_id=dados.get("referencia_id"),
            url=dados.get("url"),
            dados_extras=dados.get("dados_extras"),
        )
        session.add(n)
        notificacoes.append(n)

    await session.commit()
    for n in notificacoes:
        await session.refresh(n)

    # Tenta enviar imediatamente
    for n in notificacoes:
        try:
            await enviar_notificacao(session, n)
        except Exception as e:
            logger.exception("Erro enviando notificação %s: %s", n.id, e)

    return notificacoes


async def enviar_notificacao(session: AsyncSession, n: Notificacao) -> bool:
    """Tenta entregar a notificação via seu canal."""
    if n.status == StatusNotificacao.ENVIADA:
        return True

    n.tentativas += 1
    try:
        if n.canal == CanalNotificacao.IN_APP:
            # In-app: já está no banco, é "entregue" por estar visível na API
            n.status = StatusNotificacao.ENVIADA
            n.enviado_em = datetime.now(timezone.utc)
            await session.commit()
            return True

        if n.canal == CanalNotificacao.TELEGRAM:
            usuario = await session.get(Usuario, n.usuario_id)
            if not usuario or not usuario.telegram_id:
                n.status = StatusNotificacao.FALHOU
                n.erro_ultimo = "Usuário sem Telegram vinculado"
                await session.commit()
                return False

            msg_id = await enviar_mensagem_telegram(
                chat_id=usuario.telegram_id, texto=f"<b>{n.titulo}</b>\n\n{n.mensagem}"
            )
            if msg_id:
                n.telegram_message_id = msg_id
                n.status = StatusNotificacao.ENVIADA
                n.enviado_em = datetime.now(timezone.utc)
                await session.commit()
                return True
            n.status = StatusNotificacao.FALHOU
            n.erro_ultimo = "Falha ao enviar via Telegram"
            await session.commit()
            return False

        if n.canal == CanalNotificacao.EMAIL:
            # Stub — integrar com SendGrid/SES/etc.
            n.status = StatusNotificacao.FALHOU
            n.erro_ultimo = "Email ainda não implementado"
            await session.commit()
            return False

        return False
    except Exception as e:
        n.status = StatusNotificacao.FALHOU
        n.erro_ultimo = str(e)[:500]
        await session.commit()
        logger.exception("Erro ao enviar notificação %s: %s", n.id, e)
        return False


async def processar_fila_pendentes(
    session: AsyncSession, limite: int = 100
) -> dict:
    """Processa notificações pendentes (ou que falharam há mais de 5 min)."""
    limite_tempo = datetime.now(timezone.utc) - timedelta(minutes=5)
    result = await session.execute(
        select(Notificacao)
        .where(
            and_(
                Notificacao.status.in_([StatusNotificacao.PENDENTE, StatusNotificacao.FALHOU]),
                Notificacao.tentativas < 5,
            )
        )
        .order_by(Notificacao.created_at.asc())
        .limit(limite)
    )
    notificacoes = list(result.scalars().all())

    enviadas = 0
    falhas = 0
    for n in notificacoes:
        if n.status == StatusNotificacao.FALHOU and n.enviado_em and n.enviado_em > limite_tempo:
            continue
        if await enviar_notificacao(session, n):
            enviadas += 1
        else:
            falhas += 1

    return {"processadas": len(notificacoes), "enviadas": enviadas, "falhas": falhas}


# =============================================================================
# HOOKS — disparados por outras partes do sistema
# =============================================================================
async def hook_faro_criado(faro) -> None:
    """
    Chamado quando um faro novo é criado.
    Notifica moderadores+ para faros com score >= 30 (CRÍTICO se >= 70).
    """
    async with async_session() as session:
        # Encontra moderadores e admins
        result = await session.execute(
            select(Usuario).where(Usuario.role.in_([UserRole.MODERADOR, UserRole.ADMIN]))
        )
        destinatarios = list(result.scalars().all())

        tipo = (
            TipoNotificacao.FARO_CRITICO
            if faro.score_risco >= 70
            else TipoNotificacao.FARO_NOVO
        )

        dados = {
            "faro_id": faro.id,
            "score_risco": faro.score_risco,
            "severidade": faro.severidade if isinstance(faro.severidade, str) else faro.severidade.value,
            "titulo": faro.entidade_nome,
            "codigo_rastreio": getattr(faro, "codigo", "PC-XXXX"),
            "heuristicas": faro.heuristicas or [],
            "evidencia": faro.evidencia or {},
        }

        for user in destinatarios:
            await criar_notificacao(
                session=session,
                usuario_id=user.id,
                tipo=tipo,
                dados=dados,
                canais=[CanalNotificacao.IN_APP, CanalNotificacao.TELEGRAM],
            )


async def hook_denuncia_status(
    denuncia_id: int,
    usuario_id: int,
    status_anterior: str,
    novo_status: str,
    titulo: str = "",
) -> None:
    """Chamado quando o status de uma denúncia muda."""
    async with async_session() as session:
        await criar_notificacao(
            session=session,
            usuario_id=usuario_id,
            tipo=TipoNotificacao.DENUNCIA_STATUS,
            dados={
                "denuncia_id": denuncia_id,
                "status_anterior": status_anterior,
                "novo_status": novo_status,
                "titulo": titulo,
            },
            canais=[CanalNotificacao.IN_APP, CanalNotificacao.TELEGRAM],
        )


async def hook_nivel_up(usuario_id: int, nivel: int, pontos: int) -> None:
    """Chamado quando o usuário sobe de nível."""
    async with async_session() as session:
        await criar_notificacao(
            session=session,
            usuario_id=usuario_id,
            tipo=TipoNotificacao.NIVEL_UP,
            dados={"nivel": nivel, "pontos": pontos},
            canais=[CanalNotificacao.IN_APP],
        )
