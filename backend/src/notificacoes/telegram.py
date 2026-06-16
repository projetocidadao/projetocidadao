"""
Integração com Telegram Bot API.
"""
import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timezone

import httpx


logger = logging.getLogger(__name__)


class TelegramBot:
    """
    Cliente simples para a Telegram Bot API.
    Usa long-poll para receber /start <codigo> e vincular usuários.
    """

    BASE_URL = "https://api.telegram.org/bot{token}/{method}"

    def __init__(self, token: str):
        self.token = token
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if not self._client:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _call(self, method: str, **params) -> Dict[str, Any]:
        url = self.BASE_URL.format(token=self.token, method=method)
        client = await self._get_client()
        try:
            resp = await client.post(url, json=params)
            data = resp.json()
            if not data.get("ok"):
                logger.error("Telegram API error: %s", data)
                return {"ok": False, "error": data.get("description", "Erro desconhecido")}
            return {"ok": True, "result": data.get("result")}
        except Exception as e:
            logger.exception("Erro ao chamar Telegram API: %s", e)
            return {"ok": False, "error": str(e)}

    async def send_message(
        self,
        chat_id: int | str,
        text: str,
        parse_mode: str = "HTML",
        disable_notification: bool = False,
        reply_markup: Optional[dict] = None,
    ) -> Dict[str, Any]:
        """Envia uma mensagem de texto."""
        params: dict = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_notification": disable_notification,
        }
        if reply_markup:
            params["reply_markup"] = reply_markup
        return await self._call("sendMessage", **params)

    async def get_me(self) -> Dict[str, Any]:
        return await self._call("getMe")

    async def get_updates(self, offset: Optional[int] = None, timeout: int = 30) -> Dict[str, Any]:
        params: dict = {"timeout": timeout}
        if offset is not None:
            params["offset"] = offset
        return await self._call("getUpdates", **params)

    async def set_webhook(self, url: str) -> Dict[str, Any]:
        return await self._call("setWebhook", url=url)


# Singleton
_bot: Optional[TelegramBot] = None


def get_telegram_bot() -> Optional[TelegramBot]:
    """Retorna o bot configurado (ou None se token ausente)."""
    global _bot
    if _bot is None:
        token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        if not token:
            return None
        _bot = TelegramBot(token)
    return _bot


async def enviar_mensagem_telegram(chat_id: int, texto: str) -> Optional[int]:
    """
    Envia mensagem e retorna o message_id do Telegram.
    Retorna None se falhar.
    """
    bot = get_telegram_bot()
    if not bot:
        logger.warning("Telegram bot não configurado (TELEGRAM_BOT_TOKEN ausente)")
        return None

    resultado = await bot.send_message(chat_id=chat_id, text=texto)
    if resultado.get("ok"):
        return resultado["result"].get("message_id")
    return None
