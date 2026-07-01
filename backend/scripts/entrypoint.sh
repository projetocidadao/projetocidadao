#!/bin/sh
set -e

echo "==> Aguardando DNS do banco (db)..."
i=0
until getent hosts db >/dev/null 2>&1; do
  i=$((i+1))
  [ "$i" -ge 30 ] && { echo "❌ DNS não resolveu"; cat /etc/resolv.conf; exit 1; }
  echo "Tentativa $i/30: DNS ainda não resolveu..."
  sleep 2
done

echo "==> Aguardando Postgres..."
i=0
until python -c "
import os, asyncio, asyncpg
url = os.environ['DATABASE_URL'].replace('postgresql+asyncpg', 'postgresql')
asyncio.run(asyncpg.connect(url))
" >/dev/null 2>&1
do
  i=$((i+1))
  [ "$i" -ge 30 ] && { echo "❌ Banco não respondeu"; exit 1; }
  echo "Tentativa $i/30: banco ainda não aceitando conexões..."
  sleep 2
done

echo "==> Banco OK. Rodando migrations..."
alembic upgrade head 2>/dev/null || echo "⚠️  sem migrations, seguindo..."

echo "==> Iniciando API..."
exec uvicorn main:app --host 0.0.0.0 --port 8000
