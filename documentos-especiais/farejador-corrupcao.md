# 🕵️ Farejador de Corrupção — Especificação Técnica

> *"A função de um sistema de detecção é transformar a improbidade em risco, não em certeza."* — Projeto Cidadão

## 1. Visão Geral

O **Farejador de Corrupção** é uma ferramenta de **análise automatizada de dados públicos** que usa técnicas de ciência de dados e IA para identificar **padrões suspeitos** em gastos públicos, licitações, contratos e folha de pagamento.

A ferramenta **não julga** — ela **sinaliza** casos que merecem investigação humana, cruzando dados de múltiplas fontes e aplicando heurísticas baseadas em casos reais de corrupção.

## 2. Objetivos

- **Detectar** padrões suspeitos automaticamente
- **Acelerar** o trabalho de controle social e fiscalização
- **Educar** cidadãos sobre como identificar sinais de corrupção
- **Priorizar** investigações de acordo com o risco
- **Transparência** — tornar os dados acessíveis e compreensíveis

## 3. Fontes de Dados

### Compras Governamentais
- **ComprasNet / Compras.gov.br** — licitações federais
- **Portal da Transparência** — contratos, atas, atas de registro de preço
- **TCEs (Tribunais de Contas Estaduais)** — licitações estaduais e municipais
- **TCU** — licitações federais

### Folha de Pagamento
- **Portal da Transparência** — servidores federais
- **Portais estaduais e municipais** — servidores
- **CNJ** — salários do judiciário
- **CNMP** — salários do MP

### Transferências e Convênios
- **Portal da Transparência** — transferências, convênios
- **SICONV** — Sistema de Convênios
- **Transferênciasgov.br** — novo sistema

### Outros
- **RFB (Receita Federal)** — CNPJ, QSA, sanções
- **CEIS / CNEP / CEPIM** — cadastros de empresas inidôneas
- **TCU — Acórdãos** — decisões sobre improbidade

## 4. Heurísticas de Detecção

### 4.1. Licitações
- **H1 — Fracionamento de despesa** — várias compras pequenas para burlar limite de modalidade
- **H2 — Concentração de fornecedores** — poucos fornecedores vencem muitas licitações
- **H3 — Vencedor reincidente** — mesmo fornecedor ganha em órgão e período suspeito
- **H4 — Objeto genérico** — descrição do objeto muito vaga
- **H5 — Prazo exíguo** — prazo entre publicação e abertura muito curto
- **H6 — Dispensa de licitação** — volume alto de dispensas em um órgão
- **H7 — Sobrepreço** — preço superior a 25% da média de mercado
- **H8 — Aditivos excessivos** — aditivos que somam mais de 25% do valor original

### 4.2. Contratos
- **H9 — Pagamentos antecipados** — grande volume de pagamentos antes da entrega
- **H10 — Contratos emergenciais repetidos** — mesmo objeto, várias vezes
- **H11 — Sem fiscalização** — contrato sem fiscal designado
- **H12 — Vínculo suspeito** — sócios com parentesco com agentes públicos

### 4.3. Folha de Pagamento
- **H13 — Acumulação indevida** — cargo público em mais de um órgão
- **H14 — Cargo comissionado em excesso** — proporção de comissionados acima de 50%
- **H15 — Salário acima do teto** — remuneração acima do teto constitucional
- **H16 — Servidor fantasma** — movimentações financeiras sem folha

### 4.4. Transferências
- **H17 — Convênio sem prestação de contas** — valores transferidos sem devida comprovação
- **H18 — Convênio com mesmo objeto** — múltiplos convênios para o mesmo fim
- **H19 — Beneficiário inadimplente** — entidade com pendências

### 4.5. Cruzamento
- **H20 — Sócio com cargo público** — mesmo CPF em empresa e no serviço público
- **H21 — Doação de campanha** — empresa que doou para político e ganhou contrato
- **H22 — Endereço fictício** — empresa com endereço que não existe
- **H23 — Empresa de fachada** — capital social baixo, faturamento alto

## 5. Modelo de Risco

