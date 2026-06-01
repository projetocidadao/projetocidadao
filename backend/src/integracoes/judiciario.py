\"""
Módulo Judiciário - Integrações com dados do Judiciário
- CNJ (Conselho Nacional de Justiça)
- Tribunais (PJe, TJ's)
"""
from fastapi import APIRouter, HTTPException
import httpx
from typing import Optional

router = APIRouter()

# CNJ API
CNJ_API = "https://api.cnj.jus.br"


@router.get("/cnj/tribunais")
async def get_tribunais():
    """Lista todos os tribunais do Brasil"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{CNJ_API}/v1/tribunais",
                headers={"Accept": "application/json"}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/cnj/processos")
async def get_processos(
    tribunal: Optional[str] = None,
    ano: Optional[int] = None,
    classe: Optional[str] = None
):
    """Consulta processos (dados agregados)"""
    params = {}
    if tribunal:
        params["tribunal"] = tribunal
    if ano:
        params["ano"] = ano
    if classe:
        params["classe"] = classe
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{CNJ_API}/v1/processos",
                params=params,
                headers={"Accept": "application/json"}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/cnj/estatisticas")
async def get_estatisticas(
    tribunal: Optional[str] = None,
    periodo: Optional[str] = None
):
    """Consulta estatísticas processuais"""
    params = {}
    if tribunal:
        params["tribunal"] = tribunal
    if periodo:
        params["periodo"] = periodo
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{CNJ_API}/v1/estatisticas",
                params=params,
                headers={"Accept": "application/json"}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/pje/{tribunal}/processos/{numero}")
async def get_processo_pje(tribunal: str, numero: str):
    """Consulta processo específico no PJe"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"https://pje.{tribunal}.jus.br/api/processos/{numero}",
                headers={"Accept": "application/json"}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=str(e))