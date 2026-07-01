"""
Rotas de Denúncias (CRUD + busca + geolocalização).
"""
import secrets
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_async_session
from src.db.models.denuncia import Denuncia
from src.db.models.enums import StatusDenuncia
from src.schemas.denuncia import DenunciaCreate, DenunciaRead, DenunciaUpdate, DenunciaStatusUpdate
from src.core.deps import get_current_active_user, require_moderator
from src.db.models.usuario import Usuario


router = APIRouter(prefix="/api/denuncias", tags=["denuncias"])


def gerar_codigo_rastreio() -> str:
    """Gera um código único curto para rastreamento público (ex.: PC-AB12CD34)."""
    return f"PC-{secrets.token_hex(4).upper()}"


@router.get(
    "",
    response_model=List[DenunciaRead],
    summary="Listar denúncias públicas com filtros",
)
async def list_denuncias(
    status: Optional[StatusDenuncia] = Query(None, description="Filtrar por status"),
    categoria: Optional[str] = Query(None, description="Filtrar por categoria"),
    municipio: Optional[str] = Query(None, description="Filtrar por município"),
    estado: Optional[str] = Query(None, description="Filtrar por estado (UF)"),
    search: Optional[str] = Query(None, description="Busca textual em título/descrição"),
    area_id: Optional[int] = Query(None, description="Filtrar por área"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_async_session),
) -> list[Denuncia]:
    """Lista denúncias públicas com filtros opcionais."""
    query = select(Denuncia).where(Denuncia.publica == True)

    if status:
        query = query.where(Denuncia.status == status)
    if categoria:
        query = query.where(Denuncia.categoria == categoria)
    if municipio:
        query = query.where(Denuncia.municipio.ilike(f"%{municipio}%"))
    if estado:
        query = query.where(Denuncia.estado == estado.upper())
    if area_id:
        query = query.where(Denuncia.area_id == area_id)
    if search:
        query = query.where(
            or_(
                Denuncia.titulo.ilike(f"%{search}%"),
                Denuncia.descricao.ilike(f"%{search}%"),
            )
        )

    query = query.order_by(Denuncia.created_at.desc()).offset(skip).limit(limit)
    result = await session.execute(query)
    return list(result.scalars().all())


@router.post(
    "",
    response_model=DenunciaRead,
    status_code=201,
    summary="Criar nova denúncia (cidadão autenticado)",
)
async def create_denuncia(
    dados: DenunciaCreate,
    current_user: Usuario = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> Denuncia:
    """Cria uma denúncia. Se anonima=True, oculta o autor do público."""
    # Gera código de rastreio único
    for _ in range(5):
        codigo = gerar_codigo_rastreio()
        result = await session.execute(select(Denuncia).where(Denuncia.codigo_rastreio == codigo))
        if not result.scalar_one_or_none():
            break
    else:
        raise HTTPException(status_code=500, detail="Não foi possível gerar código de rastreio")

    # Define o autor_id conforme anonimato
    autor_id = None if dados.anonima else current_user.id

    # Roteamento automático por categoria
    canal_destino = rotear_denuncia(dados.categoria.value)

    denuncia = Denuncia(
        **dados.model_dump(),
        autor_id=autor_id,
        codigo_rastreio=codigo,
        canal_destino=canal_destino,
    )
    session.add(denuncia)
    await session.commit()
    await session.refresh(denuncia)
    return denuncia


@router.get(
    "/codigo/{codigo}",
    response_model=DenunciaRead,
    summary="Buscar denúncia por código de rastreio",
)
async def get_by_codigo(
    codigo: str,
    session: AsyncSession = Depends(get_async_session),
) -> Denuncia:
    result = await session.execute(
        select(Denuncia).where(Denuncia.codigo_rastreio == codigo.upper())
    )
    denuncia = result.scalar_one_or_none()
    if not denuncia:
        raise HTTPException(status_code=404, detail="Denúncia não encontrada")
    # Incrementa visualização (somente para denúncias públicas)
    if denuncia.publica:
        denuncia.visualizacoes += 1
        await session.commit()
        await session.refresh(denuncia)
    return denuncia


@router.get(
    "/{denuncia_id}",
    response_model=DenunciaRead,
    summary="Detalhe de uma denúncia",
)
async def get_denuncia(
    denuncia_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> Denuncia:
    result = await session.execute(select(Denuncia).where(Denuncia.id == denuncia_id))
    denuncia = result.scalar_one_or_none()
    if not denuncia:
        raise HTTPException(status_code=404, detail="Denúncia não encontrada")
    if denuncia.publica:
        denuncia.visualizacoes += 1
        await session.commit()
        await session.refresh(denuncia)
    return denuncia


@router.patch(
    "/{denuncia_id}",
    response_model=DenunciaRead,
    summary="Atualizar denúncia (autor ou moderador+)",
)
async def update_denuncia(
    denuncia_id: int,
    dados: DenunciaUpdate,
    current_user: Usuario = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> Denuncia:
    result = await session.execute(select(Denuncia).where(Denuncia.id == denuncia_id))
    denuncia = result.scalar_one_or_none()
    if not denuncia:
        raise HTTPException(status_code=404, detail="Denúncia não encontrada")

    # Apenas o autor ou moderador pode editar
    is_owner = denuncia.autor_id == current_user.id
    is_mod = current_user.role.value in ("moderador", "admin")
    if not (is_owner or is_mod):
        raise HTTPException(status_code=403, detail="Sem permissão para editar")

    for field, value in dados.model_dump(exclude_unset=True).items():
        setattr(denuncia, field, value)
    await session.commit()
    await session.refresh(denuncia)
    return denuncia


@router.patch(
    "/{denuncia_id}/status",
    response_model=DenunciaRead,
    summary="Mudar status da denúncia (moderador+)",
)
async def update_status(
    denuncia_id: int,
    dados: DenunciaStatusUpdate,
    current_user: Usuario = Depends(require_moderator),
    session: AsyncSession = Depends(get_async_session),
) -> Denuncia:
    """Endpoint para moderadores atualizarem o fluxo da denúncia."""
    result = await session.execute(select(Denuncia).where(Denuncia.id == denuncia_id))
    denuncia = result.scalar_one_or_none()
    if not denuncia:
        raise HTTPException(status_code=404, detail="Denúncia não encontrada")

    denuncia.status = dados.status
    if dados.canal_destino:
        denuncia.canal_destino = dados.canal_destino
    await session.commit()
    await session.refresh(denuncia)
    return denuncia


# -----------------------------------------------------------------------------
# Roteamento automático para órgãos competentes
# -----------------------------------------------------------------------------
ROTAS_POR_CATEGORIA = {
    "saude":         "Ministério Público + Secretaria de Saúde",
    "educacao":      "Ministério Público + MEC / Secretaria de Educação",
    "alimentacao":   "Ministério Público + CONSEA",
    "transporte":    "ANTT / DNIT / Órgão municipal de transporte",
    "seguranca":     "Polícia + Ministério Público",
    "saneamento":    "ANA + Ministério Público",
    "financas":      "Tribunal de Contas + Controladoria",
    "meio_ambiente": "IBAMA + Ministério Público",
    "cultura":       "Ministério da Cultura + Ministério Público",
    "outro":         "Ministério Público",
}


def rotear_denuncia(categoria: str) -> str:
    """Define o canal de destino inicial conforme a categoria."""
    return ROTAS_POR_CATEGORIA.get(categoria, "Ministério Público")
