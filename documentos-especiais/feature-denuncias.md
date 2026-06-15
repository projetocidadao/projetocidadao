# 📢 Feature de Denúncias — Especificação Técnica

> *"Qualquer cidadão é parte legítima para propor ação popular."* — Art. 5º, LXXIII, CF/88

## 1. Visão Geral

A Feature de Denúncias permite que qualquer cidadão envie denúncias sobre problemas públicos (corrupção, má prestação de serviços, violações de direitos) de forma **segura, anônima e rastreável**.

A denúncia é roteada automaticamente para o canal competente (CGU, MP, TCU, Ouvidoria, etc.) e o cidadão pode acompanhar o desfecho.

## 2. Objetivos

- **Empoderar o cidadão** — dar voz e instrumento
- **Reduzir burocracia** — um único formulário, múltiplos destinos
- **Proteger o denunciante** — anonimato, criptografia, sigilo
- **Aumentar a transparência** — denúncias viram dados abertos
- **Educar** — explicar onde, como e por que denunciar

## 3. Fluxo do Usuário (UX)

1. **Tela 1 — Categoria** — escolher tipo de problema:
   - Corrupção / desvio de recurso
   - Má prestação de serviço público
   - Violação de direito social (saúde, educação, etc.)
   - Violação ambiental
   - Assédio / discriminação
   - Outro

2. **Tela 2 — Localização** — onde aconteceu:
   - Município (autopreenchimento via CEP)
   - Estado
   - Endereço (opcional)
   - Data do fato

3. **Tela 3 — Descrição** — o que aconteceu:
   - Descrição detalhada (texto livre, 500-5000 caracteres)
   - Quem são os envolvidos (opcional, mas recomendado)
   - Valor estimado do dano (se aplicável)
   - Anexos: fotos, vídeos, PDFs, áudios (até 50 MB total)

4. **Tela 4 — Identificação** — quem está denunciando:
   - **Anônimo** — sem identificação, mas com código de rastreio
   - **Identificado** — nome, CPF, e-mail, telefone
   - **Pseudônimo** — apelido + código de rastreio

5. **Tela 5 — Confirmação** — revisar e enviar:
   - Resumo da denúncia
   - Canal de destino (automático, com opção de override)
   - Prazo estimado de resposta
   - Código de rastreio (gerado automaticamente)

6. **Tela 6 — Acompanhamento** — ver o status:
   - Recebida
   - Em análise
   - Encaminhada
   - Em investigação
   - Concluída (com desfecho)
   - Arquivada (com justificativa)

## 4. Arquitetura Técnica

### Backend
- **API REST** — Node.js + Express ou Python + FastAPI
- **Banco de dados** — PostgreSQL (com criptografia em repouso)
- **Fila de mensagens** — Redis ou RabbitMQ (para roteamento assíncrono)
- **Storage** — S3-compatible (para anexos)
- **Criptografia** — AES-256 para dados em repouso, TLS 1.3 para dados em trânsito

### Frontend (Mobile)
- **Framework** — React Native ou Flutter
- **Autenticação** — JWT + refresh token (apenas se identificado)
- **Offline-first** — denúncias salvas localmente e sincronizadas quando online
- **Acessibilidade** — WCAG 2.1 AA

### Web (Opcional)
- **Framework** — Next.js ou Vue.js
- **Dashboard público** — denúncias anonimizadas (estatísticas)

## 5. Modelo de Dados (PostgreSQL)

```sql
CREATE TABLE denuncias (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  codigo_rastreio VARCHAR(20) UNIQUE NOT NULL,
  categoria VARCHAR(50) NOT NULL,
  subcategoria VARCHAR(100),
  descricao TEXT NOT NULL,
  municipio VARCHAR(100),
  estado VARCHAR(2),
  endereco TEXT,
  data_fato DATE,
  valor_dano_estimado DECIMAL(15, 2),
  anonimo BOOLEAN DEFAULT TRUE,
  denunciante_id UUID REFERENCES usuarios(id),
  status VARCHAR(20) DEFAULT 'recebida',
  canal_destino VARCHAR(100),
  data_criacao TIMESTAMP DEFAULT NOW(),
  data_atualizacao TIMESTAMP DEFAULT NOW()
);

CREATE TABLE denuncia_anexos (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  denuncia_id UUID REFERENCES denuncias(id),
  arquivo_url TEXT NOT NULL,
  tipo VARCHAR(20), -- 'foto', 'video', 'pdf', 'audio'
  tamanho_bytes BIGINT
);

CREATE TABLE denuncia_historico (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  denuncia_id UUID REFERENCES denuncias(id),
  status_anterior VARCHAR(20),
  status_novo VARCHAR(20),
  comentario TEXT,
  data TIMESTAMP DEFAULT NOW()
);
```

## 6. Roteamento Automático

A denúncia é roteada para o canal competente com base na categoria e localização:

| Categoria | Destino |
|---|---|
| Corrupção / desvio | CGU, MP, TCU |
| Má prestação de serviço | Ouvidoria (municipal/estadual/federal) |
| Violação de direito social | Defensoria Pública, MP |
| Violação ambiental | IBAMA, MP |
| Assédio / discriminação | CADE, MP do Trabalho, Ouvidoria |
| Saúde | Ouvidoria do SUS, MP, CRM |
| Educação | MEC, MP |
| Transporte | ANTT, DNIT, MP |
| Segurança | Ouvidoria da PM, MP |
| Saneamento | ANA, MP |

## 7. Privacidade e Segurança

- **LGPD** — dados pessoais são criptografados e o denunciante pode solicitar exclusão
- **Anonimato** — se anônimo, o nome, CPF, e-mail e IP são **nunca** armazenados
- **Criptografia** — AES-256 em repouso, TLS 1.3 em trânsito
- **Sigilo** — apenas o canal de destino tem acesso aos dados
- **Auditoria** — todos os acessos são logados
- **Proteção de denunciante** — Lei 13.608/2019

## 8. API Endpoints

```
POST /api/denuncias — criar denúncia
GET /api/denuncias/:codigo_rastreio — consultar status
GET /api/denuncias/:id/historico — ver histórico
POST /api/denuncias/:id/anexos — adicionar anexo
PATCH /api/denuncias/:id/status — atualizar status (apenas canal de destino)
```

## 9. Métricas e KPIs

- **Tempo médio** de resposta por canal
- **Taxa de denúncias** por categoria e região
- **Taxa de conclusão** (com desfecho)
- **Satisfação do denunciante** (NPS)
- **Volume de dados abertos** (anônimos)

## 10. Roadmap

- **MVP (3 meses):** web + mobile, categorias básicas, roteamento para CGU/MP
- **V1 (6 meses):** anexos, histórico, dashboard público
- **V2 (12 meses):** IA para triagem automática, integração com mais canais
- **V3 (18 meses):** reconhecimento de padrões, alertas geográficos

---

📌 *Denunciar é um direito e um dever cívico. A Feature de Denúncias torna esse direito acessível a todos.*
