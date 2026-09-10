# Processo de Post-Mortem

> **Princípio 6 — Transparência:** Aprender com os erros publicamente.
>
> Este documento define o processo formal de post-mortem para incidentes,
> bugs críticos e quedas de serviço no Projeto Cidadão.

---

## Quando realizar um post-mortem

Um post-mortem é **obrigatório** quando:

- Queda de serviço (downtime > 5 minutos)
- Erro 500 em endpoint de produção
- Perda ou corrupção de dados
- Vulnerabilidade de segurança explorada
- Rollback necessário após deploy
- Bug crítico que afetou usuários

Um post-mortem é **opcional mas recomendado** quando:

- Bug resolvido rapidamente sem impacto
- Melhoria arquitetural significativa
- Decisão técnica importante revertida

## Prazo e responsabilidade

- **Prazo:** até 48h após o incidente ser resolvido
- **Responsável:** quem resolveu o incidente
- **Revisor:** pelo menos 1 outro contribuidor

## Template

Cada post-mortem deve seguir este template:

```markdown
# Post-Mortem: [título do incidente]

**Data:** YYYY-MM-DD
**Duração:** Xh Ymin
**Impacto:** [descrição do impacto em usuários/sistema]
**Resolvido por:** [nome]

## Resumo

[1-2 parágrafos descrevendo o que aconteceu]

## Linha do tempo

- HH:MM — Detecção
- HH:MM — Diagnóstico
- HH:MM — Fix aplicado
- HH:MM — Confirmação de recuperação

## Causa raiz

[Descrição técnica detalhada da causa raiz]

## Ação corretiva

- [x] Fix imediato aplicado
- [ ] [ação preventiva 1]
- [ ] [ação preventiva 2]

## Lições aprendidas

- [lição 1]
- [lição 2]

## Links

- Commit: [hash]
- Issue: [#N]
- PR: [#N]
```

## Onde armazenar

Post-mortems devem ser commitados em:

```
docs/post-mortems/YYYY-MM-DD-titulo.md
```

## Exemplo: Post-Mortem #001

### Post-Mortem: Erro 502 Bad Gateway (10/09/2026)

**Data:** 2026-09-10
**Duração:** ~30min
**Impacto:** Site indisponível para todos os usuários
**Resolvido por:** Mira (assistente) + Jim

#### Resumo

O site do Projeto Cidadão retornou erro 502 Bad Gateway após o container
`pc_api` entrar em loop de reinicialização. A causa foi um arquivo
`redis_stats.py` que era um **instalador quebrado** sendo importado como
se fosse um endpoint pelo `main.py`.

#### Causa raiz

O arquivo `src/api/redis_stats.py` continha código de instalador (não de
endpoint) com 3 bugs:

1. `API_DIR / UND_INIT + ".py"` — `Path + str` não é válido em Python
2. Indentação quebrada no bloco `__init__.py` patch
3. `if _name_ == "_main_":` — underscores únicos (saga continua)

O instalador nunca rodou com sucesso. O endpoint real nunca foi escrito
no disco. Mas o `main.py` importava o arquivo quebrado → crash no boot
→ nginx sem backend → 502.

#### Ação corretiva

- [x] Substituir instalador pelo endpoint limpo direto no container
- [x] Commitar versão correta no GitHub (commit 41a9d4a)
- [x] Atualizar `main.py` com import + `include_router`
- [ ] Adicionar teste pytest para o endpoint `/api/redis-stats`
- [ ] Adicionar health check que valida import de todos os módulos

#### Lições aprendidas

- Instaladores devem ser scripts separados, não módulos importáveis
- Underscores únicos continuam sendo um problema recorrente no projeto
- Health check do Docker não detecta crash de import (só detecta após
  container reiniciar)
- Commits de documentação (.md) não quebram o site, mas mudanças
  injetadas direto no container sem commit podem

#### Links

- Commit: 41a9d4acedecd0f6d9877bd70a24dab970e507ea
- Issue: #13
```

---

## Compromisso

Ao seguir este processo, garantimos que:

1. **Erros não se repetem** — cada incidente gera aprendizado documentado
2. **Transparência** — qualquer pessoa pode ver o que aconteceu e por quê
3. **Melhoria contínua** — ações preventivas são rastreadas até conclusão
4. **Cultura sem culpa** — foco no sistema, não nas pessoas
