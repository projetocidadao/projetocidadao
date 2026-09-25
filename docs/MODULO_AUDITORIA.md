# Módulo Auditoria — Projeto Cidadão

**Data:** 2026-09-25
**Autor:** Jim + Mira
**Status:** Proposta — aguardando validação

---

## Objetivo

Auditoria histórica dos **3 poderes** (Executivo, Legislativo, Judiciário) da República Federativa do Brasil desde a promulgação da Constituição de **5 de outubro de 1988**. Tirar a limpo: quem decidiu, quem executou, quem administrinou — com rastro temporal e cruzamento de sanções.

Diferente das denúncias (fatos atuais reportados por cidadãos), este módulo é um **arquivo de responsabilização histórica**: mapeia atores públicos, suas ações e consequências, permitindo ao cidadão traçar a linha do tempo de qualquer político, juiz ou servidor de alto escalão.

---

## Escopo (Fase 1)

- **Período:** 05/10/1988 → presente
- **Poderes cobertos:**
  - ✅ Legislativo (Câmara + Senado) — cobertura total desde 1988
  - ✅ Judiciário (CNJ DataJud, TRFs 1-6) — cobertura total
  - ⏸️ Executivo federal (DOU em XML só de 2020+) — **pulado na Fase 1**, OCR de PDFs pré-2020 fica pra Fase posterior
- **Granularidade:**
  - Deputados federais, senadores, presidentes da República, ministros de STF/STJ/Tribunais superiores
  - Fase 1 NÃO cobre: vereadores, prefeitos, deputados estaduais, servidores não-cargos-comissionados

---

## Fontes de dados (APIs públicas)

### Legislativo

| Fonte | URL | Cobertura | Auth |
|-------|-----|-----------|------|
| Câmara dos Deputados | `dadosabertos.camara.leg.br` | Votações nominais, proposições, tramitações, parlamentares, filiações partidárias — **desde 1988** | Nenhuma |
| Senado Federal | `legis.senado.leg.br/dadosabertos` | Parlamentares, mandatos, comissões | Nenhuma (limite 10 req/s) |

**Patterns Câmara:**
- `http://dadosabertos.camara.leg.br/arquivos/votacoes/{formato}/votacoes-{ano}.{formato}`
- `http://dadosabertos.camara.leg.br/arquivos/votacoesVotos/{formato}/votacoesVotos-{ano}.{formato}`
- `http://dadosabertos.camara.leg.br/arquivos/proposicoes/{formato}/proposicoes-{ano}.{formato}`

### Judiciário

| Fonte | URL | Cobertura | Auth |
|-------|-----|-----------|------|
| CNJ DataJud | `api-publica.datajud.cnj.jus.br` | Sentenças, acórdãos, movimentações processuais — 6 TRFs | Nenhuma (respeitar sigilos) |

**Endpoints por TRF:**
- TRF1: `https://api-publica.datajud.cnj.jus.br/api_publica_trf1/_search`
- TRF2: `https://api-publica.datajud.cnj.jus.br/api_publica_trf2/_search`
- TRF3: `https://api-publica.datajud.cnj.jus.br/api_publica_trf3/_search`
- TRF4: `https://api-publica.datajud.cnj.jus.br/api_publica_trf4/_search`
- TRF5: `https://api-publica.datajud.cnj.jus.br/api_publica_trf5/_search`
- TRF6: `https://api-publica.datajud.cnj.jus.br/api_publica_trf6/_search`

**Base legal:** Portaria CNJ nº 160/2020.

### Controle (TCU) — cruzamento de sanções

| Fonte | URL | Cobertura | Auth |
|-------|-----|-----------|------|
| TCU Dados Abertos | `dados-abertos.apps.tcu.gov.br` | Acórdãos, atos normativos, contas irregulares, inabilitados/inidôneos | Nenhuma |
| Portal da Transparência | `portaldatransparencia.gov.br/api-de-dados` | Despesas, contratos, convênios, sanções | Token (cadastro email) |

