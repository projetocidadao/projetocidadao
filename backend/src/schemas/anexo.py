"""
Schemas do Anexo.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from src.models.enums import TipoAnexo


class AnexoBase(BaseModel):
    tipo: TipoAnexo = TipoAnexo.OUTRO
    descricao: Optional[str] = Field(None, max_length=500)
    denuncia_id: int


class AnexoCreate(AnexoBase):
    pass


class AnexoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tipo: TipoAnexo
    descricao: Optional[str]
    nome_arquivo: str
    mime_type: str
    tamanho_bytes: int
    hash_sha256: str
    url: str  # URL pública (ou presigned se privado)
    largura: Optional[int]
    altura: Optional[int]
    duracao_segundos: Optional[int]
    denuncia_id: int
    uploaded_by_id: Optional[int]
    created_at: datetime


class AnexoUpdate(BaseModel):
    tipo: Optional[TipoAnexo] = None
    descricao: Optional[str] = Field(None, max_length=500)


class UploadResponse(BaseModel):
    """Resposta do upload."""
    anexo: AnexoRead
    mensagem: str = "Arquivo enviado com sucesso"


class AnexoStats(BaseModel):
    """Estatísticas de anexos."""
    total_arquivos: int
    total_bytes: int
    por_tipo: dict[str, int]
