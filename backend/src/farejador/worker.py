"""
Worker principal do Farejador de Corrupção.

Responsabilidades:
- Varrer denúncias recentes e aplicar heurísticas
- Ingerir contratos públicos
- Persistir faros no banco
- Idempotência via referência + tipo_entidade
"""
import asyncio
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import async_session
from src.models.denuncia import Denuncia
from src.models.faro import Faro
from src.models.enums import StatusFaro
from src.farejador.heuristicas import (
    avaliar_texto_denuncia,
    avaliar_padroes_contrato,
)


async def varrer_denuncias_recentes(
    session: AsyncSession,
    horas: int = 24,
    min_score: int = 30,
) -> List[Faro]:
    """Varre denúncias das últimas N horas e cria faros para as suspeitas."""
    desde = datetime.now(timezone.utc) - timedelta(hours=horas)
    result = await session.execute(
        select(Denuncia).where(
            and_(Denuncia.created_at >= desde, Denuncia.publica == True)
        )
    )
    denuncias = list(result.scalars().all())

    faros_criados: list[Faro] = []
    for d in denuncias:
        existing = await session.execute(
            select(Faro).where(
                and_(Faro.denuncia_id == d.id, Faro.tipo_entidade == "denuncia")
            )
        )
        if existing.scalar_one_or_none():
            continue

        resultado = avaliar_texto_denuncia(
            titulo=d.titulo,
            descricao=d.descricao,
            categoria=d.categoria.value if hasattr(d.categoria, "value") else str(d.categoria),
        )

        if resultado.score_risco < min_score:
            continue

        faro = Faro(
            tipo_entidade="denuncia",
            referencia_id=str(d.id),
            entidade_nome=d.titulo[:255],
            heuristicas=resultado.heuristicas,
            evidencia=resultado.evidencia,
            score_risco=resultado.score_risco,
            severidade=resultado.severidade,
            status=StatusFaro.NOVO,
            denuncia_id=d.id,
            data_deteccao=datetime.now(timezone.utc),
        )
        session.add(faro)
        faros_criados.append(faro)

    await session.commit()
    for f in faros_criados:
        await session.refresh(f)
    return faros_criados


async def varrer_contratos_publicos(
    session: AsyncSession,
    contratos: List[Dict[str, Any]] | None = None,
    min_score: int = 40,
) -> List[Faro]:
    """Recebe contratos (vindos do Portal da Transparência/ComprasNet) e cria faros."""
    contratos = contratos or _contratos_exemplo_stub()

    faros_criados: list[Faro] = []
    for c in contratos:
        chave = c.get("id_contrato") or c.get("numero")
        if not chave:
            continue
        existing = await session.execute(
            select(Faro).where(
                and_(Faro.tipo_entidade == "contrato", Faro.referencia_id == str(chave))
            )
        )
        if existing.scalar_one_or_none():
            continue

        resultado = avaliar_padroes_contrato(c)
        if resultado.score_risco < min_score:
            continue

        faro = Faro(
            tipo_entidade="contrato",
            referencia_id=str(chave),
            entidade_nome=c.get("objeto", "")[:255],
            heuristicas=resultado.heuristicas,
            evidencia=resultado.evidencia,
            score_risco=resultado.score_risco,
            severidade=resultado.severidade,
            status=StatusFaro.NOVO,
            data_deteccao=datetime.now(timezone.utc),
        )
        session.add(faro)
        faros_criados.append(faro)

    await session.commit()
    for f in faros_criados:
        await session.refresh(f)
    return faros_criados


def _contratos_exemplo_stub() -> list[dict]:
    """Stub com dados de exemplo (substituir por chamada real à API de dados abertos)."""
    return [
        {
            "id_contrato": "CT-2026-001",
            "objeto": "Prestação de serviços diversos",
            "valor_original": 1_500_000,
            "valor_total": 2_100_000,
            "qtd_aditivos": 4,
            "prazo_dias": 7,
            "empresa_id": "12.345.678/0001-90",
            "contratos_mesma_empresa_ano": 8,
        },
    ]


async def executar_farejador(
    horas: int = 24,
    incluir_contratos: bool = True,
) -> dict:
    """Executa uma passada completa do farejador."""
    async with async_session() as session:
        faros_denuncias = await varrer_denuncias_recentes(session, horas=horas)
        faros_contratos: list[Faro] = []
        if incluir_contratos:
            faros_contratos = await varrer_contratos_publicos(session)

    return {
        "executado_em": datetime.now(timezone.utc).isoformat(),
        "janela_horas": horas,
        "faros_criados": {
            "denuncias": len(faros_denuncias),
            "contratos": len(faros_contratos),
            "total": len(faros_denuncias) + len(faros_contratos),
        },
        "ids_faros": [f.id for f in faros_denuncias + faros_contratos],
    }


if __name__ == "__main__":
    print("🕵️  Executando Farejador de Corrupção...")
    resultado = asyncio.run(executar_farejador())
    print(f"✅ Concluído: {resultado['faros_criados']['total']} faros criados")
