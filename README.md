# 🇧🇷 Projeto Cidadão

> Plataforma de transparência pública, fiscalização cidadã e educação para o controle social.

[![GitHub](https://img.shields.io/badge/repo-projetocidadao%2Fprojetocidadao-blue)](https://github.com/projetocidadao/projetocidadao)

## 🏗️ Estrutura

```
projetocidadao/
├── backend/             # API FastAPI + Postgres + Redis
├── mobile/              # (em breve) App React Native / Expo
├── docs/                # Documentação educacional
└── docker-compose.yml   # Ambiente completo de dev
```

## 🚀 Subir o ambiente (Docker)

Pré-requisitos: [Docker](https://docs.docker.com/get-docker/) e [Docker Compose](https://docs.docker.com/compose/install/).

```bash
# 1. Copie o .env (edite se quiser)
cp backend/.env.example backend/.env

# 2. Suba Postgres + Redis + API
docker compose up -d

# 3. Acompanhe os logs
docker compose logs -f api

# 4. Acesse:
#    - API:        http://localhost:8000
#    - Docs:       http://localhost:8000/docs
#    - Postgres:   localhost:5432
#    - Redis:      localhost:6379
```

Para subir também o **Adminer** (gerenciador web do banco):

```bash
docker compose --profile tools up -d
# Acesse: http://localhost:8080
```

## 🐳 Sem Docker (desenvolvimento local)

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env

# Suba apenas Postgres e Redis localmente
# (ou use Docker só pra eles: docker compose up postgres redis -d)

alembic upgrade head
python scripts/seed.py
uvicorn main:app --reload
```

## 📚 Documentação

- [Áreas Temáticas](docs/areas/README.md)
- [Cursos](docs/cursos/README.md)
- [Schema do Banco](backend/SCHEMA.md) *(em breve)*

## 🤝 Como contribuir

1. Fork o repositório
2. Crie uma branch (`git checkout -b feat/minha-feature`)
3. Commit suas mudanças (`git commit -m 'feat: minha feature'`)
4. Push (`git push origin feat/minha-feature`)
5. Abra um Pull Request

## 📜 Licença

MIT — veja [LICENSE](LICENSE).
