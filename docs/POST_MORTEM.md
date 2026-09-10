# Processo de Post-Mortem

> Toda correção de bug relevante gera um registro público de aprendizado.
> Princípio 6 (Cultivo Contínuo) do [`PRINCIPIOS.md`](../PRINCIPIOS.md).

---

## Por que

Bugs acontecem. O que diferencia um projeto maduro de um projeto qualquer
é a capacidade de **reconhecer publicamente** o que aconteceu, **entender a
causa raiz**, e **transformar o incidente em aprendizado institucional**.

Post-mortems não são para culpar ninguém. São para garantir que o mesmo
problema não se repita.

---

## Quando fazer

Um post-mortem é obrigatório quando:

- 🔴 Incidente de produção (site fora do ar, dados perdidos, etc.)
- 🟠 Bug crítico corrigido em pânico (correção emergencial)
- 🟡 Saga de debugging longa (>1 dia de investigação)
- 🟢 Descoberta de bug antigo latente que exigiu refatoração

Não precisa de post-mortem:
- Correção typos em docs
- Ajustes de configuração triviais
- Features novas (essas vão no CHANGELOG)

---

## Como fazer

### 1. Criar o arquivo

Arquivos vivem em `docs/post_mortem/` com o padrão:

```
YYYY-MM-DD-slug-do-incidente.md
```

Exemplo: `2026-09-10-redis-stats-502.md`

### 2. Preencher o template

Usar o template abaixo (ver `Template` no final deste arquivo).

### 3. Linkar

- Referenciar a issue do GitHub relacionada
- Referenciar o commit do fix
- Adicionar entrada no `CHANGELOG.md` se for incidente de produção

### 4. Atualizar MAPA_PRINCIPIOS

Se o post-mortem fechar um gap, marcar como ✅ no `MAPA_PRINCIPIOS.md`.

---

## Template

```markdown
# [Título do incidente]

**Data:** YYYY-MM-DD
**Severidade:** 🔴/🟠/🟡/🟢
**Duração do impacto:** Xh Ymin
**Issue:** #NNN
**Commit do fix:** ABC1234

## Resumo

[1-2 parágrafos descrevendo o que aconteceu, em linguagem humana]

## Linha do tempo

| Hora | Evento |
|---|---|
| HH:MM | Sintoma observado |
| HH:MM | Diagnóstico confirmado |
| HH:MM | Fix aplicado |
| HH:MM | Validação |

## Causa raiz

[O que realmente causou o problema — não o sintoma]

## Fatores contribuintes

- [Fator 1]
- [Fator 2]

## O que deu certo

- [Coisa que funcionou bem na resposta]

## O que deu errado

- [Coisa que atrapalhou ou atrasou]

## Ações preventivas

- [ ] [Ação 1] — responsável: ???
- [ ] [Ação 2] — responsável: ???

## Lições

- [Lição 1]
- [Lição 2]

## Referências

- Issue #NNN
- Commit ABC1234
- PR #NNN
```

---

## Índice de post-mortems

| Data | Incidente | Severidade |
|---|---|---|
| 2026-09-10 | [redis-stats-502](./post_mortem/2026-09-10-redis-stats-502.md) | 🔴 |

---

*Mantido pelo processo de Cultivo Contínuo do Projeto Cidadão.*
