# 🏗️ Backend — Projeto Cidadão

> API REST do Projeto Cidadão — alimenta a plataforma de transparência pública.

## 1. Visão Geral

Backend do Projeto Cidadão, responsável por:

- **Autenticação** — login, cadastro, OAuth
- **Áreas Temáticas** — CRUD de áreas
- **Cursos** — CRUD de cursos, progresso
- **Denúncias** — CRUD de denúncias, comentários, anexos
- **Farejador de Corrupção** — ETL, ML, score de risco
- **Mapa** — dados georreferenciados
- **Notificações** — push, email, Telegram

## 2. Stack Técnica

- **Linguagem:** Node.js (TypeScript)
- **Framework:** Express.js / Fastify
- **ORM:** Prisma
- **Banco de Dados:** PostgreSQL
- **Cache:** Redis
- **Storage:** S3 / Cloudflare R2
- **Filas:** Bull (Redis)
- **IA/ML:** Python (microsserviço)
- **Autenticação:** JWT + OAuth2
- **Documentação:** OpenAPI / Swagger
- **Testes:** Jest + Supertest
- **Containerização:** Docker + Docker Compose

## 3. Estrutura de Pastas

```
backend/
├── src/
│   ├── config/         # Configurações (env, db, etc)
│   ├── modules/        # Módulos de domínio
│   │   ├── auth/       # Autenticação
│   │   ├── users/      # Usuários
│   │   ├── areas/      # Áreas temáticas
│   │   ├── cursos/     # Cursos
│   │   ├── denuncias/  # Denúncias
│   │   ├── farejador/  # Farejador de corrupção
│   │   └── mapa/       # Mapa
│   ├── shared/         # Código compartilhado
│   │   ├── errors/     # Erros customizados
│   │   ├── middlewares/ # Middlewares (auth, rate limit, etc)
│   │   └── utils/      # Utilitários
│   ├── infra/          # Infraestrutura
│   │   ├── database/   # Prisma client
│   │   ├── cache/      # Redis client
│   │   ├── storage/    # S3 client
│   │   └── queue/      # Bull queue
│   └── server.ts       # Entry point
├── prisma/
│   └── schema.prisma   # Schema do banco
├── tests/              # Testes
├── docker-compose.yml  # Orquestração
├── Dockerfile          # Imagem Docker
├── package.json
├── tsconfig.json
└── .env.example        # Variáveis de ambiente (exemplo)
```

## 4. Modelo de Dados (Prisma)

```prisma
// schema.prisma — esqueleto

generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model Usuario {
  id        String   @id @default(cuid())
  email     String   @unique
  nome      String
  senha     String
  role      Role     @default(CIDADAO)
  pontos    Int      @default(0)
  criadoEm  DateTime @default(now())
  atualizadoEm DateTime @updatedAt
}

model Area {
  id        String   @id @default(cuid())
  slug      String   @unique
  nome      String
  descricao String
  icone     String
  cursos    Curso[]
  denuncias Denuncia[]
}

model Curso {
  id        String   @id @default(cuid())
  slug      String   @unique
  titulo    String
  descricao String
  conteudo  String   @db.Text
  areaId    String
  area      Area     @relation(fields: [areaId], references: [id])
  progresso Progresso[]
  criadoEm  DateTime @default(now())
  atualizadoEm DateTime @updatedAt
}

model Progresso {
  id        String   @id @default(cuid())
  usuarioId String
  cursoId   String
  percent   Int      @default(0)
  concluido Boolean  @default(false)
  usuario   Usuario  @relation(fields: [usuarioId], references: [id])
  curso     Curso    @relation(fields: [cursoId], references: [id])
}

model Denuncia {
  id          String   @id @default(cuid())
  titulo      String
  descricao   String   @db.Text
  categoria   String
  anonima     Boolean  @default(false)
  status      StatusDenuncia @default(AGUARDANDO)
  autorId     String?
  autor       Usuario? @relation(fields: [autorId], references: [id])
  areaId      String
  area        Area     @relation(fields: [areaId], references: [id])
  lat         Float?
  lng         Float?
  endereco    String?
  anexos      Anexo[]
  comentarios Comentario[]
  votos       Int      @default(0)
  criadoEm    DateTime @default(now())
  atualizadoEm DateTime @updatedAt
}

model Anexo {
  id         String   @id @default(cuid())
  url        String
  tipo       String
  denunciaId String
  denuncia   Denuncia @relation(fields: [denunciaId], references: [id])
}

model Comentario {
  id         String   @id @default(cuid())
  texto      String   @db.Text
  autorId    String
  autor      Usuario  @relation(fields: [autorId], references: [id])
  denunciaId String
  denuncia   Denuncia @relation(fields: [denunciaId], references: [id])
  criadoEm   DateTime @default(now())
}

enum Role {
  CIDADAO
  AVANCADO
  MODERADOR
  ADMIN
}

enum StatusDenuncia {
  AGUARDANDO
  EM_ANALISE
  EM_ANDAMENTO
  RESOLVIDA
  REJEITADA
}
```

