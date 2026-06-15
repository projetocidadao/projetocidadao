# 📢 Feature: Denúncias Cidadãs

> *"A participação popular é essencial para o controle da gestão pública."*
> — Lei 12.527/2011 (LAI), Art. 3º

## 1. Objetivo

Permitir que o cidadão envie denúncias de problemas públicos, irregularidades, corrupção e descumprimento de direitos, integrando-se ao sistema de fiscalização do Projeto Cidadão.

## 2. Escopo

- Qualquer cidadão pode enviar uma denúncia
- Denúncias são categorizadas por área temática
- Denúncias podem ser anônimas ou identificadas
- Denúncias são georreferenciadas (opcional)
- Denúncias podem ter anexos (fotos, documentos, vídeos)

## 3. Categorias

As denúncias devem ser classificadas em uma das seguintes categorias:

### 3.1. Saúde
- Falta de medicamentos
- Demora no atendimento
- Condições precárias de unidades
- Desvios de recursos

### 3.2. Educação
- Falta de vagas
- Condições precárias de escolas
- Desvios de recursos da merenda
- Desvios de recursos do transporte escolar

### 3.3. Transporte
- Más condições de vias
- Falta de transporte público
- Atrasos em obras
- Desvios em contratos

### 3.4. Segurança
- Falta de policiamento
- Violência policial
- Condições precárias de presídios
- Desvios de recursos

### 3.5. Saneamento
- Falta de água
- Falta de esgoto
- Desvios em contratos
- Poluição

### 3.6. Finanças
- Gastos suspeitos
- Licitações irregulares
- Desvios de verba
- Superfaturamento

### 3.7. Alimentação
- Desnutrição
- Fome
- Desvios em programas de alimentação

### 3.8. Meio Ambiente
- Desmatamento ilegal
- Queimadas
- Poluição
- Desvios em contratos ambientais

### 3.9. Cultura
- Desvios em recursos da cultura
- Falta de acesso a bens culturais
- Descaso com patrimônio histórico

## 4. Fluxo da Denúncia

```
[1] Cidadão preenche formulário
        ↓
[2] Validação automática (IA)
        ↓
[3] Publicação na plataforma
        ↓
[4] Notificação aos usuários da região
        ↓
[5] Acompanhamento (status, comentários, evidências)
        ↓
[6] Resolução (pelo poder público) ou encaminhamento (MP, TCU, etc.)
```

## 5. Modelo de Dados

```typescript
type Denuncia = {
  id: string
  categoria: CategoriaDenuncia
  titulo: string
  descricao: string
  anonima: boolean
  autor?: Usuario
  localizacao?: {
    lat: number
    lng: number
    endereco: string
  }
  anexos: Anexo[]
  status: 'aguardando' | 'em_analise' | 'em_andamento' | 'resolvida' | 'rejeitada'
  comentarios: Comentario[]
  votos: number
  criadaEm: string
  atualizadaEm: string
}
```

## 6. Privacidade e Segurança

- **Anonimato:** Denúncias anônimas não revelam o autor
- **Criptografia:** Dados sensíveis são criptografados em repouso e em trânsito
- **LGPD:** Conformidade com a Lei Geral de Proteção de Dados
- **Proteção do denunciante:** Lei 13.608/2019

## 7. Integração com Outros Módulos

- **Áreas Temáticas:** Cada denúncia é vinculada à área correspondente
- **Farejador de Corrupção:** Denúncias alimentam o farejador
- **Cursos:** Usuários podem sugerir cursos sobre temas denunciados
- **Mapa:** Denúncias aparecem no mapa interativo

## 8. Stack Técnica

- **Backend:** Node.js + Express + Prisma + PostgreSQL
- **Frontend (Mobile):** React Native + Expo
- **Frontend (Web):** Next.js + TailwindCSS
- **Storage:** S3 / Cloudflare R2 (para anexos)
- **IA:** Validação e categorização automática

## 9. Roadmap

- [x] Especificação do modelo de dados
- [ ] API de denúncias (CRUD)
- [ ] UI mobile (formulário, lista, detalhes)
- [ ] UI web (painel administrativo)
- [ ] Notificações push
- [ ] Integração com o farejador de corrupção
- [ ] Mapa de denúncias
- [ ] Exportação de relatórios

---

📌 *A denúncia é o primeiro passo para a transformação — mas não o último. O Projeto Cidadão acompanha o desfecho.*
