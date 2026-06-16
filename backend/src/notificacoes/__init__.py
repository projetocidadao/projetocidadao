"""
Pacote de Notificações — in-app + Telegram + email.

Subpacotes:
- telegram: integração com Bot API
- worker: fila de entrega e hooks
- templates: renderização de mensagens por tipo
"""
from src.notificacoes.telegram import (
    TelegramBot,
    get_telegram_bot,
    enviar_mensagem_telegram,
)
from src.notificacoes.worker import (
    criar_notificacao,
    enviar_notificacao,
    processar_fila_pendentes,
    hook_faro_criado,
    hook_denuncia_status,
    hook_nivel_up,
)
from src.notificacoes.templates import renderizar_mensagem

__all__ = [
    "TelegramBot", "get_telegram_bot", "enviar_mensagem_telegram",
    "criar_notificacao", "enviar_notificacao", "processar_fila_pendentes",
    "hook_faro_criado", "hook_denuncia_status", "hook_nivel_up",
    "renderizar_mensagem",
]
