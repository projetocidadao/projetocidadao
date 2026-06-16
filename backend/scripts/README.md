# 🛠️ Scripts Utilitários

## `seed.py`
Popula o banco com dados iniciais (áreas temáticas e usuário admin).

```bash
python scripts/seed.py
```

## `wait_for_db.py`
Aguarda o banco de dados estar pronto (usado pelo Docker Compose no entrypoint).

## `init-postgis.sql`
Extensões do PostgreSQL instaladas automaticamente quando o container é criado pela primeira vez:
- `postgis` — geolocalização
- `pg_trgm` — busca textual
- `uuid-ossp` — geração de UUIDs

## Migrations (Alembic)
```bash
# Aplicar migrations
alembic upgrade head

# Reverter última migration
alembic downgrade -1

# Criar nova migration após mudar os models
alembic revision --autogenerate -m "descrição da mudança"

# Ver status
alembic current
alembic history
```

## Docker
```bash
# Subir ambiente completo (Postgres + Redis + API)
docker compose up -d

# Subir também o Adminer (gerenciador web do banco)
docker compose --profile tools up -d

# Ver logs da API
docker compose logs -f api

# Rodar migrations manualmente
docker compose exec api alembic upgrade head

# Rodar seed manualmente
docker compose exec api python scripts/seed.py

# Acessar o bash do container
docker compose exec api sh

# Parar tudo (preserva os volumes)
docker compose down

# Parar e APAGAR os volumes
docker compose down -v
```
