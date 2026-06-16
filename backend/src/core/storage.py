"""
Camada de storage — abstrai S3 (boto3) e filesystem local.

Em produção usa S3-compatible (MinIO, AWS S3, R2, Backblaze B2).
Em desenvolvimento, se as variáveis S3 não estiverem setadas, usa filesystem local.
"""
import os
import shutil
import hashlib
import mimetypes
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Tuple, BinaryIO
from urllib.parse import quote

from fastapi import UploadFile, HTTPException, status


# =============================================================================
# Configurações
# =============================================================================
MAX_FILE_SIZE_DEFAULT = 50 * 1024 * 1024  # 50 MB

# Tipos MIME permitidos
MIME_ALLOWED = {
    # Imagens
    "image/jpeg", "image/png", "image/gif", "image/webp", "image/svg+xml",
    # Documentos
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "text/plain", "text/csv",
    # Vídeos (pequenos)
    "video/mp4", "video/quicktime", "video/webm",
    # Áudio
    "audio/mpeg", "audio/ogg", "audio/wav",
}

# Mapeamento de MIME → tipo de anexo
MIME_TO_TIPO = {
    "image/": "IMAGEM",
    "video/": "VIDEO",
    "audio/": "AUDIO",
    "application/pdf": "DOCUMENTO",
    "application/msword": "DOCUMENTO",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "DOCUMENTO",
    "application/vnd.ms-excel": "PLANILHA",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "PLANILHA",
    "text/csv": "PLANILHA",
    "text/plain": "DOCUMENTO",
}


# =============================================================================
# Detecção de provider
# =============================================================================
def _is_s3_configured() -> bool:
    """Verifica se o S3 está configurado."""
    return bool(
        os.getenv("S3_ENDPOINT")
        and os.getenv("S3_ACCESS_KEY")
        and os.getenv("S3_SECRET_KEY")
    )


def _get_local_storage_path() -> Path:
    """Retorna o diretório local de armazenamento."""
    path = Path(os.getenv("LOCAL_STORAGE_PATH", "/tmp/projeto-cidadao-storage"))
    path.mkdir(parents=True, exist_ok=True)
    return path


# =============================================================================
# Funções utilitárias
# =============================================================================
def calcular_hash_sha256(conteudo: bytes) -> str:
    """Calcula o hash SHA256 de um conteúdo."""
    return hashlib.sha256(conteudo).hexdigest()


def detectar_mime(conteudo: bytes, nome_arquivo: str) -> str:
    """
    Detecta o tipo MIME do conteúdo.
    Tenta usar python-magic (se disponível), depois adivinha pela extensão.
    """
    # Tenta via python-magic
    try:
        import magic
        mime = magic.from_buffer(conteudo, mime=True)
        if mime:
            return mime
    except (ImportError, Exception):
        pass

    # Fallback: pela extensão
    mime, _ = mimetypes.guess_type(nome_arquivo)
    return mime or "application/octet-stream"


def mime_para_tipo(mime: str) -> str:
    """Converte MIME em tipo de anexo (IMAGEM, VIDEO, etc)."""
    for prefix, tipo in MIME_TO_TIPO.items():
        if mime.startswith(prefix):
            return tipo
    return "OUTRO"


def gerar_chave_arquivo(nome_arquivo: str, mime: str) -> str:
    """
    Gera uma chave única para o arquivo.
    Formato: YYYY/MM/DD/<uuid>-<nome_limpo>
    """
    hoje = datetime.now(timezone.utc)
    uid = uuid.uuid4().hex[:12]
    nome_limpo = Path(nome_arquivo).name.replace(" ", "_")
    nome_limpo = "".join(c for c in nome_limpo if c.isalnum() or c in "._-")[:80]
    return f"{hoje:%Y/%m/%d}/{uid}-{nome_limpo}"


