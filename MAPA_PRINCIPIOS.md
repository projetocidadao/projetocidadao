# Mapa de Princípios × Implementação

> Acompanhamento vivo de como cada princípio do [`PRINCIPIOS.md`](./PRINCIPIOS.md) se manifesta no código do Projeto Cidadão.
>
> Última revisão: 2026-09-10.

---

## Legenda

| Símbolo | Significado |
|---|---|
| ✅ | Implementado e maduro |
| ⚠️ | Parcialmente implementado (com gaps) |
| ❌ | Não implementado |

---

## Princípio 1 — Humanidade (Ren 仁)

**Status: ✅ Implementado e maduro**

Tratar o outro como gostaria de ser tratado. O sistema é construído para servir pessoas, não o contrário.

| Onde | O que |
|---|---|
| `backend/src/api/denuncias.py` | Endpoint de denúncias com flag `anonima` |
| `backend/src/services/anonimizacao.py` | Serviço dedicado de anonimização com nota de transparência |
| `backend/src/db/models/denuncia.py` | Modelo preserva auditoria (`removida_por`, `motivo_remocao`) mesmo após retirada |
| `backend/src/api/users.py` | Cadastro e perfil respeitando LGPD |

---

## Princípio 2 — Retidão (Yi 义)

**Status: ✅ Implementado**

Fazer o que é correto, não o que é conveniente. Código aberto, dados auditáveis, decisões transparentes.

| Onde | O que |
|---|---|
| `LICENSE` | MIT — código aberto |
| `backend/src/api/faros.py` | Faros públicos, com heurística documentada em `src/services/farejador/heuristicas.py` |
| `backend/src/api/stats.py` | Estatísticas públicas, sem autenticação |

---

## Princípio 3 — Honestidade (Xin 信)

**Status: ✅ Implementado**

Palavra cumprida. O que o sistema declara fazer, faz. O que registra, é o que aconteceu.

| Onde | O que |
|---|---|
| `backend/src/services/anonimizacao.py` | Nota de transparência injetada na descrição quando denúncia é retirada |
| `backend/src/api/denuncias.py` | Operações registradas |
| `CHANGELOG.md` | Changelog público humano das mudanças relevantes |

---

## Princípio 4 — Rito (Li 礼)

**Status: ✅ Implementado**

A forma visível do respeito. Interface clara, linguagem acessível, processo documentado.

| Onde | O que |
|---|---|
| `backend/main.py` | FastAPI gera Swagger em `/docs` automaticamente |
| `backend/SCHEMA.md` | Documentação do schema |
| `README.md` | Instruções claras de setup |
| `docs/` + `areas/` + `cursos/` | Conteúdo educacional organizado |

---

## Princípio 5 — Sabedoria (Zhi 智)

**Status: ✅ Implementado**

Distinguir o certo do errado. Cada cidadão tem direito a informação que permita discernir.

| Onde | O que |
|---|---|
| `cursos/` (8 cursos em markdown) | Educação para cidadania: fiscalização, licitações, dados abertos, constitucional |
| `areas/` (10 áreas temáticas) | Mapeamento de conhecimento por área |
| `backend/src/api/progresso.py` | Endpoint de progresso de cursos (upsert, listagem, stats) |
| `backend/src/schemas/progresso.py` | Schemas Pydantic de progresso |

---

## Princípio 6 — Cultivo Contínuo

**Status: ✅ Implementado**

Nada está pronto. O sistema evolui com o uso, com o erro reconhecido, com a correção pública.

| Onde | O que |
|---|---|
| Issues abertas no GitHub | Cultura de rastreamento público |
| `.github/workflows/ci.yml` | CI rodando |
| `backend/alembic/versions/` (7 migrations) | Evolução do schema versionada |
| `CHANGELOG.md` | Changelog público humano |
| `docs/POST_MORTEM.md` | Processo explícito de post-mortem |
| `docs/post_mortem/` | Registros de incidentes reais |

---

## Resumo executivo

| Princípio | Status |
|---|---|
| 1. Humanidade | ✅ Maduro |
| 2. Retidão | ✅ Bom |
| 3. Honestidade | ✅ Sem gaps |
| 4. Rito | ✅ Bom |
| 5. Sabedoria | ✅ Implementado |
| 6. Cultivo | ✅ Implementado |

---

## Gaps prioritários

1. ~~**Changelog público** — Princípio 3 + 6~~ ✅ Fechado em 2026-09-10
2. ~~**Endpoint de cursos com progresso** — Princípio 5~~ ✅ Fechado em 2026-09-10
3. ~~**Processo de post-mortem** de bugs encerrados — Princípio 6~~ ✅ Fechado em 2026-09-10

---

## Histórico de evolução

### 2026-09-10

- **Gap #1 fechado**: `CHANGELOG.md` criado (Princípio 3 + 6)
- **Gap #2 fechado**: Endpoint `/api/progresso` criado e validado (Princípio 5)
- **Gap #3 fechado**: Processo de post-mortem documentado em `docs/POST_MORTEM.md` + primeiro registro real em `docs/post_mortem/2026-09-10-redis-stats-502.md` (Princípio 6)

---

## Como contribuir

Este mapa é vivo. Ao implementar uma feature nova, verifique:

- Qual princípio ela atende?
- Deve ser registrada neste mapa?
- Há gap que ela fecha?

Ao fechar um gap, marque o símbolo como ✅ e mova a entrada antiga para um histórico de evolução no final do documento.

---

*Mantido por colaboradores do Projeto Cidadão.*
