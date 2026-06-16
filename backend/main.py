"""
Aplicação principal FastAPI — Projeto Cidadão.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.db.config import settings
from src.db.session import async_engine
from src.api import auth, users, areas, cursos, denuncias, comentarios, faros, votos, anexos
from src.api import admin_farejador

try:
    from src.farejador.scheduler import iniciar_scheduler, parar_scheduler
    FAREJADOR_DISPONIVEL = True
except ImportError:
    FAREJADOR_DISPONIVEL = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Projeto Cidadão API iniciando...")

    if getattr(settings, "farejador_scheduler_enabled", True) and FAREJADOR_DISPONIVEL:
        try:
            iniciar_scheduler(
                cron_expression=getattr(settings, "farejador_cron", "0 */6 * * *"),
                timezone=getattr(settings, "farejador_timezone", "America/Sao_Paulo"),
            )
            print("🕵️  Farejador de Corrupção: scheduler ATIVO")
        except Exception as e:
            print(f"⚠️  Falha ao iniciar scheduler do farejador: {e}")

    yield

    if FAREJADOR_DISPONIVEL:
        try:
            parar_scheduler()
        except Exception:
            pass

    print("👋 Encerrando conexão com o banco...")
    await async_engine.dispose()


app = FastAPI(
    title="🇧🇷 Projeto Cidadão",
    description=(
        "API de transparência pública, fiscalização cidadã e educação para o controle social.\n\n"
        "**Funcionalidades:**\n"
        "- Autenticação JWT\n"
        "- CRUD de denúncias com geolocalização\n"
        "- Votação com gamificação e ranking\n"
        "- Upload de anexos (S3-compatible + dedup por SHA256)\n"
        "- Áreas temáticas (Saúde, Educação, etc.)\n"
        "- Cursos de capacitação\n"
        "- Comentários em thread\n"
        "- Farejador de Corrupção (heurísticas + scheduler automático)"
    ),
    version="0.4.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.app_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["health"], summary="Verificar saúde da API")
async def health() -> dict:
    return {
        "status": "ok",
        "service": "projeto-cidadao-api",
        "version": "0.4.0",
        "env": settings.app_env,
        "farejador_scheduler": FAREJADOR_DISPONIVEL,
    }


@app.get("/", tags=["health"], summary="Boas-vindas")
async def root() -> dict:
    return {
        "message": "🇧🇷 Projeto Cidadão — API de transparência pública",
        "docs": "/docs",
        "health": "/health",
    }


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(areas.router)
app.include_router(cursos.router)
app.include_router(denuncias.router)
app.include_router(comentarios.router)
app.include_router(faros.router)
app.include_router(votos.router)
app.include_router(anexos.router)
app.include_router(admin_farejador.router)


@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Recurso não encontrado", "path": str(request.url.path)},
    )
