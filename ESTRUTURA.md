# Estrutura do Sistema de Transparência Pública

---

## 1. Estrutura por Poder

### 1.1 EXECUTIVO
- **Presidente/Governador/Prefeito**
  - Decretos
  - Viagens
  - Gastos
- **Ministérios/Secretarias**
  - Estrutura organizacional
  - Funcionários
  - Orçamento
- **Órgãos Reguladores**
  - Licenças
  - Autorizações
  - Fiscalizações
- **Licitações e Contratos**
  - Chamamentos
  - Atas
  - Aditivos
  - Pagamentos
- **Serviços Públicos**
  - Escolas
  - Hospitais
  - Transporte
  - Saneamento

### 1.2 LEGISLATIVO
- **Deputados/Vereadores**
  - Presenças
  - Votações
  - Gastos
- **Comissões**
  - Relatórios
  - Audiências públicas
- **Leis**
  - Projetos
  - Tramitação
  - Aprovação
  - Vetos
- **Orçamento**
  - LOA (Lei Orçamentária Anual)
  - LDO (Lei de Diretrizes Orçamentárias)
  - Emendas
  - Execução

### 1.3 JUDICIÁRIO
- **Tribunais**
  - Processos
  - Decisões
  - Prazos
- **Magistrados**
  - Declarações patrimoniais
  - Processos
- **Ministério Público**
  - Inquéritos
  - Promotorias
- **Sistema Prisional**
  - Custódia
  - Progressão de pena

### 1.4 PONTOS COMUNS (todos os poderes)
- Folha de pagamento
- Patrimônio público
- Diárias e passagens
- Contratações temporárias
- Convênios e repasses

---

## 2. Modelo de Dados

### 2.1 Estrutura em Árvore
```
poder → órgão → função → dado público → ponto de fiscalização
```

### 2.2 Entidades Principais
- **Poder:** Executivo, Legislativo, Judiciário
- **Órgão:** Ministério, Secretaria, Tribunal, etc.
- **Função:** Atribuição legal do órgão
- **Dado Público:** Informação que deve ser disponibilizada
- **Ponto de Fiscalização:** Local onde o cidadão pode verificar

---

## 3. Módulos do Sistema


### Módulo 1 - Estrutura Organizacional
- Secretarias e departamentos
- Lista de responsáveis
- Organograma
- Competências

### Módulo 2 - Dados Abertos
- Licitações
- Contratos
- Convênios
- Diárias e passagens
- Folha de pagamento

### Módulo 3 - Legislação
- Leis municipais/estaduais/federais
- Projetos de lei
- Votações
- Histórico de tramitação

### Módulo 4 - Judiciary
- Processos públicos
- Decisões
- Prazos

### Módulo 5 - Cidadão

> "Qualquer cidadão é parte legítima para propor ação popular que vise a anulação de ato lesivo ao patrimônio público ou de entidade de que participe o Estado, à moralidade administrativa, ao meio ambiente e ao patrimônio histórico e cultural, ficam ressalvadas, nas hipóteses previstas nesta Constituição, as ações de natureza exclusivamente privada."
> — **Art. 5º, inciso LXXIII** da Constituição Federal de 1988

- **Cadastro anônimo (LGPD)** — proteção de dados do cidadão
- **Proteção de dados pessoais** — privacidade em primeiro lugar
- **Ferramentas de fiscalização** — mapas, dashboards, alertas
- **Direito de resposta** — canal para gestores públicos
- **Ação popular** — base constitucional para fiscalização

---

## 4. Fundamento Constitucional

A fiscalização cidadã tem base no **Art. 5º, inciso LXXIII** da Constituição Federal de 1988, que garante a qualquer cidadão o direito de:

1. **Ação Popular** — propor ação para anular atos lesivos ao:
   - Patrimônio público
   - Moralidade administrativa
   - Meio ambiente
   - Patrimônio histórico e cultural

2. **Mandado de Segurança** — Art. 5º, LXIX
   - Proteger direito líquido e certo violado por autoridade

3. **Direito de Petição** — Art. 5º, XXXIV
   - Petitionar autoridades para defesa de direitos

---

## 5. Fontes de Dados

- Portal da Transparência (federal, estadual, municipal)
- Sites das câmaras legislativas
- Tribunais de Justiça
- Diário Oficial
- APIs públicas de órgãos governamentais