"""
Servico de estatisticas agregadas (publico, sem dados sensiveis) - v2.1.
Cada query em transacao isolada para evitar abort em cascata.
"""
from datetime import datetime, timezone
from typing import List

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.denuncia import Denuncia
from src.db.models.area import Area
from src.db.models.usuario import Usuario
from src.db.models.enums import StatusDenuncia
from src.schemas.stats import (
    StatsGerais,
    StatsPorMes,
    StatsPorArea,
    StatsPorCategoria,
    StatsPorEstado,
    StatsTopMunicipio,
    StatsTopUsuario,
    StatsFarejos,
    StatsEngajamento,
    StatsRead,
)


async def _safe_count(session: AsyncSession, table_name: str) -> int:
    """COUNT(*) em SQL puro com rollback explicito em caso de erro."""
    try:
        result = await session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        return int(result.scalar_one() or 0)
    except Exception as e:
        await session.rollback()
        print(f"[stats] Tabela {table_name} indisponivel: {e}")
        return 0


async def _safe_distinct_count(session: AsyncSession, table_name: str, column: str) -> int:
    """COUNT(DISTINCT column) em SQL puro com rollback explicito."""
    try:
        result = await session.execute(
            text(f"SELECT COUNT(DISTINCT {column}) FROM {table_name}")
        )
        return int(result.scalar_one() or 0)
    except Exception as e:
        await session.rollback()
        print(f"[stats] {table_name}.{column} indisponivel: {e}")
        return 0


async def _safe_query(session: AsyncSession, sql: str, fetch_all: bool = True):
    """Query SQL pura com rollback em caso de erro."""
    try:
        result = await session.execute(text(sql))
        if fetch_all:
            return result.fetchall()
        return result.scalar_one()
    except Exception as e:
        await session.rollback()
        print(f"[stats] Query falhou: {e}")
        return [] if fetch_all else 0


# ----- v1.0 (mantido) -----

async def stats_gerais(session: AsyncSession) -> StatsGerais:
    total = (await session.execute(select(func.count(Denuncia.id)))).scalar_one()
    publicas = (await session.execute(
        select(func.count(Denuncia.id)).where(Denuncia.publica == True)  # noqa: E712
    )).scalar_one()
    anonimas = (await session.execute(
        select(func.count(Denuncia.id)).where(Denuncia.anonima == True)  # noqa: E712
    )).scalar_one()
    aguardando = (await session.execute(
        select(func.count(Denuncia.id)).where(Denuncia.status == StatusDenuncia.AGUARDANDO)
    )).scalar_one()
    em_analise = (await session.execute(
        select(func.count(Denuncia.id)).where(Denuncia.status == StatusDenuncia.EM_ANALISE)
    )).scalar_one()
    resolvidas = (await session.execute(
        select(func.count(Denuncia.id)).where(Denuncia.status == StatusDenuncia.RESOLVIDA)
    )).scalar_one()
    retiradas = (await session.execute(
        select(func.count(Denuncia.id)).where(Denuncia.status_remocao == "retirada_pelo_autor")
    )).scalar_one()
    canceladas = (await session.execute(
        select(func.count(Denuncia.id)).where(Denuncia.status_remocao == "cancelada_por_coacao")
    )).scalar_one()
    pedidos_pendentes = (await session.execute(
        select(func.count(Denuncia.id)).where(
            Denuncia.pedido_retirada_em.isnot(None),
            Denuncia.status_remocao.is_(None),
        )
    )).scalar_one()
    areas_com_denuncias = (await session.execute(
        select(func.count(func.distinct(Denuncia.area_id))).where(Denuncia.area_id.isnot(None))
    )).scalar_one()
    usuarios = (await session.execute(select(func.count(Usuario.id)))).scalar_one()

    return StatsGerais(
        total_denuncias=total,
        denuncias_publicas=publicas,
        denuncias_anonimas=anonimas,
        denuncias_aguardando=aguardando,
        denuncias_em_analise=em_analise,
        denuncias_resolvidas=resolvidas,
        denuncias_retiradas=retiradas,
        denuncias_canceladas_coacao=canceladas,
        pedidos_retirada_pendentes=pedidos_pendentes,
        areas_ativas=areas_com_denuncias,
        usuarios_cadastrados=usuarios,
    )


