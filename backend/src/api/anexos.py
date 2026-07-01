"""
Rotas de Anexos — upload, download, listagem, exclusão.

Recursos:
- Upload multipart (até 50MB por arquivo)
- Validação de MIME
- Hash SHA256 para deduplicação
- Múltiplos providers: S3 (prod) ou filesystem local (dev)
- URL pública ou presigned
- Associa anexos a denúncias (e opcionalmente comentários)
"""
import io
from typing import List, Optional
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_async_session
from src.db.models.denuncia import Anexo
from src.db.models.denuncia import Denuncia
from src.schemas.anexo import AnexoRead, AnexoUpdate, UploadResponse, AnexoStats
from src.core.deps import get_current_active_user, require_moderator
from src.core.storage import (
    calcular_hash_sha256,
    detectar_mime,
    mime_para_tipo,
    validar_arquivo,
    salvar_arquivo,
    gerar_url_publica,
    deletar_arquivo,
    abrir_arquivo_local,
)
from src.db.models.usuario import Usuario
from src.db.models.enums import TipoAnexo


router = APIRouter(prefix="/api/denuncias", tags=["anexos"])


# =============================================================================
# UPLOAD
# =============================================================================
@router.post(
    "/{denuncia_id}/anexos",
    response_model=UploadResponse,
    status_code=201,
    summary="Enviar um ou mais anexos para uma denúncia",
)
async def upload_anexos(
    denuncia_id: int,
    files: List[UploadFile] = File(..., description="Arquivos a enviar (multipart/form-data)"),
    descricao: Optional[str] = Form(None, description="Descrição comum a todos os arquivos"),
    tipo: Optional[TipoAnexo] = Form(None, description="Tipo comum (auto-detectado se omitido)"),
    current_user: Usuario = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> UploadResponse:
    """
    Faz upload de 1 ou N arquivos para uma denúncia.
    - Detecta MIME, calcula hash SHA256, valida tamanho
    - Dedup: se o hash já existir para esta denúncia, retorna o existente
    - Suporta imagens, PDFs, vídeos curtos, planilhas e áudios
    """
    # Valida denúncia
    denuncia = await session.get(Denuncia, denuncia_id)
    if not denuncia:
        raise HTTPException(status_code=404, detail="Denúncia não encontrada")

    if not files:
        raise HTTPException(status_code=400, detail="Nenhum arquivo enviado")

    anexos_criados: list[Anexo] = []

    for upload in files:
        conteudo = await upload.read()

        # Detecta MIME real
        mime = detectar_mime(conteudo, upload.filename or "arquivo")
        # Valida
        validar_arquivo(conteudo, mime, upload.filename or "arquivo")
        # Hash para dedup
        hash_arquivo = calcular_hash_sha256(conteudo)

        # Dedup: se já existe anexo com mesmo hash nesta denúncia
        result = await session.execute(
            select(Anexo).where(
                Anexo.denuncia_id == denuncia_id,
                Anexo.hash_sha256 == hash_arquivo,
            )
        )
        if result.scalar_one_or_none():
            continue  # pula (já existe)

        # Salva no storage
        chave, tamanho = await salvar_arquivo(
            conteudo, upload.filename or "arquivo", mime
        )

        # Tenta extrair metadados (largura/altura para imagens, duração para vídeos)
        largura, altura, duracao = _extrair_metadados(conteudo, mime)

        # Tipo (auto se não informado)
        tipo_final = tipo or TipoAnexo(mime_para_tipo(mime))

        anexo = Anexo(
            denuncia_id=denuncia_id,
            uploaded_by_id=current_user.id,
            tipo=tipo_final,
            descricao=descricao,
            nome_arquivo=upload.filename or "arquivo",
            mime_type=mime,
            tamanho_bytes=tamanho,
            hash_sha256=hash_arquivo,
            storage_chave=chave,
            largura=largura,
            altura=altura,
            duracao_segundos=duracao,
        )
        session.add(anexo)
        anexos_criados.append(anexo)

    await session.commit()
    for a in anexos_criados:
        await session.refresh(a)

    # Resposta (apenas o primeiro, ou uma lista)
    if not anexos_criados:
        # Tudo era duplicado
        raise HTTPException(
            status_code=409,
            detail="Todos os arquivos enviados já existem nesta denúncia",
        )

    # Adiciona URL pública a cada anexo
    anexos_read = []
    for a in anexos_criados:
        ar = AnexoRead.model_validate(a)
        ar.url = gerar_url_publica(a.storage_chave)
        anexos_read.append(ar)

    return UploadResponse(
        anexo=anexos_read[0],  # para compat com schema de 1 arquivo
        mensagem=f"{len(anexos_read)} arquivo(s) enviado(s) com sucesso",
    )


# =============================================================================
# LISTAGEM
# =============================================================================
@router.get(
    "/{denuncia_id}/anexos",
    response_model=List[AnexoRead],
    summary="Listar anexos de uma denúncia",
)
async def list_anexos(
    denuncia_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> list[AnexoRead]:
    result = await session.execute(
        select(Anexo)
        .where(Anexo.denuncia_id == denuncia_id)
        .order_by(Anexo.created_at.desc())
    )
    anexos = list(result.scalars().all())
    anexos_read = []
    for a in anexos:
        ar = AnexoRead.model_validate(a)
        ar.url = gerar_url_publica(a.storage_chave)
        anexos_read.append(ar)
    return anexos_read


# =============================================================================
# DETALHE / DOWNLOAD
# =============================================================================
@router.get(
    "/{denuncia_id}/anexos/{anexo_id}",
    response_model=AnexoRead,
    summary="Detalhe de um anexo",
)
async def get_anexo(
    denuncia_id: int,
    anexo_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> AnexoRead:
    anexo = await session.get(Anexo, anexo_id)
    if not anexo or anexo.denuncia_id != denuncia_id:
        raise HTTPException(status_code=404, detail="Anexo não encontrado")
    ar = AnexoRead.model_validate(anexo)
    ar.url = gerar_url_publica(anexo.storage_chave)
    return ar


@router.get(
    "/{denuncia_id}/anexos/{anexo_id}/download",
    summary="Baixar o arquivo de um anexo (dev: filesystem local)",
    response_class=StreamingResponse,
)
async def download_anexo(
    denuncia_id: int,
    anexo_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Stream do arquivo.
    Em produção, redirecione para a URL presigned do S3.
    """
    anexo = await session.get(Anexo, anexo_id)
    if not anexo or anexo.denuncia_id != denuncia_id:
        raise HTTPException(status_code=404, detail="Anexo não encontrado")

    fp = abrir_arquivo_local(anexo.storage_chave)
    if not fp:
        raise HTTPException(
            status_code=404,
            detail="Arquivo não disponível no storage local. Use a URL pública para S3.",
        )

    return StreamingResponse(
        io.BytesIO(fp.read()),
        media_type=anexo.mime_type,
        headers={
            "Content-Disposition": f'attachment; filename="{anexo.nome_arquivo}"',
        },
    )


# =============================================================================
# ATUALIZAR METADADOS
# =============================================================================
@router.patch(
    "/{denuncia_id}/anexos/{anexo_id}",
    response_model=AnexoRead,
    summary="Atualizar tipo/descrição (autor ou moderador+)",
)
async def update_anexo(
    denuncia_id: int,
    anexo_id: int,
    dados: AnexoUpdate,
    current_user: Usuario = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> AnexoRead:
    anexo = await session.get(Anexo, anexo_id)
    if not anexo or anexo.denuncia_id != denuncia_id:
        raise HTTPException(status_code=404, detail="Anexo não encontrado")

    # Permissão: uploader, autor da denúncia, ou moderador
    denuncia = await session.get(Denuncia, denuncia_id)
    is_uploader = anexo.uploaded_by_id == current_user.id
    is_owner = denuncia.autor_id == current_user.id
    is_mod = current_user.role.value in ("moderador", "admin")
    if not (is_uploader or is_owner or is_mod):
        raise HTTPException(status_code=403, detail="Sem permissão")

    for field, value in dados.model_dump(exclude_unset=True).items():
        setattr(anexo, field, value)
    await session.commit()
    await session.refresh(anexo)

    ar = AnexoRead.model_validate(anexo)
    ar.url = gerar_url_publica(anexo.storage_chave)
    return ar


# =============================================================================
# DELETAR
# =============================================================================
@router.delete(
    "/{denuncia_id}/anexos/{anexo_id}",
    status_code=204,
    summary="Apagar anexo (uploader, autor da denúncia, moderador+)",
)
async def delete_anexo(
    denuncia_id: int,
    anexo_id: int,
    current_user: Usuario = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> None:
    anexo = await session.get(Anexo, anexo_id)
    if not anexo or anexo.denuncia_id != denuncia_id:
        raise HTTPException(status_code=404, detail="Anexo não encontrado")

    denuncia = await session.get(Denuncia, denuncia_id)
    is_uploader = anexo.uploaded_by_id == current_user.id
    is_owner = denuncia.autor_id == current_user.id
    is_mod = current_user.role.value in ("moderador", "admin")
    if not (is_uploader or is_owner or is_mod):
        raise HTTPException(status_code=403, detail="Sem permissão")

    chave = anexo.storage_chave
    await session.delete(anexo)
    await session.commit()

    # Remove do storage (best effort)
    deletar_arquivo(chave)


# =============================================================================
# ESTATÍSTICAS
# =============================================================================
@router.get(
    "/{denuncia_id}/anexos/stats",
    response_model=AnexoStats,
    summary="Estatísticas de anexos de uma denúncia",
)
async def anexo_stats(
    denuncia_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> AnexoStats:
    result = await session.execute(
        select(
            func.count(Anexo.id).label("total"),
            func.coalesce(func.sum(Anexo.tamanho_bytes), 0).label("bytes"),
        ).where(Anexo.denuncia_id == denuncia_id)
    )
    total, total_bytes = result.one()

    result_tipos = await session.execute(
        select(Anexo.tipo, func.count(Anexo.id))
        .where(Anexo.denuncia_id == denuncia_id)
        .group_by(Anexo.tipo)
    )
    por_tipo = {t.value: c for t, c in result_tipos.all()}

    return AnexoStats(
        total_arquivos=total or 0,
        total_bytes=int(total_bytes or 0),
        por_tipo=por_tipo,
    )


# =============================================================================
# HELPER
# =============================================================================
def _extrair_metadados(conteudo: bytes, mime: str) -> tuple[Optional[int], Optional[int], Optional[int]]:
    """
    Tenta extrair largura/altura (imagens) ou duração (vídeos).
    Retorna (largura, altura, duracao_segundos).
    """
    largura, altura, duracao = None, None, None

    if mime.startswith("image/"):
        try:
            from PIL import Image
            img = Image.open(io.BytesIO(conteudo))
            largura, altura = img.size
        except Exception:
            pass

    if mime.startswith("video/") or mime.startswith("audio/"):
        try:
            # Requer ffprobe instalado no sistema
            import subprocess
            import tempfile
            import json
            with tempfile.NamedTemporaryFile(suffix=".tmp", delete=False) as tmp:
                tmp.write(conteudo)
                tmp_path = tmp.name
            try:
                result = subprocess.run(
                    ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", tmp_path],
                    capture_output=True, text=True, timeout=5,
                )
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    dur = data.get("format", {}).get("duration")
                    if dur:
                        duracao = int(float(dur))
            finally:
                import os
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
        except Exception:
            pass

    return largura, altura, duracao
