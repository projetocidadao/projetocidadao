# 🏛️ Projeto Cidadão

> Plataforma colaborativa de transparência pública, fiscalização cidadã e educação para a participação social.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Status: Em Construção](https://img.shields.io/badge/Status-Em%20Construção-yellow.svg)](#)

## Sobre o Projeto

O **Projeto Cidadão** é uma iniciativa open source que visa aproximar o cidadão do poder público, fornecendo ferramentas para **fiscalizar**, **denunciar**, **aprender** e **participar** da vida pública.

Acreditamos que a transparência é o antídoto contra a corrupção — e que o cidadão é o principal agente dessa transformação.

## Estrutura do Repositório

```
projetocidadao/
├── README.md                       # Este arquivo
├── LICENSE                         # Licença MIT
├── CONTRIBUTING.md                 # Como contribuir
├── CODE_OF_CONDUCT.md              # Código de conduta
│
├── areas/                          # Áreas temáticas
│   ├── README.md                   # Índice de áreas
│   ├── saude.md
│   ├── educacao.md
│   ├── alimentacao.md
│   ├── transporte.md
│   ├── seguranca.md
│   ├── saneamento.md
│   ├── financas.md
│   ├── meio-ambiente.md
│   └── cultura.md
│
├── cursos/                         # Cursos educacionais
│   ├── README.md                   # Índice de cursos
│   ├── orgaos-publicos.md
│   ├── direito-constitucional.md
│   ├── fiscalizacao-cidada.md
│   ├── licitacoes-contratos.md
│   ├── dados-abertos.md
│   ├── tecnologia-transparencia.md
│   ├── meio-ambiente.md
│   └── cultura.md
│
├── docs/                           # Documentação técnica
│   ├── GOVERNANCA.md               # Modelo de governança
│   ├── CURSOS_GOVERNANCA.md        # Governança dos cursos
│   ├── denuncias.md                # Feature de denúncias
│   ├── farejador-corrupcao.md      # Farejador de corrupção
│   ├── api.md                      # Documentação da API
│   └── LGPD.md                     # Conformidade com a LGPD
│
├── backend/                        # API REST
│   ├── README.md                   # Stack e modelo de dados
│   ├── src/
│   ├── prisma/
│   ├── tests/
│   ├── docker-compose.yml
│   └── Dockerfile
│
└── mobile/                         # App mobile
    ├── README.md                   # Stack e telas
    ├── src/
    ├── app.json
    └── eas.json
```

## Áreas Temáticas

O projeto cobre **9 áreas temáticas** com cursos, denúncias, dados públicos e dashboards:

- 🏥 [Saúde](./areas/saude.md)
- 🎓 [Educação](./areas/educacao.md)
- 🍞 [Alimentação](./areas/alimentacao.md)
- 🚗 [Transporte](./areas/transporte.md)
- 👮 [Segurança](./areas/seguranca.md)
- 💧 [Saneamento](./areas/saneamento.md)
- 💰 [Finanças](./areas/financas.md)
- 🌱 [Meio Ambiente](./areas/meio-ambiente.md)
- 🎭 [Cultura](./areas/cultura.md)

## Cursos

**8 cursos** sobre transparência, fiscalização e direitos do cidadão:

- 🏛️ [Órgãos Públicos](./cursos/orgaos-publicos.md)
- ⚖️ [Direito Constitucional](./cursos/direito-constitucional.md)
- 🛡️ [Fiscalização Cidadã](./cursos/fiscalizacao-cidada.md)
- 📜 [Licitações e Contratos](./cursos/licitacoes-contratos.md)
- 📊 [Dados Abertos](./cursos/dados-abertos.md)
- 💻 [Tecnologia e Transparência](./cursos/tecnologia-transparencia.md)
- 🌱 [Meio Ambiente](./cursos/meio-ambiente.md)
- 🎭 [Cultura](./cursos/cultura.md)

## Features

- 📢 **Denúncias Cidadãs** — envie e acompanhe denúncias com foto, vídeo e geolocalização
- 🕵️ **Farejador de Corrupção** — sistema automatizado que monitora dados públicos em busca de padrões suspeitos
- 🗺️ **Mapa Interativo** — visualize denúncias e áreas críticas
- 📊 **Dashboards** — gastos públicos em tempo real
- 🎓 **Cursos** — educação para a cidadania
- 🏆 **Sistema de Pontos** — gamificação para incentivar a participação
- 🔒 **LGPD** — conformidade com a Lei Geral de Proteção de Dados

## Tecnologias

- **Backend:** Node.js + TypeScript + Express + Prisma + PostgreSQL
- **Mobile:** React Native + Expo + TypeScript
- **IA/ML:** Python (Farejador de Corrupção)
- **Infra:** Docker + Docker Compose
- **CI/CD:** GitHub Actions

## Como Contribuir

Quer ajudar? Veja [CONTRIBUTING.md](./CONTRIBUTING.md) e [GOVERNANÇA](./docs/GOVERNANCA.md) para entender o modelo de governança colaborativa.

```bash
# 1. Fork o repositório
# 2. Crie uma branch (git checkout -b feature/minha-contribuicao)
# 3. Faça commit (git commit -m 'feat: minha contribuição')
# 4. Push (git push origin feature/minha-contribuicao)
# 5. Abra um Pull Request
```

## Licença

Este projeto está licenciado sob a [Licença MIT](./LICENSE).

## Contato

- **Repositório:** [github.com/projetocidadao/projetocidadao](https://github.com/projetocidadao/projetocidadao)
- **Issues:** [github.com/projetocidadao/projetocidadao/issues](https://github.com/projetocidadao/projetocidadao/issues)
- **Discussões:** [github.com/projetocidadao/projetocidadao/discussions](https://github.com/projetocidadao/projetocidadao/discussions)

---

📌 *Todo poder emana do povo, para o povo. A transparência é o caminho, a fiscalização é o meio, a cidadania é o destino.*
