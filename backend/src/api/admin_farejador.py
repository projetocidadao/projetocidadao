"""
Rotas administrativas do Farejador — executa heurísticas manualmente e gerencia scheduler.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from src.farejador.worker import executar_farejador, varrer_denuncias_recentes, varrer_contratos_publicos
from src.farejador.scheduler import iniciar_scheduler, parar_scheduler, status_scheduler
from src.farejador.heuristicas import HEURISTICAS_DISPONIVEIS
from src.core.deps import require_admin
from src.db.models.usuario import Usuario
from src.db.session import AsyncSessionLocal


router = APIRouter(prefix="/api/admin/farejador", tags=["admin:farejador"])


class ExecutarFarejadorRequest(BaseModel):
    horas: int = Field(default=24, ge=1, le=168)
    incluir_contratos: bool = True
    min_score: int = Field(default=30, ge=0, le=100)


class ExecutarFarejadorResponse(BaseModel):
    executado_em: str
    janela_horas: int
    faros_criados: dict
    ids_faros: list[int]


@router.post(
    "/executar",
    response_model=ExecutarFarejadorResponse,
    summary="Rodar farejador manualmente (admin)",
)
async def executar(
    payload: ExecutarFarejadorRequest = ExecutarFarejadorRequest(),
    current_user: Usuario = Depends(require_admin),
) -> ExecutarFarejadorResponse:
    try:
        resultado = await executar_farejador(
            horas=payload.horas,
            incluir_contratos=payload.incluir_contratos,
        )
        return ExecutarFarejadorResponse(**resultado)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao executar farejador: {e}")


@router.post("/varrer/denuncias", summary="Apenas varrer denúncias recentes")
async def varrer_denuncias(
    horas: int = 24,
    current_user: Usuario = Depends(require_admin),
) -> dict:
    async with AsyncSessionLocal() as session:
        faros = await varrer_denuncias_recentes(session, horas=horas)
    return {"total": len(faros), "ids": [f.id for f in faros]}


@router.post("/varrer/contratos", summary="Apenas varrer contratos (stub)")
async def varrer_contratos(
    current_user: Usuario = Depends(require_admin),
) -> dict:
    async with AsyncSessionLocal() as session:
        faros = await varrer_contratos_publicos(session)
    return {"total": len(faros), "ids": [f.id for f in faros]}


@router.get("/heuristicas", summary="Listar heurísticas disponíveis")
async def listar_heuristicas(
    current_user: Usuario = Depends(require_admin),
) -> dict:
    return {
        "total": len(HEURISTICAS_DISPONIVEIS),
        "heuristicas": [
            {
                "id": k,
                "nome": v["nome"],
                "descricao": v["descricao"],
                "peso": v["peso"],
            }
            for k, v in HEURISTICAS_DISPONIVEIS.items()
        ],
    }


@router.get("/scheduler", summary="Status do scheduler")
async def scheduler_status(
    current_user: Usuario = Depends(require_admin),
) -> dict:
    return status_scheduler()


@router.post("/scheduler/iniciar", summary="Iniciar scheduler")
async def scheduler_iniciar(
    cron: str = "0 */6 * * *",
    tz: str = "America/Sao_Paulo",
    current_user: Usuario = Depends(require_admin),
) -> dict:
    iniciar_scheduler(cron_expression=cron, timezone=tz)
    return {"message": "Scheduler iniciado", "cron": cron, "tz": tz}


@router.post("/scheduler/parar", summary="Parar scheduler")
async def scheduler_parar(
    current_user: Usuario = Depends(require_admin),
) -> dict:
    parar_scheduler()
    return {"message": "Scheduler parado"}
