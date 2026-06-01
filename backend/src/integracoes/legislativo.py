\"""
Módulo Legislativo - Integrações com dados do Legislativo
- Câmara dos Deputados
- Senado Federal
"""
from fastapi import APIRouter, HTTPException
import httpx
from typing import Optional

router = APIRouter()

# Câmara dos Deputados API
CAMARA_API = "https://dadosabertos.camara.leg.br/api/v2"

# Senado Federal API
SENADO_API = "https://legiscam.senado.leg.br/doc"


@router.get("/camara/deputados")
async def get_deputados(nome: Optional[str] = None, estado: Optional[str] = None):
    """Lista deputados atuais"""
    params = {"itens": 100}
    if nome:
        params["nome"] = nome
    if estado:
        params["siglaUf"] = estado
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{CAMARA_API}/deputados",
                params=params,
                headers={"Accept": "application/json"}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/camara/proposicoes")
async def get_proposicoes(
    ano: Optional[int] = None,
    tipo: Optional[str] = None,
    autor: Optional[str] = None
):
    """Consulta proposições legislativas"""
    params = {"itens": 100}
    if ano:
        params["ano"] = ano
    if tipo:
        params["siglaTipo"] = tipo
    if autor:
        params["autor"] = autor
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{CAMARA_API}/proposicoes",
                params=params,
                headers={"Accept": "application/json"}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/camara/votacoes/{id_proposicao}")
async def get_votacoes(id_proposicao: str):
    """Consulta votações de uma proposição"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{CAMARA_API}/proposicoes/{id_proposicao}/votacoes",
                headers={"Accept": "application/json"}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/senado/senadores")
async def get_senadores(nome: Optional[str] = None):
    """Lista senators atuais"""
    params = {}
    if nome:
        params["nome"] = nome
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{SENADO_API}/senadores",
                params=params
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/senado/proposicoes")
async def get_proposicoes_senado(
    ano: Optional[int] = None,
    tipo: Optional[str] = None
):
    """Consulta proposições do Senado"""
    params = {}
    if ano:
        params["ano"] = ano
    if tipo:
        params["tipo"] = tipo
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{SENADO_API}/materias",
                params=params
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=str(e))