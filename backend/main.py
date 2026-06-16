"""
Aplicação principal FastAPI — Projeto Cidadão.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.db.config import settings
from src.db.session import async_engine
from src.api import auth, users, areas, cursos, denuncias, comentarios, faros


# -----------------------------------------------------------------------------
# Lifespan — inicializa e finaliza recursos
# -----------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ações no startup/shutdown."""
    print("🚀 Projeto Cidadão API iniciando...")
    yield
    print("👋 Encerrando conexão com o banco...")
    await async_engine.dispose()


# -----------------------------------------------------------------------------
# App
# -----------------------------------------------------------------------------
app = FastAPI(
    title="🇧🇷 Projeto Cidadão",
    description=(
        "API de transparência pública, fiscalização cidadã e educação para o controle social.\n\n"
        "**Funcionalidades:**\n"
        "- Autenticação JWT\n"
        "- CRUD de denúncias com geolocalização\n"
        "- Áreas temáticas (Saúde, Educação, etc.)\n"
        "- Cursos de capacitação\n"
        "- Comentários em thread\n"
        "- Farejador de Corrupção (sinais automatizados)"
    ),
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# -----------------------------------------------------------------------------
# CORS
# -----------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.app_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------------------------------------------------------
# Health check
# -----------------------------------------------------------------------------
@app.get("/health", tags=["health"], summary="Verificar saúde da API")
async def health() -> dict:
    """Endpoint de health check (usado pelo Docker)."""
    return {
        "status": "ok",
        "service": "projeto-cidadao-api",
        "version": "0.1.0",
        "env": settings.app_env,
    }


@app.get("/", tags=["health"], summary="Boas-vindas")
async def root() -> dict:
    return {
        "message": "🇧🇷 Projeto Cidadão — API de transparência pública",
        "docs": "/docs",
        "health": "/health",
    }


# -----------------------------------------------------------------------------
# Routers
# -----------------------------------------------------------------------------
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(areas.router)
app.include_router(cursos.router)
app.include_router(denuncias.router)
app.include_router(comentarios.router)
app.include_router(faros.router)


# -----------------------------------------------------------------------------
# Exception handlers
# -----------------------------------------------------------------------------
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Recurso não encontrado", "path": str(request.url.path)},
    )