**Endpoints TCU principais:**
- `GET /api/acordao/recupera-acordaos?{inicio}&{quantidade}`
- `GET /api/atonormativo/recupera-atos-normativos`
- `POST /api/publico/responsaveis-inabilitados` (certidoes.apps.tcu.gov.br)
- `POST /api/publico/responsaveis-inidoneos`
- `POST /api/publico/responsaveis-contas-irregulares`
- `POST /api/publico/responsaveis-fins-eleitorais`

### Executivo (Fase posterior)

| Fonte | URL | Cobertura | Limitação |
|-------|-----|-----------|------------|
| DOU (Imprensa Nacional) | `in.gov.br/dados-abertos` | Decretos, portarias, nomeações, contratos (Seções 1, 2, 3) | XML estruturado só de 01/01/2020+. Pré-2020 exige OCR de PDFs escaneados. |

---

## Modelo de dados

### Tabelas

```sql
-- Pessoa física (parlamentar, juiz, ministro, presidente)
CREATE TABLE atores (
    id              SERIAL PRIMARY KEY,
    nome            VARCHAR(200) NOT NULL,
    nome_normalizado VARCHAR(200) NOT NULL,  -- lowercase, sem acento, para match
    cpf_publico     VARCHAR(14),              -- só se publicamente disponível
    data_nascimento DATE,
    biografia       TEXT,
    foto_url        VARCHAR(500),
    partido_atual   VARCHAR(20),
    cargo_atual     VARCHAR(100),
    poder_atual     VARCHAR(20),              -- executivo|legislativo|judiciario
    criado_em       TIMESTAMP DEFAULT NOW(),
    atualizado_em   TIMESTAMP DEFAULT NOW(),
    UNIQUE(nome_normalizado, data_nascimento)
);

-- Histórico de cargos/mandatos de um ator
CREATE TABLE cargos (
    id              SERIAL PRIMARY KEY,
    ator_id         INTEGER NOT NULL REFERENCES atores(id),
    cargo           VARCHAR(100) NOT NULL,    -- deputado_federal, senador, ministro_stf, presidente
    poder           VARCHAR(20) NOT NULL,
    orgao           VARCHAR(200),             -- Câmara dos Deputados, STF, TRF3
    uf              VARCHAR(2),               -- para cargos regionais
    partido         VARCHAR(20),              -- para mandatos legislativos
    periodo_inicio  DATE NOT NULL,
    periodo_fim     DATE,                     -- NULL = em exercício
    legislatura     INTEGER,                  -- para mandatos legislativos
    criado_em       TIMESTAMP DEFAULT NOW()
);

-- Ação pública: voto, proposição, sentença, decreto, contrato
CREATE TABLE acoes (
    id              SERIAL PRIMARY KEY,
    tipo             VARCHAR(50) NOT NULL,    -- voto|proposicao|sentenca|acordao|decreto|portaria|contrato
    data             DATE NOT NULL,
    poder            VARCHAR(20) NOT NULL,
    orgao            VARCHAR(200),
    descricao        TEXT,
    ementa           TEXT,
    valor_envolvido  DECIMAL(15,2),
    fonte_url        VARCHAR(500),
    dou_referencia   VARCHAR(200),            -- seção + página + data DOU
    codigo_externo   VARCHAR(100),            -- ID na fonte original (ex: codProposicao na Câmara)
    criado_em        TIMESTAMP DEFAULT NOW(),
    UNIQUE(tipo, data, codigo_externo)
);

-- Vínculo ator ↔ ação (qual papel ele teve naquela ação)
CREATE TABLE vinculos (
    id              SERIAL PRIMARY KEY,
    ator_id         INTEGER NOT NULL REFERENCES atores(id),
    acao_id         INTEGER NOT NULL REFERENCES acoes(id),
    papel           VARCHAR(30) NOT NULL,     -- autor|executor|administrador|relator|votante|signatario
    voto            VARCHAR(10),              -- sim|nao|abstencao|presidente (se aplicável)
    observacao      TEXT,
    criado_em       TIMESTAMP DEFAULT NOW(),
    UNIQUE(ator_id, acao_id, papel)
);

-- Consequência: sanção, irregularidade, cassação, anulação
CREATE TABLE consequencias (
    id              SERIAL PRIMARY KEY,
    ator_id         INTEGER NOT NULL REFERENCES atores(id),
    acao_id         INTEGER REFERENCES acoes(id),  -- ação que gerou a consequência (se houver)
    tipo            VARCHAR(50) NOT NULL,     -- irregularidade|inabilitacao|inidoneidade|cassacao|multa|eleitoral
    status          VARCHAR(30),              -- ativa|revogada|prescrita
    data            DATE NOT NULL,
    orgao_julgador  VARCHAR(200),             -- TCU, TSE, STF
    valor_multa     DECIMAL(15,2),
    tcu_acordao_id  VARCHAR(100),             -- ID do acórdão no TCU
    descricao       TEXT,
    criado_em       TIMESTAMP DEFAULT NOW()
);

-- Metadados de fonte (para auditoria e reprocessamento)
CREATE TABLE fontes (
    id              SERIAL PRIMARY KEY,
    nome            VARCHAR(100) NOT NULL,    -- camara|senado|cnj|tcu|dou
    tipo            VARCHAR(30),              -- api|csv|pdf|xml
    url             VARCHAR(500),
    data_coleta     TIMESTAMP DEFAULT NOW(),
    hash_conteudo   VARCHAR(64),              -- SHA256 do payload bruto
    raw_payload     TEXT,                     -- JSON/XML bruto (opcional, para debug)
    acao_id         INTEGER REFERENCES acoes(id)
);
```