async def stats_por_mes(session: AsyncSession) -> List[StatsPorMes]:
    rows = await _safe_query(session, """
        SELECT TO_CHAR(created_at, 'YYYY-MM') AS mes,
               COUNT(*) AS total,
               COUNT(*) FILTER (WHERE publica = true) AS publicas,
               COUNT(*) FILTER (WHERE anonima = true) AS anonimas
        FROM denuncias
        GROUP BY TO_CHAR(created_at, 'YYYY-MM')
        ORDER BY mes DESC
        LIMIT 24
    """)
    return [
        StatsPorMes(mes=row.mes, total=row.total, publicas=row.publicas, anonimas=row.anonimas)
        for row in rows
    ]


async def stats_por_area(session: AsyncSession) -> List[StatsPorArea]:
    rows = await _safe_query(session, """
        SELECT a.id AS area_id, a.nome AS area_nome, a.slug AS area_slug,
               COUNT(d.id) AS total
        FROM areas a
        LEFT JOIN denuncias d ON d.area_id = a.id
        GROUP BY a.id, a.nome, a.slug
        HAVING COUNT(d.id) > 0
        ORDER BY total DESC
    """)
    total_geral = sum(r.total for r in rows) or 1
    return [
        StatsPorArea(
            area_id=r.area_id, area_nome=r.area_nome, area_slug=r.area_slug,
            total=r.total, percentual=round((r.total / total_geral) * 100, 2),
        )
        for r in rows
    ]


async def stats_por_categoria(session: AsyncSession) -> List[StatsPorCategoria]:
    rows = await _safe_query(session, """
        SELECT categoria, COUNT(*) AS total
        FROM denuncias
        WHERE categoria IS NOT NULL
        GROUP BY categoria
        ORDER BY total DESC
    """)
    total_geral = sum(r.total for r in rows) or 1
    return [
        StatsPorCategoria(
            categoria=r.categoria, total=r.total,
            percentual=round((r.total / total_geral) * 100, 2),
        )
        for r in rows
    ]


# ----- v2.0 (robustos) -----

async def stats_por_estado(session: AsyncSession) -> List[StatsPorEstado]:
    rows = await _safe_query(session, """
        SELECT estado, COUNT(*) AS total
        FROM denuncias
        WHERE estado IS NOT NULL AND estado != ''
        GROUP BY estado
        ORDER BY total DESC
        LIMIT 27
    """)
    total_geral = sum(r.total for r in rows) or 1
    return [
        StatsPorEstado(
            estado=r.estado, total=r.total,
            percentual=round((r.total / total_geral) * 100, 2),
        )
        for r in rows
    ]


async def stats_top_municipios(session: AsyncSession) -> List[StatsTopMunicipio]:
    rows = await _safe_query(session, """
        SELECT municipio, estado, COUNT(*) AS total
        FROM denuncias
        WHERE municipio IS NOT NULL AND municipio != ''
        GROUP BY municipio, estado
        ORDER BY total DESC
        LIMIT 10
    """)
    return [
        StatsTopMunicipio(municipio=r.municipio, estado=r.estado or "N/I", total=r.total)
        for r in rows
    ]


async def stats_top_usuarios(session: AsyncSession) -> List[StatsTopUsuario]:
    """Top 10 cidadaos - via ORM (sem SQL puro, mais robusto)."""
    try:
        from src.db.models.comentario import Comentario
        sql = text("""
            SELECT
                u.id AS usuario_id,
                u.nome AS nome,
                COUNT(DISTINCT d.id) AS total_denuncias,
                COUNT(DISTINCT c.id) AS total_comentarios
            FROM usuarios u
            LEFT JOIN denuncias d ON d.autor_id = u.id AND d.anonima = false
            LEFT JOIN comentarios c ON c.autor_id = u.id
            GROUP BY u.id, u.nome
            HAVING COUNT(DISTINCT d.id) > 0 OR COUNT(DISTINCT c.id) > 0
            ORDER BY total_denuncias DESC, total_comentarios DESC
            LIMIT 10
        """)
        rows = await _safe_query(session, str(sql))
    except Exception as e:
        await session.rollback()
        print(f"[stats] top_usuarios sem join de comentarios: {e}")
        rows = await _safe_query(session, """
            SELECT id AS usuario_id, nome,
                   0 AS total_denuncias,
                   0 AS total_comentarios
            FROM usuarios
            ORDER BY criado_em DESC
            LIMIT 10
        """)

    return [
        StatsTopUsuario(
            usuario_id=r.usuario_id,
            nome=r.nome,
            total_denuncias=r.total_denuncias or 0,
            total_comentarios=r.total_comentarios or 0,
            pontos_cidadania=(r.total_denuncias or 0) * 10 + (r.total_comentarios or 0) * 2,
        )
        for r in rows
    ]