## 5. Endpoints Principais

### Auth
- `POST /auth/register` — cadastro
- `POST /auth/login` — login
- `POST /auth/refresh` — refresh token
- `POST /auth/forgot` — esqueci a senha

### Usuários
- `GET /users/me` — perfil
- `PATCH /users/me` — atualizar perfil
- `GET /users/:id/pontos` — pontos

### Áreas
- `GET /areas` — listar áreas
- `GET /areas/:slug` — detalhes da área

### Cursos
- `GET /cursos` — listar cursos
- `GET /cursos/:slug` — detalhes do curso
- `POST /cursos/:id/progresso` — atualizar progresso
- `POST /cursos` — criar curso (admin)

### Denúncias
- `GET /denuncias` — listar (com filtros)
- `GET /denuncias/:id` — detalhes
- `POST /denuncias` — criar denúncia
- `PATCH /denuncias/:id` — atualizar status
- `POST /denuncias/:id/comentarios` — comentar
- `POST /denuncias/:id/voto` — votar

### Farejador
- `GET /farejador/score/:cnpj` — score de risco de empresa
- `GET /farejador/alertas` — alertas recentes
- `GET /farejador/padroes` — padrões detectados

### Mapa
- `GET /mapa/denuncias` — denúncias georreferenciadas
- `GET /mapa/areas` — áreas georreferenciadas

## 6. Variáveis de Ambiente

```env
# .env.example
DATABASE_URL=postgresql://user:pass@localhost:5432/projetocidadao
REDIS_URL=redis://localhost:6379
JWT_SECRET=changeme
JWT_EXPIRES_IN=7d
AWS_ACCESS_KEY_ID=changeme
AWS_SECRET_ACCESS_KEY=changeme
AWS_BUCKET=projetocidadao
TELEGRAM_BOT_TOKEN=changeme
ML_SERVICE_URL=http://localhost:8000
PORT=3333
NODE_ENV=development
```

## 7. Como Rodar Localmente

```bash
# 1. Clone o repositório
git clone https://github.com/projetocidadao/projetocidadao.git
cd projetocidadao/backend

# 2. Instale as dependências
npm install

# 3. Configure as variáveis de ambiente
cp .env.example .env
# edite o .env com suas credenciais

# 4. Suba o banco de dados
docker-compose up -d postgres redis

# 5. Rode as migrations
npx prisma migrate dev

# 6. Inicie o servidor
npm run dev
```

## 8. Docker Compose (Dev)

```yaml
# docker-compose.yml
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: projetocidadao
      POSTGRES_PASSWORD: changeme
      POSTGRES_DB: projetocidadao
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7
    ports:
      - "6379:6379"

  backend:
    build: .
    ports:
      - "3333:3333"
    depends_on:
      - postgres
      - redis
    environment:
      DATABASE_URL: postgresql://projetocidadao:changeme@postgres:5432/projetocidadao
      REDIS_URL: redis://redis:6379

volumes:
  pgdata:
```

## 9. Roadmap

- [x] Especificação da stack e estrutura
- [ ] Configurar Prisma + migrations iniciais
- [ ] CRUD de usuários + auth (JWT)
- [ ] CRUD de áreas e cursos
- [ ] CRUD de denúncias + upload de anexos
- [ ] Microsserviço de ML (Farejador)
- [ ] API de mapa (georreferenciamento)
- [ ] Notificações push (Telegram Bot)
- [ ] Testes E2E
- [ ] CI/CD (GitHub Actions)
- [ ] Deploy (Railway / Render / Fly.io)

---

📌 *Backend é a espinha dorsal — mas o frontend (mobile) é a cara do projeto. Ambos precisam ser pensados juntos.*
