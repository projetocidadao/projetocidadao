"""
Schemas de Notificação.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict

from src.db.models.enums import TipoNotificacao, CanalNotificacao, StatusNotificacao


class NotificacaoBase(BaseModel):
    tipo: TipoNotificacao
    canal: CanalNotificacao = CanalNotificacao.IN_APP
    titulo: str
    mensagem: str
    referencia_tipo: Optional[str] = None
    referencia_id: Optional[int] = None
    url: Optional[str] = None
    dados_extras: Optional[Dict[str, Any]] = None


class NotificacaoCreate(NotificacaoBase):
    usuario_id: int


class NotificacaoRead(NotificacaoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int
    status: StatusNotificacao
    lida: bool
    lida_em: Optional[datetime]
    tentativas: int
    erro_ultimo: Optional[str]
    created_at: datetime
    enviado_em: Optional[datetime]
    telegram_message_id: Optional[int] = None


class NotificacaoUpdate(BaseModel):
    lida: Optional[bool] = None


class NotificacaoStats(BaseModel):
    total: int
    nao_lidas: int
    por_tipo: Dict[str, int]
    por_canal: Dict[str, int]


class PreferenciasNotificacao(BaseModel):
    """Estrutura das preferências de notificação do usuário."""
    in_app: Dict[str, bool] = {}
    telegram: Dict[str, bool] = {}
    email: Dict[str, bool] = {}


class PreferenciasNotificacaoUpdate(PreferenciasNotificacao):
    pass


class TelegramLinkRequest(BaseModel):
    """Solicita código de vinculação Telegram."""
    pass  # apenas para gerar o código


class TelegramLinkResponse(BaseModel):
    codigo: str
    expires_at: datetime
    bot_username: str
    instrucoes: str
