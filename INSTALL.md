# 🚀 Projeto Cidadão - Guia de Instalação

## ⚡️ Instalação Rápida (1 comando)

```bash
curl -fsSL https://raw.githubusercontent.com/projetocidadao/projetocidadao/main/install.sh | bash
```

O script vai:
1. Verificar Docker/Compose
2. Pedir a senha do Postgres
3. Aplicar URL-encode automaticamente
4. Subir todos os containers
5. Aguardar a API ficar healthy

---

## Pré-requisitos

- Docker 20.10+ ([instalar](https://docs.docker.com/get-docker/))
- Docker Compose v2+ (já vem com Docker Desktop)
- Python 3 (só pra URL-encode da senha)

---

## Instalação Manual

Se preferir fazer passo a passo:

### 1. Clone o repositório
```bash
git clone https://github.com/projetocidadao/projetocidadao.git
cd projetocidadao
```

### 2. Configure o arquivo de ambiente
```bash
cp .env.example .env
nano .env
```

**Aviso:** Se sua senha tem caractere especial (`@`, `#`, etc.), ela precisa ser URL-encoded na DATABASE_URL:

| Senha original | Senha na DATABASE_URL |
|----------------|------------------------|
| `cidadao@123`  | `cidadao%40123`       |
| `senha#forte`  | `senha%23forte`       |

Dica: use Python pra encodar automaticamente:
```bash
python3 -c "import urllib.parse; print(urllib.parse.quote_plus(input()))"
# cole sua senha e pressione Enter
```

### 3. Suba os containers
```bash
docker compose up -d
```

### 4. Verifique a saúde da API
```bash
curl http://localhost:8000/health
```

---

## Troubleshooting

### Erro: `[Errno -2] Name or service not known`

O container da API não consegue resolver o hostname `db`.

**Solução:**
```bash
docker compose restart api
```

### Erro: `asyncpg` falha com senha correta

A senha tem caractere especial (`@`, `#`, etc.) e não foi URL-encoded.

**Solução:** encodar a senha na `DATABASE_URL` (veja tabela acima).

### Container reiniciando em loop

**Solução:**
```bash
docker compose logs api --tail 50
```

---

## Comandos Úteis

| Comando | O que faz |
|---------|-----------|
| `docker compose ps` | Lista containers |
| `docker compose logs -f api` | Logs ao vivo da API |
| `docker compose restart api` | Reinicia a API |
| `docker compose down` | Para tudo |
| `docker compose down -v` | Para tudo e apaga volumes |

---

## Como Contribuir

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/minha-feature`)
3. Commit (`git commit -m "feat: minha feature"`)
4. Push (`git push origin feature/minha-feature`)
5. Abra um Pull Request

## Licença

MIT License - Projeto Cidadão 2026
