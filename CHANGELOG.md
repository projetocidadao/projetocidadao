# Changelog

> Histórico de mudanças do Projeto Cidadão.
> Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/), versionamento [SemVer](https://semver.org/lang/pt-BR/).

---

## [Não publicado]

### Adicionado
- `MAPA_PRINCIPIOS.md` — cruzamento dos 6 princípios com a implementação atual
- `PRINCIPIOS.md` — manifesto fundador do projeto (6 princípios + citações de Confúcio)
- Issue #13 aberta para rastrear evolução do manifesto

### Alterado
- Issue #13 atualizada com checklist de gaps prioritários

---

## [0.4.0] — 2026-09-10

### Adicionado
- `MAPA_PRINCIPIOS.md` mapeando princípios × implementação
- 3 gaps prioritários identificados: changelog público, endpoint de cursos com progresso, post-mortem de bugs

### Documentação
- Issue #13 atualizada com checklist de gaps e link para o mapa

---

## [0.3.0] — 2026-09-07

### Adicionado
- `PRINCIPIOS.md` — documento de princípios do projeto
- 6 princípios fundamentais: Ren (Humanidade), Yi (Retidão), Xin (Honestidade), Li (Rito), Zhi (Sabedoria), Cultivo Contínuo
- Tabela de aplicação concreta no sistema
- Citações de Confúcio (551–479 a.C.) como fonte de inspiração declarada
- Issue #13 aberta para rastrear revisão, tradução e mapeamento

---

## [0.2.3] — 2026-08-03

### Corrigido
- **Saga `stats.py` encerrada** — 6 bugs encadeados resolvidos:
  - Linha órfã em `src/services/stats.py`
  - `]]` duplo (colchete extra)
  - `try` sem `except`
  - `return` fora do `try`
  - `except` faltando cláusula
  - `return StatsX` (classe) em vez de `return StatsX(...)` (instância) — causava `ModelMetaclass` error no Pydantic
- Endpoint `/api/stats` retornando dados corretos: 12 denúncias, 5 áreas, 6 categorias, 3 faros, 3 heurísticas
- Todos os endpoints retornando HTTP 200 (Faros 401 protegido por auth)

### Padrão de debug documentado
- Quando Pydantic reclamar `ModelMetaclass` no `/api/stats`, verificar `return SchemaClasse` sem parênteses — script diagnóstico: `grep -n 'return Stats' src/services/stats.py`

---

## [0.2.2] — 2026-07-07

### Adicionado
- **Endpoint `/api/stats`** — estatísticas públicas sem autenticação
  - Contadores gerais: total, públicas, anônimas, por status, retiradas, coação, pedidos pendentes
  - Distribuição por mês, por área temática (com percentual), por categoria
  - 3 arquivos: `src/schemas/stats.py`, `src/services/stats.py`, `src/api/stats.py`

### Corrigido
- **Modelo de retirada de denúncias** (Issue #9) — 9/9 testes pytest passando
  - Fluxo E2E validado: denúncia criada → pedido_retirada registrado → moderador confirma → autor anonimizado para `null`, `status_remocao=retirada_pelo_autor`, nota de transparência adicionada na descrição, auditoria preservada (`removida_por`, `motivo_remocao`)
- **Bug do farejador** (Issue #10) — `scheduler.py` sem `if __name__ == "__main__"` causava loop de reinício
  - Adicionado bloco main que chama `iniciar_scheduler()` + `while True: time.sleep(60)` + handlers SIGTERM/SIGINT
- **FK ambígua** (Issue #11) — instalador v3 corrigiu múltiplos caminhos de foreign key para `usuarios.id`

### Removido
- Issues #7, #9, #10, #11 fechadas no GitHub

### Documentação
- Saga completa de correções (02–07/07/2026) documentada no comentário 4899368993 da issue #7
- Instalador final v3 publicado em S3

---

## [0.2.1] — 2026-07-06

### Adicionado
- **Modelo de retirada de denúncias** (Issue #9) — código pronto
  - 6 colunas novas: `status_remocao`, `motivo_remocao`, `pedido_retirada_em`, `pedido_retirada_justificativa`, `removida_em`, `removida_por`
  - 3 endpoints novos: `pedido-retirada`, `decisao-retirada`, `admin/pedidos-retirada-pendentes`
  - Migration `20260706_2200_add_denuncia_retirada`

### Corrigido
- `AttributeError: Denuncia.criado_em` no farejador — model usa `created_at`, não `criado_em`
- Patch `criado_em → created_at` aplicado em `src/farejador/worker.py`

---

## [0.2.0] — 2026-07-03

### Adicionado
- **API 100% funcional COM DADOS**
  - `/api/areas` — 5 registros
  - `/api/cursos` — 3 registros
  - `/api/denuncias` — 10 registros
  - `/api/faros` — 2 registros
- Seed data completo no banco

### Corrigido
- **3 rounds de fix em models SQLAlchemy:**
  1. `__tablename__` corrigido em 9 models (usando `chr(95)*2` para escapar markdown que consome underscores duplos)
  2. `faro.py` + `denuncia.py` — dunders + `values_callable` no Enum
  3. `area.py` e `curso.py` — schema completo (ativo, ordem, artigo_cf, nivel, total_modulos, etc)
- `enums.py` alinhado ao banco: `StatusFaro.EM_REVISao → EM_ANALISE` + `INVESTIGADO`, removido `FALSO_POSITIVO/ENCAMINHADO/ARQUIVADA_DENUNCIA`
- `denuncia.py` — `canal_destino: String(100)` em vez de `Enum(CanalDenuncia)`
- `schemas/faro.py` — `heuristicas: List[Dict[str, Any]]`
- Auth funcionando com campos `nome` e `biografia` (não `nome_completo` nem `bio`)

### Documentação
- Skill `/dunder_fix` publicada no catálogo Mira — automatiza correção de `__tablename__` quebrado

---

## [0.1.2] — 2026-07-02

### Corrigido
- **Bug do farejador** — `scheduler.py` só definia funções, sem `if __name__ == "__main__"`
  - Container reiniciava em loop
  - Fix: bloco main chamando `iniciar_scheduler()` + `while True: time.sleep(60)` + handlers SIGTERM/SIGINT
- **2 jobs registrados no scheduler:**
  - Cron `0 */6 * * *` (a cada 6h)
  - Healthcheck a cada 30min
- Scheduler rodando em PID 1 dentro do container, sem `RuntimeWarning`

### Corrigido (infra)
- **Wget do BusyBox no nginx:1.25-alpine** não aceita `-qO-` — usar `-q -O /tmp/h` (args separados)
- **Healthcheck Docker** — sempre usar `127.0.0.1` em vez de `localhost` (Alpine resolve `localhost` para `::1` IPv6 quando nginx só escuta IPv4)

---

## [0.1.1] — 2026-07-01

### Adicionado
- **API subiu oficialmente**
  - Login admin OK (HTTP 200 + JWT válido)
  - Swagger `/docs` disponível em `http://localhost:8000/docs`
  - `GET /api/users/me` retorna 200

### Corrigido
- **Import errors** em múltiplos arquivos
- **URL-encode na senha do Postgres** — caractere especial `@` exige `%40` na `DATABASE_URL`
- **`entrypoint.sh`** com `wait-for-DNS` para inicialização limpa
- **`bcrypt` downgradeado para 3.2.2** — `passlib` incompatível com bcrypt 4.x (não tem `_about_`)
- **Schema Pydantic `UsuarioRead`** alinhado ao model e banco: usa `biografia/criado_em/atualizado_em` (não `bio/created_at/updated_at`), não exige `nivel/verificado`
- **Função de hash** em `src/core/security.py` é `hash_senha()` (não `gerar_hash`)
- **Variável de sessão async** renomeada para `AsyncSessionLocal` (não `async_session`) — imports atualizados em `worker.py`, `admin_farejador.py`, `notificacoes/worker.py`

---

## [0.1.0] — 2026-06-16

### Adicionado
- Schema inicial do banco via Alembic (`2026_06_16_0000-001_initial_schema.py`)
- Models SQLAlchemy para 9 entidades: Usuario, Area, Curso, Denuncia, Comentario, Faro, Notificacao, Progresso, Voto
- Estrutura básica do backend FastAPI
- Docker Compose com containers: `pc_api`, `pc_db`, `pc_redis`, `pc_nginx`, `pc_farejador`
- API rodando na porta 8000

---

## Tipos de mudança

- **Adicionado** — novas features
- **Alterado** — mudanças em features existentes
- **Depreciado** — features que serão removidas
- **Removido** — features removidas
- **Corrigido** — bug fixes
- **Segurança** — vulnerabilidades corrigidas
- **Documentação** — mudanças apenas em docs

---

*Para ver o diff completo de cada versão, consulte os commits no GitHub.*