### Índices recomendados

```sql
CREATE INDEX idx_atores_nome_normalizado ON atores(nome_normalizado);
CREATE INDEX idx_atores_poder_atual ON atores(poder_atual);
CREATE INDEX idx_cargos_ator_id ON cargos(ator_id);
CREATE INDEX idx_cargos_periodo ON cargos(periodo_inicio, periodo_fim);
CREATE INDEX idx_acoes_data_poder ON acoes(data, poder);
CREATE INDEX idx_acoes_tipo_data ON acoes(tipo, data);
CREATE INDEX idx_vinculos_ator_acao ON vinculos(ator_id, acao_id);
CREATE INDEX idx_vinculos_papel ON vinculos(papel);
CREATE INDEX idx_consequencias_ator ON consequencias(ator_id);
CREATE INDEX idx_consequencias_data ON consequencias(data);
```

---

## Endpoints REST (Fase 1 — esqueleto)

Todos sob `/api/audit/`, públicos (sem auth) salvo os marcados.

### Lista de atores
```
GET /api/audit/atores
  ?poder=legislativo
  &partido=PT
  &cargo=senador
  &uf=SP
  &periodo_de=1990-01-01
  &periodo_ate=2026-12-31
  &q=joao              # busca por nome
  &page=1&per_page=20
```

### Perfil completo de um ator
```
GET /api/audit/atores/{id}
```
Retorna: dados pessoais, histórico de cargos, ações recentes, sanções.

### Ações (com filtros)
```
GET /api/audit/acoes
  ?ator_id=42
  &poder=legislativo
  &tipo=voto
  &data_de=1988-10-05
  &data_ate=2026-12-31
  &orgao=Camara dos Deputados
  &page=1&per_page=20
```

### Linha do tempo de um ator
```
GET /api/audit/linha-do-tempo?ator_id=42
```
Retorna eventos cronológicos: cargos, ações, consequências — mesclados.

### Sanções de um ator
```
GET /api/audit/sancoes?ator_id=42
```
Retorna: consequencias + cruzamento TCU (inabilitado, inidôneo, contas irregulares).

### Busca full-text
```
GET /api/audit/busca?q=mensalao
```
Busca em acoes.descricao, acoes.ementa, atores.nome.

### Estatísticas (público)
```
GET /api/audit/stats
```
Retorna: total de atores por poder, ações por tipo, sanções ativas, etc.

