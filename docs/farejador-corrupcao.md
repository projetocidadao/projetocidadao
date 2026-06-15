# 🕵️ Feature: Farejador de Corrupção

> *"A corrupção é o maior obstáculo ao desenvolvimento. A transparência é o antídoto."*
> — Projeto Cidadão

## 1. Objetivo

O **Farejador de Corrupção** é um sistema automatizado que monitora dados públicos em busca de padrões suspeitos de corrupção, licitações irregulares, superfaturamento, nepotismo e outros desvios.

## 2. Escopo

- Monitorar continuamente portais de transparência
- Cruzar dados de diferentes fontes
- Identificar padrões suspeitos via IA
- Alertar cidadãos e jornalistas
- Alimentar a base de dados do Projeto Cidadão

## 3. Fontes de Dados

O farejador consome dados de:

- [x] **Portal da Transparência** — gastos, programas, servidores
- [x] **Compras Governamentais** — licitações, contratos, atas
- [x] **Câmara dos Deputados** — proposições, votações
- [x] **Senado Federal** — projetos, senadores
- [x] **CNJ** — processos judiciais
- [x] **Diário Oficial** — nomeações, exonerações
- [x] **CEIS / CNEP** — empresas e pessoas impedidas de licitar
- [x] **TCEs / TCUs** — tribunais de contas estaduais e federal
- [x] **Receita Federal** — CNPJ, sócios, dívidas
- [x] **IBAMA / ICMBio** — autos de infração ambiental
- [x] **INPE** — desmatamento, queimadas
- [x] **ANATEL / ANEEL / ANVISA** — agências reguladoras
- [x] **Denúncias** — denúncias enviadas na plataforma

## 4. Padrões Suspeitos Detectados

### 4.1. Licitações
- **Falta de concorrentes** (apenas 1 proposta)
- **Vencedor recorrente** (mesma empresa sempre ganha)
- **Empate técnico suspeito** (preços muito próximos)
- **Pregão com dispensa** (urgência fabricada)
- **Valor muito acima** do preço de mercado
- **Objeto genérico** (descrição vaga)

### 4.2. Gastos
- **Gastos em alta** (aumento sem justificativa)
- **Gastos com fornecedor único**
- **Pagamentos atrasados** (sinal de desvio)
- **Reembolso suspeito** (despesas sem comprovação)
- **Diárias excessivas** (viagens sem propósito)

### 4.3. Contratos
- **Aditivos excessivos** (aumento de valor sem justificativa)
- **Prorrogações suspeitas** (renovação automática)
- **Subcontratação irregular**
- **Contrato sem fiscal** (sem responsável)

### 4.4. Servidores
- **Acumulação irregular de cargos**
- **Remuneração acima do teto**
- **Nepotismo** (parentes em cargos comissionados)
- **Nomeações em época eleitoral** (aproveitamento político)

### 4.5. Empresas
- **Sócios com processos** (sócios com ficha suja)
- **Empresa fantasma** (CNPJ sem atividade)
- **Mudança repentina de sócios** (sinal de alerta)
- **Empresa em endereço falso**
- **Empresa com capital social baixo** para o contrato

### 4.6. Pessoas
- **Políticos com empresas** (conflito de interesse)
- **Políticos em CPFs inválidos** (suspeita de laranja)
- **Patrimônio incompatível** com a renda declarada
- **Vínculos com empresas investigadas**

## 5. Algoritmo de Detecção

```python
# Pseudocódigo simplificado

def farejar(dados):
    padroes_suspeitos = []
    
    for licitacao in dados.licitacoes:
        if licitacao.numero_propostas == 1:
            padroes_suspeitos.append({
                'tipo': 'FALTA_CONCORRENTES',
                'licitacao_id': licitacao.id,
                'severidade': 'ALTA'
            })
        
        if licitacao.vencedor_ja_ganhou(ultimas=10):
            padroes_suspeitos.append({
                'tipo': 'VENCEDOR_RECORRENTE',
                'licitacao_id': licitacao.id,
                'severidade': 'MEDIA'
            })
        
        if licitacao.valor > preco_medio_mercado * 1.5:
            padroes_suspeitos.append({
                'tipo': 'SUPERFATURAMENTO',
                'licitacao_id': licitacao.id,
                'severidade': 'ALTA'
            })
    
    return padroes_suspeitos
```

## 6. Score de Risco

Cada entidade (empresa, pessoa, licitação) recebe um **score de risco** de 0 a 100:

- **0-30:** Baixo risco
- **31-60:** Médio risco
- **61-80:** Alto risco
- **81-100:** Risco crítico

O score é calculado com base em:
- Número de padrões suspeitos detectados
- Severidade dos padrões
- Histórico da entidade
- Cruzamento com outras fontes

## 7. Alertas

O farejador envia alertas quando:

- Score de risco ultrapassa 60
- Novo padrão crítico é detectado
- Mudança repentina no padrão de gastos
- Denúncia relacionada é criada

## 8. Privacidade e Ética

- **LGPD:** Conformidade com a Lei Geral de Proteção de Dados
- **Transparência:** Algoritmo é aberto e auditável
- **Não discriminação:** Não usar dados sensíveis (raça, religião, etc.)
- **Direito de defesa:** Entidades podem contestar o score

## 9. Integração com Outros Módulos

- **Denúncias:** Alimenta a base de denúncias
- **Áreas Temáticas:** Vincula suspeitas às áreas correspondentes
- **Cursos:** Sugere cursos sobre temas detectados
- **Mapa:** Mostra suspeitas no mapa

## 10. Stack Técnica

- **Linguagem:** Python (Pandas, Scikit-learn)
- **Banco de Dados:** PostgreSQL
- **Jobs:** Apache Airflow / Celery
- **IA:** Machine Learning supervisionado
- **API:** FastAPI
- **Visualização:** Grafana / D3.js

## 11. Roadmap

- [x] Especificação do algoritmo
- [ ] Coleta de dados (ETL)
- [ ] Modelo de ML supervisionado
- [ ] API de score de risco
- [ ] Dashboard público
- [ ] Alertas (email, push, Telegram)
- [ ] Integração com denúncias
- [ ] Mapa interativo

---

📌 *O farejador não substitui o julgamento humano — ele amplifica a capacidade de fiscalização do cidadão. A tecnologia a serviço do controle social.*
