"""
Rotas de Votação — apoio/peso em denúncias, com gamificação e ranking.

Regras:
- Cada usuário vota UMA vez por denúncia (idempotente, atualiza se já votou)
- Peso (pontos) de 1 a 10 — usuários avançados podem dar peso maior
- Cada voto apoia o autor da denúncia (gamificação: +1 ponto no autor)
- Não pode votar na própria denúncia
"""
from typing import List, Optional
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, and_, or_, case
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_async_session
from src.models.voto import Voto
from src.models.denuncia import Denuncia
from src.models.usuario import Usuario, UserRole
from src.models.enums import StatusDenuncia
from src.schemas.voto import VotoCreate, VotoRead, VotoUpdate, RankingItem, VotoStats
from src.core.deps import get_current_active_user, require_moderator


router = APIRouter(prefix="/api/denuncias", tags=["votos"])


# Limite de peso conforme o papel do usuário
PESO_MAXIMO_POR_ROLE = {
    UserRole.CIDADAO: 3,
    UserRole.AVANCADO: 7,
    UserRole.MODERADOR: 10,
    UserRole.ADMIN: 10,
}


# =============================================================================
# VOTAR
# =============================================================================
@router.post(
    "/{denuncia_id}/votar",
    response_model=VotoRead,
    summary="Votar em uma denúncia (cria ou atualiza)",
)
async def votar(
    denuncia_id: int,
    dados: VotoCreate,
    current_user: Usuario = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> Voto:
    """
    Registra (ou atualiza) o voto do usuário autenticado.
    - O peso máximo depende do seu papel
    - Você não pode votar na própria denúncia
    - Cada voto dá pontos para o autor da denúncia (gamificação)
    """
    # Valida a denúncia
    denuncia = await session.get(Denuncia, denuncia_id)
    if not denuncia:
        raise HTTPException(status_code=404, detail="Denúncia não encontrada")

    # Bloqueia auto-voto
    if denuncia.autor_id == current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Você não pode votar na própria denúncia",
        )

    # Bloqueia denúncia em status final
    if denuncia.status in (StatusDenuncia.REJEITADA,):
        raise HTTPException(
            status_code=400,
            detail="Não é possível votar em denúncia rejeitada",
        )

    # Limita o peso conforme o papel
    peso_max = PESO_MAXIMO_POR_ROLE.get(current_user.role, 3)
    if dados.pontos > peso_max:
        raise HTTPException(
            status_code=403,
            detail=f"Seu papel permite peso máximo de {peso_max}. Atualize sua conta para votar com mais peso.",
        )

    # Verifica se já existe voto deste usuário
    result = await session.execute(
        select(Voto).where(
            and_(Voto.usuario_id == current_user.id, Voto.denuncia_id == denuncia_id)
        )
    )
    voto = result.scalar_one_or_none()

    # Garante que o voto (novo ou atualizado) está com apoio booleano coerente
    novo_apoio = dados.apoio
    novo_peso = dados.pontos

    if voto:
        # Devolve pontos antigos ao autor (se não era auto-voto, mas já filtramos isso)
        if voto.apoio and voto.pontos and denuncia.autor_id:
            autor_antigo = await session.get(Usuario, denuncia.autor_id)
            if autor_antigo:
                autor_antigo.pontos = max(0, autor_antigo.pontos - voto.pontos)
        elif not voto.apoio and voto.pontos and denuncia.autor_id:
            # Voto contra não dava pontos ao autor — nada a devolver
            pass

        # Atualiza
        voto.apoio = novo_apoio
        voto.pontos = novo_peso
    else:
        voto = Voto(
            usuario_id=current_user.id,
            denuncia_id=denuncia_id,
            apoio=novo_apoio,
            pontos=novo_peso,
        )
        session.add(voto)

    # Atualiza contador agregado na denúncia
    contagem = await _contar_votos(session, denuncia_id)
    denuncia.votos = contagem["score"]

    # Gamificação: se apoio, soma pontos ao autor
    if novo_apoio and novo_peso and denuncia.autor_id:
        autor = await session.get(Usuario, denuncia.autor_id)
        if autor:
            autor.pontos += novo_peso
            autor.nivel = _calcular_nivel(autor.pontos)

    await session.commit()
    await session.refresh(voto)
    return voto