Cada caso detectado recebe um **score de risco** (0-100) baseado em:

- **Severidade** — impacto potencial do desvio (peso 40%)
- **Probabilidade** — número de heurísticas acionadas (peso 30%)
- **Recorrência** — reincidência do agente ou fornecedor (peso 20%)
- **Exposição** — visibilidade pública do caso (peso 10%)

**Faixas:**
- 🟢 **0-30** — Baixo risco
- 🟡 **31-60** — Médio risco
- 🟠 **61-80** — Alto risco
- 🔴 **81-100** — Risco crítico

## 6. Arquitetura Técnica

### Coleta de Dados
- **Scrapers** — Python + BeautifulSoup / Playwright
- **APIs** — quando disponíveis (Portal da Transparência, TCU)
- **ETL** — Apache Airflow para orquestração
- **Storage** — Data Lake (S3) + Data Warehouse (PostgreSQL + dbt)

### Análise
- **Python** — pandas, numpy, scikit-learn
- **Grafos** — NetworkX para detectar conexões suspeitas
- **Machine Learning** — classificação de risco, detecção de anomalias
- **Regras** — heurísticas implementadas como queries SQL + scripts Python

### Apresentação
- **Dashboard** — Next.js + D3.js / Recharts
- **API** — FastAPI
- **Mobile** — React Native (visualização + alertas)

## 7. Privacidade e Ética

- **LGPD** — dados pessoais são anonimizados antes de qualquer análise
- **Presunção de inocência** — o score de risco é **sinalização**, não acusação
- **Transparência** — todas as heurísticas são públicas e auditáveis
- **Direito de resposta** — agentes e empresas podem contestar sinalizações
- **Não discriminação** — análises baseadas em dados, não em perfis

## 8. Modelo de Dados (Simplificado)

```sql
CREATE TABLE casos_suspeitos (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tipo VARCHAR(50) NOT NULL, -- 'licitacao', 'contrato', 'folha', etc.
  referencia_id VARCHAR(100), -- ID do item original
  heuristicas JSONB, -- lista de heurísticas acionadas
  score_risco INT,
  data_deteccao TIMESTAMP DEFAULT NOW(),
  status VARCHAR(20) DEFAULT 'novo' -- novo, em_analise, investigado, arquivado
);

CREATE TABLE heuristicas_acionadas (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  caso_id UUID REFERENCES casos_suspeitos(id),
  heuristica VARCHAR(10) NOT NULL, -- 'H1', 'H2', etc.
  evidencia JSONB -- dados que sustentam a sinalização
);
```

## 9. Interface do Usuário

### Dashboard Público
- **Mapa de calor** — casos por município/estado
- **Top 10** — casos com maior score de risco
- **Filtros** — por tipo, região, período, órgão
- **Detalhes** — clique para ver heurísticas acionadas e evidências

### Alertas
- **E-mail** — para usuários cadastrados
- **Push** — no app mobile
- **RSS / Webhook** — para integração com outros sistemas

### API Pública
- **GET /api/casos** — listar casos
- **GET /api/casos/:id** — detalhar caso
- **GET /api/heuristicas** — listar heurísticas disponíveis
- **POST /api/casos/:id/contestar** — direito de resposta

## 10. Roadmap

- **MVP (6 meses):** 10 heurísticas de licitação + dashboard básico
- **V1 (12 meses):** todas as 23 heurísticas + cruzamento de dados
- **V2 (18 meses):** ML para detectar novas heurísticas + API pública
- **V3 (24 meses):** integração com canais de denúncia (Feature de Denúncias)

## 11. Limitações e Disclaimer

- O Farejador **não substitui** o trabalho dos órgãos de controle
- Os resultados são **sinalizações**, não acusações
- Pode haver **falsos positivos** — toda sinalização deve ser investigada
- A ferramenta é **complementar** ao trabalho humano, não substituto

---

📌 *O Farejador não caça corruptos — ele ilumina padrões. Quem julga é a sociedade, com seus representantes eleitos e órgãos de controle.*
