# 📊 Balanço Real da Desnutrição — Acompanhamento Evolutivo

> Documento dedicado ao **monitoramento longitudinal** dos indicadores de desnutrição no Brasil, fundamental para avaliar o impacto do Projeto Cidadão e das políticas públicas ao longo do tempo.

## 🎯 Objetivo

Construir uma **linha de base sólida e rastreável** da desnutrição no Brasil, que permita:

1. **Comparar** a situação antes, durante e depois da implantação do Projeto Cidadão
2. **Medir o impacto** das políticas públicas e da mobilização social
3. **Identificar** populações invisibilizadas pelo sistema
4. **Cobrar políticas** com base em evidências
5. **Alertar precocemente** crises alimentares regionais

## 📐 Marco Conceitual

A desnutrição é multidimensional — não se mede só com peso. Usamos 4 eixos:

```
            ┌─────────────────────────────────────────────┐
            │         ESTADO NUTRICIONAL (RESULTADO)      │
            │  Peso, Altura, IMC, Anemia, Deficiências   │
            └─────────────────────────────────────────────┘
                          ▲              ▲
                          │              │
       ┌──────────────────┘              └──────────────────┐
       │                                                     │
┌──────────────────┐                              ┌──────────────────┐
│ DETERMINANTES    │                              │ INSTRUMENTOS     │
│ ESTRUTURAIS      │                              │ DE POLÍTICA      │
│                  │                              │                  │
│ - Renda          │                              │ - Bolsa Família  │
│ - Saneamento     │                              │ - PNAE (merenda) │
│ - Moradia        │                              │ - PAA            │
│ - Escolaridade   │                              │ - SUS (Básico)   │
│ - Raça/Etnia     │                              │ - CadÚnico       │
│ - Território     │                              │ - Ater. sanitária│
└──────────────────┘                              └──────────────────┘
```

## 📊 Indicadores-Chave (Acompanhamento Evolutivo)

### Indicadores de Resultado (Diretos)

| Indicador | Fonte | Frequência | Idade-alvo |
|-----------|-------|-----------|------------|
| **Prevalência de desnutrição aguda (P/A ou IMC/I abaixo de -2 DP)** | Sisvan, POF | Mensal (Sisvan) / 5 anos (POF) | < 5 anos |
| **Prevalência de desnutrição crônica (E/I abaixo de -2 DP)** | Sisvan, POF | Mensal / 5 anos | < 5 anos |
| **Prevalência de baixo peso ao nascer (< 2.500g)** | SINASC | Mensal | Recém-nascidos |
| **Mortalidade por desnutrição (CID-10: E40-E46)** | SIM | Mensal | Todas as idades |
| **Internações por desnutrição** | SIH/SUS | Mensal | < 5 anos prioritário |
| **Anemia em crianças e gestantes** | Sisvan, ENANI | Anual | < 5 anos, gestantes |
| **Deficiência de vitamina A** | ENANI | 5 anos | < 5 anos |
| **Hipovitaminose A, D, B12, Ácido fólico** | ENANI | 5 anos | Crianças |
| **Baixo IMC em adultos (IMC < 18,5)** | VIGITEL | Anual | ≥ 18 anos |

### Indicadores de Determinante (Contexto)

| Indicador | Fonte | Frequência |
|-----------|-------|-----------|
| **Insegurança alimentar grave (%)** | VIGISAN, PNAD | Anual |
| **Famílias no CadÚnico** | MDS | Mensal |
| **Beneficiários do Bolsa Família** | MDS/CEF | Mensal |
| **Crianças no PNAE** | FNDE | Mensal |
| **Compra da agricultura familiar (mín. 30%)** | FNDE/SIGPC | Anual |
| **Cesta básica / Salário mínimo** | DIEESE | Mensal |
| **Cobertura de água/esgoto (Snis)** | SNIS | Anual |
| **População em extrema pobreza (POF)** | IBGE | Anual |

## 🗓️ Linha do Tempo (a partir de 2025)

### Ano 0 (Linha de Base — 2024-2025)
- [ ] Snapshot inicial de todos os indicadores acima
- [ ] Cruzamento raça/etnia, região, idade, território
- [ ] Publicação do "**0º Balanço da Desnutrição**" como documento histórico
- [ ] Definição de **metas de redução** para 4 e 8 anos

