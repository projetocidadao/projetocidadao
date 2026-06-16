# 🗄️ Schema do Banco de Dados

> Estrutura relacional do Projeto Cidadão — FastAPI + SQLAlchemy 2.0 (async) + PostgreSQL

## Visão Geral

O schema é organizado em **10 tabelas principais**, agrupadas em 4 domínios:

```
┌─────────────┐
│  USUÁRIOS   │ ← sistema de pontos pioneiros + LGPD
└──────┬──────┘
       │
       ├─────────────┐
       ↓             ↓
┌─────────────┐  ┌────────────┐
│   ÁREAS     │  │  DENÚNCIAS │ ← georreferenciadas, anônimas, com anexos
└──────┬──────┘  └──────┬─────┘
       │                │
       ↓                ├──→ ┌────────┐
┌─────────────┐         │     │ ANEXOS │
│   CURSOS    │         │     └────────┘
└──────┬──────┘         │
       │                └──→ ┌────────────┐
       ↓                      │COMENTÁRIOS │ ← polimórfico
┌─────────────┐               └────────────┘
│  MÓDULOS    │
└─────────────┘
       ↓
┌─────────────┐
│ PROGRESSOS  │ ← usuário x curso
└─────────────┘

┌────────────────┐
│CASOS SUSPEITOS │ ← Farejador de Corrupção
└───────┬────────┘
        ↓
┌──────────────┐
│ HEURÍSTICAS  │ ← H1, H2, H3, ... acionadas
└──────────────┘
```

## Tabelas

### `usuarios`
- Sistema de **5 níveis de papel** (cidadao → admin)
- **Pontos pioneiros** (3-2-1) com gamificação
- **Período de incubação** — só pode criar conteúdo após X dias
- **LGPD** — consentimento explícito + data

### `areas` (temáticas)
- 9 áreas pré-cadastradas (saúde, educação, etc.)
- Slug, ícone, cor, ordem de exibição

### `cursos`
- Status de governança: `incubacao` → `em_aprovacao` → `publicado`
- Vinculado a uma `area` e um `autor` (usuario)
- Markdown como conteúdo principal

### `modulos`
- Subdivisão dos cursos (1:N)
- Ordenados, com `duracao_minutos`

### `progressos`
- Tabela de junção `usuario` x `curso` com `percent` e `concluido`
- Constraint única para evitar duplicatas

### `denuncias`
- Georreferenciadas (`lat`/`lng`/`municipio`/`estado`)
- **Anônimas** ou identificadas
- **Código de rastreio** único (20 chars)
- **Status** e **canal de destino** (CGU, MP, TCU...)
- Vinculada a uma `area` e opcionalmente a um `autor`
- `resposta_oficial` do poder público

### `anexos`
- Evidências (fotos, vídeos, PDFs)
- URL + tipo + tamanho + **hash SHA256** (integridade)

### `comentarios`
- **Polimórficos** — funcionam para denúncias, cursos, áreas e casos
- Suporte a **threading** (`parent_id`)
- Auto-relacionamento

### `casos_suspeitos` (Farejador)
- 7 tipos: licitacao, contrato, folha, transferencia, cruzamento, empresa, pessoa
- **Score de risco** (0-100) + severidade (BAIXA/MEDIA/ALTA/CRITICA)
- **JSONB** para dados flexíveis
- Vinculação opcional a uma denúncia

### `heuristicas`
- Quais heurísticas (H1, H2, ...) foram acionadas em cada caso
- Peso + evidência em JSONB

## Enums

| Enum | Valores |
|---|---|
| `role_enum` | cidadao, avancado, pioneiro, moderador, admin |
| `status_curso_enum` | incubacao, em_aprovacao, publicado, rejeitado, arquivado |
| `status_denuncia_enum` | aguardando, em_analise, em_andamento, resolvida, rejeitada, arquivada |
| `canal_denuncia_enum` | cgu, ministerio_publico, tcu, tce, ouvidoria_*, defensoria, ibama, policia_federal, outro |
| `tipo_alvo_enum` | denuncia, curso, area, caso_suspeito |
| `status_caso_enum` | novo, em_analise, investigado, confirmado, falso_positivo, arquivado |
| `tipo_caso_enum` | licitacao, contrato, folha, transferencia, cruzamento, empresa, pessoa |

## Como aplicar

```bash
# 1. Subir o Postgres
docker-compose up -d postgres

# 2. Aplicar a migration
alembic upgrade head

# 3. Rodar o seed (áreas + admin)
python -m src.db.seed
```

## Próximos passos

- [ ] Criar rotas de auth (`/auth/register`, `/auth/login`)
- [ ] Criar CRUD de denúncias (`/denuncias`)
- [ ] Criar CRUD de cursos (`/cursos`)
- [ ] Integrar com o Farejador (jobs assíncronos)
- [ ] Criar índices adicionais baseados em queries reais
- [ ] Adicionar soft delete (`deleted_at`) para LGPD
