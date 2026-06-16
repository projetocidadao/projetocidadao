"""
Schemas Pydantic comuns (paginação, mensagens).
"""
from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field


T = TypeVar("T")


class Message(BaseModel):
    """Resposta simples de mensagem."""
    message: str


class PaginationParams(BaseModel):
    """Parâmetros de paginação (query string)."""
    page: int = Field(default=1, ge=1, description="Página (1-based)")
    per_page: int = Field(default=20, ge=1, le=100, description="Itens por página")


class PaginatedResponse(BaseModel, Generic[T]):
    """Resposta paginada genérica."""
    items: List[T]
    total: int
    page: int
    per_page: int
    pages: int


class ErrorResponse(BaseModel):
    """Resposta padrão de erro."""
    detail: str
    code: Optional[str] = None