---

## Plano de implementação por fases

### Fase 1 — Esqueleto (1-2 dias)
- [ ] Models SQLAlchemy: `AtorPublico`, `Cargo`, `AcaoPublica`, `Vinculo`, `Consequencia`, `Fonte`
- [ ] Migration Alembic
- [ ] Schemas Pydantic (Read + Create)
- [ ] Endpoints REST vazios retornando `[]` ou `404`
- [ ] Testes básicos de rota

### Fase 2 — Ingestão Câmara (2-3 dias)
- [ ] Worker `audit_camara.py` no `pc_farejador`
- [ ] Download anual de votações, votacoesVotos, proposições (1988→2026)
- [ ] Parser → upsert em `atores`, `acoes`, `vinculos`
- [ ] Cada voto nominal vira um `vinculo` (papel=votante, voto=sim/nao/abstencao)
- [ ] Cada proposição vira uma `acao` (tipo=proposicao); autor vira `vinculo` (papel=autor)
- [ ] Endpoint `/api/audit/atores?cargo=deputado_federal` populado

### Fase 3 — Ingestão Senado (1-2 dias)
- [ ] Worker `audit_senado.py`
- [ ] Mandatos + votações
- [ ] Respeitar limite 10 req/s (sleep 0.1s entre requests)

### Fase 4 — Ingestão Judiciário (2-3 dias)
- [ ] Worker `audit_cnj.py`
- [ ] Queries por TRF (1-6)
- [ ] Sentenças e acórdãos → `acoes` (tipo=sentenca|acordao)
- [ ] Magistrados → `atores` (poder=judiciario)
- [ ] Respeitar sigilos (LGPD): não expor dados de partes, só de magistrados

### Fase 5 — Cruzamento TCU (1-2 dias)
- [ ] Worker `audit_tcu.py`
- [ ] Baixar acórdãos + listas de inabilitados/inidôneos/contas irregulares
- [ ] Match por `nome_normalizado` + período
- [ ] Popular `consequencias`

### Fase 6 — Frontend PWA
- [ ] Linha do tempo visual (timeline.js ou similar)
- [ ] Busca com autocomplete
- [ ] Perfil de ator com abas (cargos, ações, sanções)
- [ ] Modo escuro

### Fase 7 — Executivo federal (posterior)
- [ ] OCR de PDFs do DOU pré-2020
- [ ] Worker `audit_dou.py` para XML pós-2020
- [ ] Decretos, portarias, nomeações

---

## Decisões pendentes

1. **Granularidade de vereadores/prefeitos:** Fase 1 NÃO cobre. Vale a pena abrir depois?
2. **Atualização dos dados:** contínua (crawler diário) ou batches mensais?
3. **LGPD para magistrados:** expor nome + sentença ou só nome?
4. **Cache de fontes:** salvar raw_payload em `fontes` ou só hash?
5. **Match de atores entre fontes:** nome_normalizado + data_nascimento basta, ou precisa CPF?

---

## Riscos e mitigações

| Risco | Mitigação |
|-------|----------|
| APIs fora do ar | Retry com backoff exponencial, cache local de raw_payload |
| Rate limit (Senado 10 req/s) | Sleep 0.1s entre requests, fila de processamento |
| Dados inconsistentes entre fontes | Match por nome_normalizado + validação manual amostral |
| Volume (38 anos de dados) | Ingestão incremental por ano, índices otimizados |
| LGPD | Expor só dados públicos de atores em cargo de confiança/comissionado |
| Duplicação de atores | Constraint UNIQUE(nome_normalizado, data_nascimento) + merge manual |

---

## Próximos passos imediatos

1. **Jim valida este documento** (24h de reflexão)
2. Ajustes de escopo/granularidade se necessário
3. Fase 1: gerar patch com models + migration + schemas + endpoints vazios
4. Subir no `pc_api`, testar rotas
5. Avançar para Fase 2 (ingestão Câmara)

---

*Documento vivo — atualizar conforme decisões forem tomadas.*
