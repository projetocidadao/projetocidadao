# =============================================================================
# Projeto Cidadão — Dockerfile
# Imagem da API FastAPI (multi-stage)
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Builder — instala dependências
# -----------------------------------------------------------------------------
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Dependências do sistema para compilar pacotes Python (psycopg2, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia apenas o requirements primeiro (cache de layers do Docker)
COPY requirements.txt .

# Instala as dependências em um prefixo separado
RUN pip install --user --no-cache-dir -r requirements.txt


# -----------------------------------------------------------------------------
# Stage 2: Runtime — imagem final leve
# -----------------------------------------------------------------------------
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/home/appuser/.local/bin:${PATH}"

# Dependências runtime (libpq para psycopg2, curl para healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Cria usuário não-root (segurança)
RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app

# Copia as dependências instaladas do builder
COPY --from=builder /home/appuser/.local /home/appuser/.local

# Copia o código
COPY --chown=appuser:appuser . /app

USER appuser

# Exposição da porta da API
EXPOSE 8000

# Healthcheck nativo do container
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando padrão (sobrescrito pelo docker-compose em dev)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