async def stats_farejos(session: AsyncSession) -> StatsFarejos:
    """Saude do farejador de corrupcao."""
    try:
        from src.db.models.faro import Faro, StatusFaro
        total = (await session.execute(select(func.count(Faro.id)))).scalar_one()
        ativos = (await session.execute(
            select(func.count(Faro.id)).where(Faro.status == StatusFaro.EM_ANALISE)
        )).scalar_one()
        investigados = (await session.execute(
            select(func.count(Faro.id)).where(Faro.status == StatusFaro.INVESTIGADO)
        )).scalar_one()

        rows = await _safe_query(session, """
            SELECT heuristica, COUNT(*) AS total
            FROM faros
            WHERE heuristica IS NOT NULL AND heuristica != ''
            GROUP BY heuristica
            ORDER BY total DESC
        """)
        heuristicas = [
            StatsPorCategoria(categoria=r.heuristica, total=r.total, percentual=0.0)
            for r in rows
        ]
    except Exception as e:
        await session.rollback()
        print(f"[stats] farejos indisponivel: {e}")
        total = ativos = investigados = 0
        heuristicas = []

    return StatsFarejos(
        total_faros=total,
        faros_ativos=ativos,
        faros_em_analise=ativos,
        faros_investigados=investigados,
        por_heuristica=heuristicas,
    )


async def stats_engajamento(session: AsyncSession) -> StatsEngajamento:
    """Qualidade do sistema - cada query em transacao isolada."""
    # Cada _safe_* faz seu proprio rollback em caso de erro
    den_com_comentarios = await _safe_distinct_count(session, "comentarios", "denuncia_id")
    den_com_votos = await _safe_distinct_count(session, "votos", "denuncia_id")
    total_comentarios = await _safe_count(session, "comentarios")
    total_votos = await _safe_count(session, "votos")

    # Total de visualizacoes (vai funcionar mesmo se as outras falharem)
    try:
        total_visualizacoes = (await session.execute(
            select(func.coalesce(func.sum(Denuncia.visualizacoes), 0))
        )).scalar_one() or 0
    except Exception:
        await session.rollback()
        total_visualizacoes = 0

    total_denuncias = (await session.execute(select(func.count(Denuncia.id)))).scalar_one() or 1

    return StatsEngajamento(
        denuncias_com_comentarios=den_com_comentarios,
        denuncias_com_votos=den_com_votos,
        total_comentarios=total_comentarios,
        total_votos=total_votos,
        total_visualizacoes=total_visualizacoes,
        media_comentarios_por_denuncia=round(total_comentarios / total_denuncias, 2),
        media_visualizacoes_por_denuncia=round(total_visualizacoes / total_denuncias, 2),
    )


# ----- agregador principal -----

async def estatisticas_completas(session: AsyncSession) -> StatsRead:
    """Cada sub-statistica faz seu proprio rollback se falhar."""
    geral = await stats_gerais(session)
    por_mes = await stats_por_mes(session)
    por_area = await stats_por_area(session)
    por_categoria = await stats_por_categoria(session)
    por_estado = await stats_por_estado(session)
    top_municipios = await stats_top_municipios(session)
    top_usuarios = await stats_top_usuarios(session)
    farejos = await stats_farejos(session)
    engajamento = await stats_engajamento(session)
    return StatsRead(
        geral=geral,
        por_mes=por_mes,
        por_area=por_area,
        por_categoria=por_categoria,
        por_estado=por_estado,
        top_municipios=top_municipios,
        top_usuarios=top_usuarios,
        farejos=farejos,
        engajamento=engajamento,
        ultima_atualizacao=datetime.now(timezone.utc),
    )
