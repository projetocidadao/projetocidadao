\"""
Utils - Funções utilitárias para integrações
- Cache
- Rate limiting
- Autenticação
"""
import time
from typing import Optional, Dict, Any
from functools import wraps
import httpx

# Cache em memória simples
_cache: Dict[str, tuple[Any, float]] = {}
CACHE_TTL = 300  # 5 minutos


def get_cached(key: str) -> Optional[Any]:
    """Retorna valor do cache se ainda válido"""
    if key in _cache:
        value, timestamp = _cache[key]
        if time.time() - timestamp < CACHE_TTL:
            return value
        del _cache[key]
    return None


def set_cache(key: str, value: Any):
    """Armazena valor no cache"""
    _cache[key] = (value, time.time())


def clear_cache():
    """Limpa todo o cache"""
    _cache.clear()


# Rate limiting simples
_request_times: list = []
MAX_REQUESTS = 60  # por minuto
WINDOW = 60  # segundos


def check_rate_limit() -> bool:
    """Verifica se pode fazer requisição"""
    now = time.time()
    global _request_times
    
    # Remove requisições antigas
    _request_times = [t for t in _request_times if now - t < WINDOW]
    
    if len(_request_times) >= MAX_REQUESTS:
        return False
    
    _request_times.append(now)
    return True


def rate_limit(func):
    """Decorator para rate limiting"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if not check_rate_limit():
            raise Exception("Rate limit excedido. Aguarde um momento.")
        return await func(*args, **kwargs)
    return wrapper


# Headers padrão para APIs governamentais
DEFAULT_HEADERS = {
    "Accept": "application/json",
    "User-Agent": "Projeto-Cidadao/1.0"
}


async def fetch_with_cache(url: str, params: Optional[Dict] = None) -> Dict:
    """Faz requisição HTTP com cache"""
    cache_key = f"{url}:{str(params)}"
    
    cached = get_cached(cache_key)
    if cached:
        return cached
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, headers=DEFAULT_HEADERS)
        response.raise_for_status()
        data = response.json()
        set_cache(cache_key, data)
        return data