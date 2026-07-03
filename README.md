# 🌎 Projeto Cidadão

> Plataforma de transparência pública, fiscalização cidadã e educação para o controle social.

[![GitHub](https://img.shields.io/badge/repo-projetocidadao%2Fprojetocidadao-blue)](https://github.com/projetocidadao/projetocidadao)

## 📐 Estrutura

```
projetocidadao/
├── backend/                # API FastAPI + Postgres + Redis
├── mobile/                 # (em breve) App React Native / Expo
├── docs/                   # Documentação educacional
├── docker-compose.yml      # Ambiente completo de dev
```

## 🚀 Subir o ambiente (Docker)

Pré-requisitos: [Docker](https://docs.docker.com/get-docker/) e [Docker Compose](https://docs.docker.com/compose/install/).

```bash
# 1. Copie o .env (edite se quiser)
cp backend/.env.example backend/.env

# 2. Sobe Postgres + Redis + API
docker compose up -d

# 3. Acompanhe os logs
docker compose logs -f api

# 4. Acesse:
#    - API:       http://localhost:8000
#    - Docs:      http://localhost:8000/docs
#    - Postgres:  localhost:5432
#    - Redis:     localhost:6379
```

Para subir também o ambiente de admin (gera usuário admin):

```bash
docker compose exec api python -m src.scripts.create_admin
```

## 📚 Documentação adicional

- [Visão geral do projeto](docs/01-visao-geral.md)
- [Mapa dos poderes](docs/02-mapa-poderes.md)
- [Como contribuir](docs/03-como-contribuir.md)

## ✨ Status atual

- ✅ API FastAPI rodando na porta 8000
- ✅ 4 endpoints principais funcionando (`/api/areas`, `/api/cursos`, `/api/denuncias`, `/api/faros`)
- ✅ Login admin + JWT
- ✅ Schema Postgres sincronizado com models (0 drift no Alembic)
- ✅ Swagger em `/docs`
- ✅ Scheduler de faros rodando dentro do container
- ✅ Seed data: 5 áreas, 3 cursos, 10 denúncias, 2 faros

## 🛠️ Stack

- **API**: Python 3.11 + FastAPI + SQLAlchemy 2 + Alembic
- **Banco**: PostgreSQL 16 + PostGIS (geolocalização)
- **Cache/queue**: Redis
- **Auth**: JWT (python-jose) + bcrypt 3.2.2
- **Conteinerização**: Docker + Docker Compose
- **Mobile**: React Native + Expo (em breve)

## 📝 Licença

MIT © 2026 Projeto Cidadão