# =============================================================================
# Validações
# =============================================================================
def validar_arquivo(
    conteudo: bytes,
    mime: str,
    nome_arquivo: str,
    max_size: int = MAX_FILE_SIZE_DEFAULT,
) -> None:
    """
    Valida um arquivo. Lança HTTPException se inválido.
    """
    # Tamanho
    if len(conteudo) == 0:
        raise HTTPException(status_code=400, detail="Arquivo vazio")
    if len(conteudo) > max_size:
        raise HTTPException(
            status_code=413,
            detail=f"Arquivo muito grande ({len(conteudo) / 1024 / 1024:.1f} MB). Máximo: {max_size // 1024 // 1024} MB",
        )

    # MIME
    if mime not in MIME_ALLOWED:
        raise HTTPException(
            status_code=415,
            detail=f"Tipo de arquivo não permitido: {mime}. Permitidos: {sorted(MIME_ALLOWED)}",
        )

    # Nome do arquivo
    if not nome_arquivo or len(nome_arquivo) > 255:
        raise HTTPException(status_code=400, detail="Nome de arquivo inválido")


# =============================================================================
# Storage provider (S3 ou local)
# =============================================================================
async def salvar_arquivo(
    conteudo: bytes,
    nome_arquivo: str,
    mime: str,
) -> Tuple[str, int]:
    """
    Salva um arquivo no storage configurado.
    Retorna (chave, tamanho_bytes).
    """
    chave = gerar_chave_arquivo(nome_arquivo, mime)

    if _is_s3_configured():
        return await _salvar_s3(conteudo, chave, mime)
    return await _salvar_local(conteudo, chave)


async def _salvar_s3(conteudo: bytes, chave: str, mime: str) -> Tuple[str, int]:
    """Salva no S3-compatible."""
    try:
        import boto3
    except ImportError:
        raise RuntimeError("boto3 não instalado. Rode: pip install boto3")

    s3 = boto3.client(
        "s3",
        endpoint_url=os.getenv("S3_ENDPOINT"),
        aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("S3_SECRET_KEY"),
        region_name=os.getenv("S3_REGION", "us-east-1"),
    )
    bucket = os.getenv("S3_BUCKET", "projetocidadao")
    s3.put_object(Bucket=bucket, Key=chave, Body=conteudo, ContentType=mime)
    return chave, len(conteudo)


async def _salvar_local(conteudo: bytes, chave: str) -> Tuple[str, int]:
    """Salva no filesystem local (dev)."""
    base = _get_local_storage_path()
    destino = base / chave
    destino.parent.mkdir(parents=True, exist_ok=True)
    with open(destino, "wb") as f:
        f.write(conteudo)
    return chave, len(conteudo)


def gerar_url_publica(chave: str) -> str:
    """
    Gera a URL pública (ou presigned) para acessar o arquivo.
    """
    if _is_s3_configured():
        # Em produção, gerar URL presigned com expiração
        try:
            import boto3
            s3 = boto3.client(
                "s3",
                endpoint_url=os.getenv("S3_ENDPOINT"),
                aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
                aws_secret_access_key=os.getenv("S3_SECRET_KEY"),
                region_name=os.getenv("S3_REGION", "us-east-1"),
            )
            bucket = os.getenv("S3_BUCKET", "projetocidadao")
            return s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket, "Key": chave},
                ExpiresIn=3600 * 24,  # 24h
            )
        except Exception:
            pass

    # Local: URL relativa
    return f"/files/{quote(chave, safe='/')}"


def deletar_arquivo(chave: str) -> bool:
    """Remove um arquivo do storage."""
    try:
        if _is_s3_configured():
            import boto3
            s3 = boto3.client(
                "s3",
                endpoint_url=os.getenv("S3_ENDPOINT"),
                aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
                aws_secret_access_key=os.getenv("S3_SECRET_KEY"),
            )
            bucket = os.getenv("S3_BUCKET", "projetocidadao")
            s3.delete_object(Bucket=bucket, Key=chave)
        else:
            destino = _get_local_storage_path() / chave
            if destino.exists():
                destino.unlink()
        return True
    except Exception:
        return False


def abrir_arquivo_local(chave: str) -> Optional[BinaryIO]:
    """Abre arquivo local (apenas em modo dev)."""
    if _is_s3_configured():
        return None
    destino = _get_local_storage_path() / chave
    if not destino.exists():
        return None
    return open(destino, "rb")
