# Mapa de Princípios × Implementação

> Cruzamento dos 6 princípios do [PRINCIPIOS.md](./PRINCIPIOS.md) com o que já existe no código.
> Última revisão: 2026-09-10.

---

## Legenda

| Símbolo | Significado |
|---|---|
| ✅ | Implementado e maduro |
| ⚠️ | Parcialmente implementado (com gaps) |
| ❌ | Não implementado |

---

## 1. Humanidade (Ren 仁) — ✅ Maduro

> *Tratar o outro como gostaria de ser tratado.*

| Onde | O que |
|---|---|
| `backend/src/api/denuncias.py` | Endpoint de denúncias com flag `anonima` |
| `backend/src/services/anonimizacao.py` | Serviço dedicado de anonimização com nota de transparência |
| `backend/src/db/models/denuncia.py` | Modelo preserva auditoria (`removida_por`, `motivo_remocao`) mesmo após retirada |
| `backend/src/api/users.py` | Cadastro e perfil respeitando LGPD |

---

## 2. Retidão (Yi 义) — ✅ Implementado

> *Fazer o que é correto, não o que é conveniente.*

| Onde | O que |
|---|---|
| `LICENSE` | MIT — código aberto |
| `backend/src/api/faros.py` | Faros públicos, com heurística documentada em `src/services/farejador/heuristicas.py` |
| `backend/src/api/stats.py` | Estatísticas públicas, sem autenticação |

---

## 3. Honestidade (Xin 信) — ⚠️ Bom com gap

> *O que o sistema declara fazer, faz.*

| Onde | O que |
|---|---|
| `backend/src/services/anonimizacao.py` | Nota de transparência injetada na descrição quando denúncia é retirada |
| `backend/src/api/denuncias.py` | Operações registradas |
| ⚠️ **Gap** | Não há changelog público automático das mudanças relevantes |

---

## 4. Rito (Li 礼) — ✅ Implementado

> *A forma visível do respeito.*

| Onde | O que |
|---|---|
| `backend/main.py` | FastAPI gera Swagger em `/docs` automaticamente |
| `backend/SCHEMA.md` | Documentação do schema |
| `README.md` | Instruções claras de setup |
| `docs/` + `areas/` + `cursos/` | Conteúdo educacional organizado |

---

## 5. Sabedoria (Zhi 智) — ⚠️ Parcial

> *Cada cidadão tem direito a informação que permita discernir.*

| Onde | O que |
|---|---|
| `cursos/` (8 cursos em markdown) | Educação para cidadania: fiscalização, licitações, dados abertos, constitucional |
| `areas/` (10 áreas temáticas) | Mapeamento de conhecimento por área |
| ⚠️ **Gap** | Não há sistema de quiz/progresso exposto na API ainda (existem models em `progresso.py` mas sem endpoint ativo) |

---

## 6. Cultivo Contínuo — ⚠️ Prática forte, documentação fraca

> *Nada está pronto.*

| Onde | O que |
|---|---|
| Issues abertas no GitHub | Cultura de rastreamento público |
| `.github/workflows/ci.yml` | CI rodando |
| `backend/alembic/versions/` (7 migrations) | Evolução do schema versionada |
| ⚠️ **Gap** | Não há `CHANGELOG.md` humano, nem processo explícito de post-mortem de bugs |

---

## Resumo

| Princípio | Status |
|---|---|
| 1. Humanidade | ✅ Maduro |
| 2. Retidão | ✅ Bom |
| 3. Honestidade | ⚠️ Gap: changelog público |
| 4. Rito | ✅ Bom |
| 5. Sabedoria | ⚠️ Gap: endpoint de cursos com progresso |
| 6. Cultivo | ⚠️ Gap: changelog + post-mortem |

---

## Gaps prioritários

1. **Changelog público** (`CHANGELOG.md`) — atende Princípio 3 + 6
2. **Endpoint de cursos com progresso** — atende Princípio 5
3. **Processo de post-mortem** de bugs encerrados — atende Princípio 6

---

*Documento vivo. Atualizar a cada nova feature ou correção que afete o mapeamento.*
