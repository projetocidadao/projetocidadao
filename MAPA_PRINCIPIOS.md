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

**Status: ⚠️ Implementado com gaps**

Palavra cumprida. O que o sistema declara fazer, faz. O que registra, é o que aconteceu.

| Onde | O que |
|---|---|
| `backend/src/services/anonimizacao.py` | Nota de transparência injetada na descrição quando denúncia é retirada |
| `backend/src/api/denuncias.py` | Operações registradas |
| ⚠️ **Gap** | Não há changelog público automático das mudanças relevantes |

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

**Status: ⚠️ Parcialmente implementado**

Distinguir o certo do errado. Cada cidadão tem direito a informação que permita discernir.

| Onde | O que |
|---|---|
| `cursos/` (8 cursos em markdown) | Educação para cidadania: fiscalização, licitações, dados abertos, constitucional |
| `areas/` (10 áreas temáticas) | Mapeamento de conhecimento por área |
| ⚠️ **Gap** | Não há sistema de quiz/progresso exposto na API ainda (existem models em `progresso.py` mas sem endpoint ativo) |

---

## Princípio 6 — Cultivo Contínuo

**Status: ⚠️ Forte na prática, fraco na documentação**

Nada está pronto. O sistema evolui com o uso, com o erro reconhecido, com a correção pública.

| Onde | O que |
|---|---|
| Issues abertas no GitHub | Cultura de rastreamento público |
| `.github/workflows/ci.yml` | CI rodando |
| `backend/alembic/versions/` (7 migrations) | Evolução do schema versionada |
| ⚠️ **Gap** | Não há `CHANGELOG.md` humano, nem processo explícito de post-mortem de bugs |

---

## Resumo executivo

| Princípio | Status |
|---|---|
| 1. Humanidade | ✅ Maduro |
| 2. Retidão | ✅ Bom |
| 3. Honestidade | ⚠️ Bom com gap (changelog) |
| 4. Rito | ✅ Bom |
| 5. Sabedoria | ⚠️ Conteúdo pronto, API de cursos não exposta |
| 6. Cultivo | ⚠️ Prática forte, documentação fraca |

---

## Gaps prioritários

1. **Changelog público** — Princípio 3 + 6
2. **Endpoint de cursos com progresso** — Princípio 5
3. **Processo de post-mortem** de bugs encerrados — Princípio 6

---

## Como contribuir

Este mapa é vivo. Ao implementar uma feature nova, verifique:

- Qual princípio ela atende?
- Deve ser registrada neste mapa?
- Há gap que ela fecha?

Ao fechar um gap, marque o símbolo como ✅ e mova a entrada antiga para um histórico de evolução no final do documento.

---

*Mantido por colaboradores do Projeto Cidadão.*