# =============================================================================
# REMOVER VOTO
# =============================================================================
@router.delete(
    "/{denuncia_id}/votar",
    status_code=204,
    summary="Remover meu voto",
)
async def remover_voto(
    denuncia_id: int,
    current_user: Usuario = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> None:
    result = await session.execute(
        select(Voto).where(
            and_(Voto.usuario_id == current_user.id, Voto.denuncia_id == denuncia_id)
        )
    )
    voto = result.scalar_one_or_none()
    if not voto:
        raise HTTPException(status_code=404, detail="Você ainda não votou nesta denúncia")

    # Devolve pontos ao autor (se for voto de apoio)
    denuncia = await session.get(Denuncia, denuncia_id)
    if voto.apoio and voto.pontos and denuncia and denuncia.autor_id:
        autor = await session.get(Usuario, denuncia.autor_id)
        if autor:
            autor.pontos = max(0, autor.pontos - voto.pontos)
            autor.nivel = _calcular_nivel(autor.pontos)

    await session.delete(voto)

    # Recalcula contador
    if denuncia:
        contagem = await _contar_votos(session, denuncia_id)
        denuncia.votos = contagem["score"]

    await session.commit()


# =============================================================================
# ESTATÍSTICAS DE UMA DENÚNCIA
# =============================================================================
@router.get(
    "/{denuncia_id}/votos/stats",
    response_model=VotoStats,
    summary="Estatísticas de votos de uma denúncia",
)
async def stats_votos(
    denuncia_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> VotoStats:
    contagem = await _contar_votos(session, denuncia_id)
    return VotoStats(
        denuncia_id=denuncia_id,
        apoio=contagem["apoio"],
        contra=contagem["contra"],
        total=contagem["total"],
        score=contagem["score"],
        pontuacao_total=contagem["pontuacao_total"],
        votaram=[],  # público não vê quem votou
    )


@router.get(
    "/{denuncia_id}/votos",
    response_model=VotoStats,
    summary="Estatísticas + lista de quem votou (moderador+)",
)
async def stats_votos_mod(
    denuncia_id: int,
    current_user: Usuario = Depends(require_moderator),
    session: AsyncSession = Depends(get_async_session),
) -> VotoStats:
    contagem = await _contar_votos(session, denuncia_id)
    result = await session.execute(
        select(Voto.usuario_id).where(Voto.denuncia_id == denuncia_id)
    )
    return VotoStats(
        denuncia_id=denuncia_id,
        apoio=contagem["apoio"],
        contra=contagem["contra"],
        total=contagem["total"],
        score=contagem["score"],
        pontuacao_total=contagem["pontuacao_total"],
        votaram=[uid for uid, in result.all()],
    )


# =============================================================================
# RANKING
# =============================================================================
@router.get(
    "/ranking/engajamento",
    response_model=List[RankingItem],
    summary="Ranking de denúncias por engajamento",
)
async def ranking_engajamento(
    categoria: Optional[str] = Query(None),
    estado: Optional[str] = Query(None, description="UF"),
    municipio: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_async_session),
) -> list[RankingItem]:
    """
    Lista as denúncias mais engajadas (maior score de apoio).
    Critério de desempate: visualizações.
    """
    stmt = (
        select(
            Denuncia.id.label("denuncia_id"),
            Denuncia.titulo,
            Denuncia.categoria,
            Denuncia.codigo_rastreio,
            Denuncia.votos.label("score_apoio"),
            func.coalesce(func.sum(case((Voto.apoio == False, Voto.pontos), else_=0)), 0).label("score_contra"),
            func.count(Voto.id).label("total_votos"),
            Denuncia.visualizacoes,
            Denuncia.municipio,
            Denuncia.estado,
        )
        .select_from(Denuncia)
        .outerjoin(Voto, Voto.denuncia_id == Denuncia.id)
        .where(Denuncia.publica == True)
        .group_by(Denuncia.id)
        .order_by(Denuncia.votos.desc(), Denuncia.visualizacoes.desc())
        .limit(limit)
    )

    if categoria:
        stmt = stmt.where(Denuncia.categoria == categoria)
    if estado:
        stmt = stmt.where(Denuncia.estado == estado.upper())
    if municipio:
        stmt = stmt.where(Denuncia.municipio.ilike(f"%{municipio}%"))

    result = await session.execute(stmt)
    rows = result.all()

    ranking = []
    for row in rows:
        ranking.append(
            RankingItem(
                denuncia_id=row.denuncia_id,
                titulo=row.titulo,
                categoria=row.categoria.value if hasattr(row.categoria, "value") else str(row.categoria),
                codigo_rastreio=row.codigo_rastreio,
                score_apoio=row.score_apoio or 0,
                score_contra=row.score_contra or 0,
                score_total=(row.score_apoio or 0) - (row.score_contra or 0),
                total_votos=row.total_votos or 0,
                visualizacoes=row.visualizacoes,
                municipio=row.municipio,
                estado=row.estado,
            )
        )
    return ranking


# =============================================================================
# HELPERS
# =============================================================================
async def _contar_votos(session: AsyncSession, denuncia_id: int) -> dict:
    """Conta votos agrupados por apoio/contra."""
    # Apoio
    result_apoio = await session.execute(
        select(func.count(Voto.id), func.coalesce(func.sum(Voto.pontos), 0))
        .where(and_(Voto.denuncia_id == denuncia_id, Voto.apoio == True))
    )
    qtd_apoio, peso_apoio = result_apoio.one()

    # Contra
    result_contra = await session.execute(
        select(func.count(Voto.id), func.coalesce(func.sum(Voto.pontos), 0))
        .where(and_(Voto.denuncia_id == denuncia_id, Voto.apoio == False))
    )
    qtd_contra, peso_contra = result_contra.one()

    return {
        "apoio": qtd_apoio or 0,
        "contra": qtd_contra or 0,
        "total": (qtd_apoio or 0) + (qtd_contra or 0),
        "score": (qtd_apoio or 0) - (qtd_contra or 0),
        "pontuacao_total": (peso_apoio or 0) + (peso_contra or 0),
    }


def _calcular_nivel(pontos: int) -> int:
    """
    Calcula o nível baseado nos pontos.
    Curva: a cada 100 pontos sobe de nível. Nível 1 começa com 0.
    """
    return max(1, (pontos // 100) + 1)
