\"""
Módulo Executivo - Integrações com dados do Executivo
- Portal da Transparência
- Compras Governamentais
"""
from fastapi import APIRouter, HTTPException
import httpx
from typing import Optional

router = APIRouter()

# Portal da Transparência API
TRANSPARENCIA_API = "https://portaldatransparencia.gov.br/api-de-dados"

# Compras Governamentais API
COMPRAS_API = "https://compras.gov.br/api"


@router.get("/transparencia/bolsa-familia")
async def get_bolsa_familia(cpf: Optional[str] = None, nis: Optional[str] = None):
    """Consulta benefícios do Bolsa Família"""
    params = {}
    if cpf:
        params["cpf"] = cpf
    if nis:
        params["nis"] = nis
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{TRANSPARENCIA_API}/bolsa-familia",
                params=params
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/transparencia/convenios")
async def get_convenios(cnpj_favorecido: Optional[str] = None, mes: Optional[str] = None):
    """Consulta convênios e transferências"""
    params = {}
    if cnpj_favorecido:
        params["cnpjFavorecido"] = cnpj_favorecido
    if mes:
        params["mes"] = mes
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{TRANSPARENCIA_API}/convenios",
                params=params
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/compras/licitacoes")
async def get_licitacoes(
    ua: Optional[str] = None,
    modalidae: Optional[str] = None,
    ano: Optional[int] = None
):
    """Consulta licitações públicas"""
    params = {}
    if ua:
        params["ua"] = ua
    if modalidae:
        params["modalidade"] = modalidae
    if ano:
        params["ano"] = ano
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{COMPRAS_API}/licitacoes",
                params=params
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/compras/contratos")
async def get_contratos(
    id_licitacao: Optional[str] = None,
    cnpj: Optional[str] = None
):
    """Consulta contratos públicos"""
    params = {}
    if id_licitacao:
        params["idLicitacao"] = id_licitacao
    if cnpj:
        params["cnpj"] = cnpj
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{COMPRAS_API}/contratos",
                params=params
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=str(e))