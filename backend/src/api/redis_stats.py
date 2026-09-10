"""
Endpoint /api/redis-stats — Dashboard Redis.

Retorna métricas em tempo real do Redis (memória, conexões, comandos/s)
+ histórico em memória (últimas 60 medições) para alimentar o dashboard.
"""
import os
from datetime import datetime

from fastapi import APIRouter

import redis.asyncio as aioredis

router = APIRouter(prefix="/api", tags=["redis-stats"])

REDIS_URL = os.getenv("REDIS_URL", "redis://pc_redis:6379/0")
MAX_HIST = 60

_historico: dict = {"memory": [], "connections": []}
_redis: aioredis.Redis | None = None


async def _get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(REDIS_URL, decode_responses=True)
    return _redis


def _registrar(agora: str, mem_mb: float, conns: int) -> None:
    _historico["memory"].append({"time": agora, "memory_used": mem_mb})
    _historico["connections"].append({"time": agora, "connections": conns})
    for k in _historico:
        if len(_historico[k]) > MAX_HIST:
            _historico[k] = _historico[k][-MAX_HIST:]


@router.get("/redis-stats", summary="Estatísticas do Redis para o dashboard")
async def redis_stats() -> dict:
    r = await _get_redis()
    info = await r.info()

    mem_used = int(info.get("used_memory", 0))
    mem_total = int(
        info.get("total_system_memory", 0) or info.get("maxmemory", 0) or 0
    )
    if mem_total == 0:
        mem_total = int(info.get("used_memory_rss", mem_used))

    try:
        clients = await r.client_list()
        connections = len(clients) if isinstance(clients, list) else 0
    except Exception:
        connections = int(info.get("connected_clients", 0))

    cmds = int(info.get("instantaneous_ops_per_sec", 0))
    agora = datetime.now().strftime("%H:%M:%S")
    _registrar(agora, round(mem_used / 1024 / 1024, 2), connections)

    return {
        "memory_used": mem_used,
        "memory_total": mem_total,
        "connections": connections,
        "commands_per_second": cmds,
        "memory_history": list(_historico["memory"]),
        "connections_history": list(_historico["connections"]),
    }