### Acompanhamento Anual (a partir de 2026)
- [ ] Painel dinâmico com atualização de todos os indicadores
- [ ] Relatório anual de progresso
- [ ] Comparação com metas propostas
- [ ] Identificação de territórios prioritários

### Marcos de Avaliação
- [ ] **2027** (2 anos) — Revisão intermediária
- [ ] **2028** (3 anos) — Publicação do "1º Balanço de Impacto"
- [ ] **2030** (5 anos) — Comparação com metas de ODS 2 (Fome Zero)
- [ ] **2033** (8 anos) — Avaliação de longo prazo

## 📈 Visualizações Previstas

- 📊 **Série temporal** por indicador (linha de tendência 2010-2033)
- 🗺️ **Mapas de calor** por município (desnutrição infantil, insegurança grave)
- 👥 **Equidade** — desagregação por raça, etnia, gênero, região
- 📉 **Benchmarking** — comparação entre municípios e estados
- 🏆 **Ranking** — melhores e piores indicadores por região

## 🛠️ Implementação Técnica

### Coleta de Dados
- 🔄 Integração via API com Sisvan, MDS, FNDE, CONAB, SNIS, SIM, SINASC
- 📡 Web scraping ético de portais municipais
- 📝 Canal direto de relato comunitário (voluntário e anônimo)

### Armazenamento
- 🗃️ **PostgreSQL** para séries temporais estruturadas
- 📊 **Data lake** (S3) para PDFs e arquivos brutos
- 🕒 Versionamento por data de corte (imutável)

### Visualização
- 📱 App mobile (RN) com gráficos e mapas
- 💻 Web (Next.js) com dashboards
- 🔔 Alertas quando indicadores pioram

## 🎯 Metas Propostas (referência aos ODS 2 — Fome Zero)

| Meta | Indicador | 2024 (Linha de Base) | Meta 2030 |
|------|-----------|----------------------|-----------|
| 2.1 | Fome → acesso a alimentos seguros | — | < 5% insegurança grave |
| 2.2 | Desnutrição em < 5 anos | — | < 2,5% desnutrição crônica |
| 2.3 | Produtividade agricultura familiar | — | +50% renda média |
| 2.A | Investimento em agricultura | — | Cumprimento de planos |
| 2.B | Volatilidade dos preços | — | -30% variação cesta básica |

> ⚠️ *As metas serão detalhadas com base no 0º Balanço e revisadas por epidemiologistas e nutricionistas da rede.*

## 🤝 Como contribuir

1. **Dados** — ajudar a cruzar fontes, identificar bases históricas
2. **Análise** — epidemiologistas, nutricionistas, estatísticos
3. **Visualização** — designers, devs front-end, especialistas em UX
4. **Comunicação** — jornalistas, comunicadores populares
5. **Articulação** — entidades de saúde, conselhos, universidades

📌 *A fome não espera — nem o projeto.*

## 📚 Referências Técnicas

- [Sisvan — Sistema de Vigilância Alimentar e Nutricional](https://sisaps.saude.gov.br/sisvan/)
- [ENANI — Estudo Nacional de Alimentação e Nutrição Infantil](https://enani.nutricao.ufrj.br/)
- [VIGISAN — Insegurança Alimentar (UFRJ)](https://olheparaafome.com.br/)
- [PNAD / POF — IBGE](https://www.ibge.gov.br/)
- [SIM — Sistema de Mortalidade (DATASUS)](https://datasus.saude.gov.br/sistema-de-informacao-sobre-mortalidade-sim/)
- [POF — Pesquisa de Orçamentos Familiares](https://www.ibge.gov.br/estatisticas/sociais/populacao/24786-pesquisa-de-orcamentos-familiares-2.html)
- [VIGITEL — Vigilância de Doenças Crônicas](https://www.gov.br/saude/pt-br/centrais-de-conteudo/apresentacoes/2021/vigitel)
- [DIEESE — Cesta Básica](https://www.dieese.org.br/cesta/)
- [Rede Brasileira de Pesquisa em Soberania e Segurança Alimentar](https://pesquisassan.net.br/)
- [Conselho Federal de Nutricionistas](https://www.cfn.org.br/)
- [CGAN — Coordenação-Geral de Alimentação e Nutrição](https://www.gov.br/saude/pt-br/composicao/saps/cgan)

---

🇧🇷 *O Brasil é o país que mais reduziu a fome no mundo entre 2002 e 2013. Voltou a subir. Este balanço é o nosso mapa para reverter.*
