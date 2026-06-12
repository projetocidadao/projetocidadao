# 🏛️ Projeto Cidadão

> *"Todo poder emana do povo, para o povo."*
> — Art. 1º, parágrafo único, Constituição Federal de 1988

**Sistema brasileiro de transparência pública** que mapeia e fiscaliza os 3 poderes (Executivo, Legislativo, Judiciário) e suas ações em todas as áreas da vida pública.

Construído como uma **cooperativa digital de código aberto** — sem investidores, sem fins lucrativos, com governança comunitária.

---

## 📜 Fundamento Constitucional

O projeto se apoia em dois pilares da **Constituição Federal de 1988**:

> **Art. 5º, XIV** — *"É assegurado a todos o acesso à informação e protegido o direito à intimidade, à vida privada, à honra e à imagem das pessoas."* (Incluído pela EC nº 115/2022)

> **Art. 5º, LXXIII** — *"Qualquer cidadão é parte legítima para propor ação popular que vise a anulação de ato lesivo ao patrimônio público, à moralidade administrativa, ao meio ambiente e ao patrimônio histórico e cultural."* (Ação Popular)

Em outras palavras: **transparência é direito fundamental, e fiscalizar é dever cívico.**

---

## 🗂️ Documentos do Projeto

| Documento | O que tem dentro |
|-----------|------------------|
| 📐 [ESTRUTURA.md](ESTRUTURA.md) | Mapeamento completo dos 3 poderes, órgãos, dados públicos e pontos de fiscalização |
| 🏗️ [ARQUITETURA.md](ARQUITETURA.md) | Stack técnico (frontend, backend, banco, hospedagem) e APIs de integração |
| ⚖️ [GOVERNANCA.md](GOVERNANCA.md) | Modelo de cooperativa digital, copyleft, financiamento coletivo, tomada de decisão |
| 🎓 [CURSOS_GOVERNANCA.md](CURSOS_GOVERNANCA.md) | Sistema de cursos colaborativos: incubação por IA, regra das 3 aprovações, pontos pioneiros |
| 🏛️ [areas/README.md](areas/README.md) | Áreas temáticas da vida pública: saúde, educação, transporte, segurança, saneamento, finanças, alimentação, meio ambiente, cultura |
| 📚 [cursos/README.md](cursos/README.md) | Módulo educacional: cursos colaborativos sobre fiscalização e transparência |
| 📢 [DENUNCIAS.md](DENUNCIAS.md) | Canal de denúncias (cidadãos e servidores) e fluxo de apuração |
| 🐕 [FAREJADOR.md](FAREJADOR.md) | Farejador de Corrupção: varredura automatizada de dados públicos com IA |

---

## 🏛️ Os 3 Poderes

### ⚡ Executivo
Políticas públicas, gastos, programas sociais, licitações, contratos, servidores.
→ Detalhes em [ESTRUTURA.md → Executivo](ESTRUTURA.md#11-executivo)

### 📜 Legislativo
Deputados, senadores, vereadores, proposições, votações, leis, orçamento.
→ Detalhes em [ESTRUTURA.md → Legislativo](ESTRUTURA.md#12-legislativo)

### ⚖️ Judiciário
Tribunais, magistrados, processos, decisões, Ministério Público, sistema prisional.
→ Detalhes em [ESTRUTURA.md → Judiciário](ESTRUTURA.md#13-judici%C3%A1rio)

---

## 🏥 Áreas Temáticas

A fiscalização não vive só de poder — vive de **tema**. Por isso organizamos também por área da vida pública:

- 🏥 [Saúde](areas/saude.md) — SUS, hospitais, verbas, filas, programas
- 🎓 [Educação](areas/educacao.md) — escolas, FUNDEB, merenda, transporte escolar
- 🚌 [Transporte](areas/transporte.md) — mobilidade urbana, obras, concessões
- 🛡️ [Segurança](areas/seguranca.md) — polícias, sistema prisional, estatísticas
- 💧 [Saneamento](areas/saneamento.md) — água, esgoto, resíduos
- 💰 [Finanças](areas/financas.md) — orçamento público, LOA, LDO, execução
- 🍎 [Alimentação](areas/alimentacao.md) — segurança alimentar, PNAE, PAA
  - 📊 [Balanço da Desnutrição](areas/alimentacao-balanco-desnutricao.md) — acompanhamento evolutivo
- 🌱 [Meio Ambiente](areas/meio-ambiente.md) — licenciamento, desmatamento, recursos hídricos
- 🎭 [Cultura](areas/cultura.md) — patrimônio, Lei Aldir Blanc, diversidade

→ Veja detalhes e fontes em [areas/README.md](areas/README.md)

---

## 📢 Denúncias & Farejador de Corrupção

O projeto inclui **dois mecanismos complementares** para combate à corrupção:

- **📢 [Canal de Denúncias](DENUNCIAS.md)** — qualquer cidadão (comum ou servidor público) pode registrar uma denúncia, com proteção de identidade e fluxo de apuração
- **🐕 [Farejador de Corrupção](FAREJADOR.md)** — varredura automatizada com IA sobre dados públicos, identificando padrões suspeitos em licitações, contratos, folha de pagamento e declarações de bens

---

## 🔌 Fontes de Dados Integradas

| Fonte | Dados |
|-------|-------|
| [Portal da Transparência](https://portaldatransparencia.gov.br/) | Repasses, programas sociais, servidores |
| [Compras Governamentais](https://www.gov.br/compras/) | Licitações, contratos, atas |
| [Câmara dos Deputados](https://www.camara.leg.br/) | Proposições, votações, deputados |
| [Senado Federal](https://www12.senado.leg.gov.br/) | Projetos de lei, senadores |
| [CNJ / PJe](https://www.cnj.jus.br/) | Processos judiciais |
| [Dados Abertos Brasil](https://dados.gov.br/) | Catálogo geral de dados públicos |

---

## 💻 Stack Técnico

```
/backend          # API Python (FastAPI)
/mobile           # App React Native
/integracoes/     # Módulos de integração com fontes públicas
```

Frontend: **Next.js / React + TypeScript + Tailwind** • Banco: **PostgreSQL** • Deploy: **Vercel + Railway/AWS**
→ Detalhes em [ARQUITETURA.md](ARQUITETURA.md)

---

## 🤝 Como Contribuir

1. **Fork** este repositório
2. Crie uma **branch** para sua feature (`git checkout -b feature/minha-contribuicao`)
3. Faça suas alterações e **commit** (`git commit -m 'feat: adiciona...'`)
4. Envie um **Pull Request**

Quer criar **cursos** sobre fiscalização? Leia [CURSOS_GOVERNANCA.md](CURSOS_GOVERNANCA.md) — a comunidade te acolhe depois do período de incubação.

Tem dúvida sobre **como decisões são tomadas**? Comece por [GOVERNANCA.md](GOVERNANCA.md).

---

## 📜 Licença

**MIT License** — Projeto aberto para todos os cidadãos brasileiros.

---

*"A transparência é o antídoto contra a corrupção."* — Projeto Cidadão 🇧🇷
