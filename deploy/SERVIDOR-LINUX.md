# 🖥️ Deploy do Projeto Cidadão em Servidor Linux

Guia completo pra colocar o sistema rodando em uma máquina Linux própria (Ubuntu/Debian).

---

## 📋 Pré-requisitos

- Servidor Linux (Ubuntu 22.04+ ou Debian 12+ recomendado)
- Acesso root ou sudo
- 2 GB RAM mínimo (4 GB recomendado)
- 20 GB de disco livre
- Portas 80, 443, 5432, 6379, 8000 liberadas (ou as customizadas)

---

## 🚀 Passo a Passo

### 1. Instalar Docker e Docker Compose

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependências
sudo apt install -y ca-certificates curl gnupg

# Adicionar chave GPG oficial do Docker
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Adicionar repositório
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Adicionar seu usuário ao grupo docker (evita usar sudo sempre)
sudo usermod -aG docker $USER
newgrp docker

# Verificar instalação
docker --version
docker compose version
```

### 2. Clonar o Repositório

```bash
# Instalar git se não tiver
sudo apt install -y git

# Clonar
cd /opt
sudo git clone https://github.com/projetocidadao/projetocidadao.git
sudo chown -R $USER:$USER /opt/projetocidadao
cd projetocidadao
```

### 3. Configurar Variáveis de Ambiente

```bash
# Copiar template
cp .env.example .env

# Gerar chave JWT segura
JWT_SECRET=$(openssl rand -hex 32)
sed -i "s|JWT_SECRET=.*|JWT_SECRET=$JWT_SECRET|" .env

# Gerar senha forte do banco
DB_PASS=$(openssl rand -hex 16)
sed -i "s|POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD=$DB_PASS|" .env

# Ver o arquivo
cat .env
```

**Edite também** se necessário:
- `APP_URL` — seu domínio ou IP
- `POSTGRES_PASSWORD` — (já foi trocado acima)

### 4. Subir a Stack

```bash
# Build + start em background
docker compose up -d --build

# Acompanhar logs (Ctrl+C pra sair)
docker compose logs -f api
```

Aguarde aparecer `Application startup complete`.

### 5. Verificar se Está Funcionando

```bash
# Status dos containers
docker compose ps

# Health check
curl http://localhost:8000/api/health

# Documentação
# Abra no navegador: http://SEU_IP:8000/docs
```

### 6. Configurar Firewall

```bash
# Liberar portas essenciais
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw allow 8000/tcp    # API (opcional — nginx já faz proxy)

# Ativar firewall
sudo ufw enable
sudo ufw status
```

### 7. (Opcional) Configurar Domínio + SSL com Let's Encrypt

```bash
# Instalar certbot
sudo apt install -y certbot

# Obter certificado (substitua o domínio)
sudo certbot certonly --standalone -d seudominio.org -d www.seudominio.org

# Copiar para a pasta do nginx
sudo cp /etc/letsencrypt/live/seudominio.org/fullchain.pem nginx/certs/
sudo cp /etc/letsencrypt/live/seudominio.org/privkey.pem nginx/certs/
sudo chown $USER:$USER nginx/certs/*

# Editar nginx/conf.d/app.conf:
# - Descomente o bloco de redirecionamento HTTP→HTTPS
# - Descomente o bloco server 443
# - Substitua "_" por "seudominio.org"

# Recarregar nginx
docker compose restart nginx

# Renovação automática (certbot já cria um cron)
sudo certbot renew --dry-run
```

---

## 🛠️ Comandos Úteis do Dia a Dia

```bash
# Ver logs em tempo real
docker compose logs -f api

# Reiniciar só a API
docker compose restart api

# Entrar no container da API
docker compose exec api bash

# Rodar migrations manualmente
docker compose exec api alembic upgrade head

# Criar admin via CLI
docker compose exec api python -c "
import asyncio, os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select
from src.models.usuario import Usuario
from src.core.security import hash_password
from src.models.enums import UserRole

async def main():
    engine = create_async_engine(os.environ['DATABASE_URL'])
    Session = async_sessionmaker(engine, expire_on_commit=False)
    async with Session() as s:
        result = await s.execute(select(Usuario).where(Usuario.email == 'admin@projetocidadao.local'))
        if not result.scalar_one_or_none():
            u = Usuario(
                email='admin@projetocidadao.local',
                nome='Administrador',
                senha_hash=hash_password('SUA_SENHA_FORTE'),
                role=UserRole.ADMIN,
                verificado=True,
                ativo=True,
            )
            s.add(u)
            await s.commit()
            print('Admin criado!')
    await engine.dispose()

asyncio.run(main())
"

# Ver uso de recursos
docker stats

# Limpar logs antigos do Docker
sudo sh -c 'truncate -s 0 /var/lib/docker/containers/*/*-json.log'
```

---

## 💾 Backup e Restore

### Backup Manual

```bash
# Backup do banco
docker compose exec db pg_dump -U cidadao projetocidadao > backup_$(date +%Y%m%d).sql

# Backup da pasta de mídia (anexos)
tar -czf media_$(date +%Y%m%d).tar.gz -C backend media/
```

### Restore

```bash
# Restaurar banco
cat backup_20260615.sql | docker compose exec -T db psql -U cidadao projetocidadao

# Restaurar mídia
tar -xzf media_20260615.tar.gz -C backend/
```

### Backup Automático (já configurado!)

O serviço `backup` no `docker-compose.yml` faz backup diário automático em `./backups/`, mantendo:
- 7 dias de backups diários
- 4 semanas de backups semanais
- 6 meses de backups mensais

---

## 🔒 Checklist de Segurança

- [ ] Senha do Postgres trocada (não usar `mudar123`)
- [ ] JWT_SECRET gerado aleatoriamente
- [ ] SSH com chave (desabilitar login por senha)
- [ ] Firewall ativado (ufw)
- [ ] Fail2ban instalado
- [ ] Updates automáticos do sistema
- [ ] Backup automático testado
- [ ] SSL/HTTPS configurado (Let's Encrypt)
- [ ] Senha do admin padrão trocada (criar admin novo e desabilitar o padrão)
- [ ] Cloudflare na frente (DDoS + WAF grátis)

```bash
# Instalar fail2ban
sudo apt install -y fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Updates automáticos
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

---

## 🔄 Atualizando o Sistema

```bash
cd /opt/projetocidadao

# Puxar últimas mudanças
git pull origin main

# Rebuild e reiniciar
docker compose up -d --build

# Rodar migrations (se houver)
docker compose exec api alembic upgrade head
```

---

## 🆘 Solução de Problemas

### "Port 8000 already in use"

```bash
# Ver o que está usando
sudo lsof -i :8000

# Mudar porta no .env
echo "API_PORT=8001" >> .env
docker compose up -d
```

### "Database connection refused"

```bash
# Ver logs do banco
docker compose logs db

# Recriar (CUIDADO: apaga dados)
docker compose down -v
docker compose up -d
```

### Containers reiniciando em loop

```bash
# Ver o erro
docker compose logs api
```

### Espaço em disco

```bash
# Ver uso do Docker
docker system df

# Limpar coisas não usadas
docker system prune -a
```

---

## 📊 Monitoramento

```bash
# Ver uso de recursos em tempo real
docker stats

# Health check
curl http://localhost:8000/api/health

# Logs estruturados
docker compose logs --tail=100 api
```

Para monitoramento mais robusto, considere:
- **Uptime Kuma** (free, self-hosted) — alerta se o site cair
- **Prometheus + Grafana** — métricas e dashboards
- **Sentry** — tracking de erros

---

## 🎯 Próximos Passos

Depois que o sistema estiver rodando:

1. ✅ Criar admin real (trocar senha do padrão)
2. ✅ Configurar domínio + SSL
3. ✅ Configurar backups externos (B2, S3)
4. ✅ Adicionar monitoramento (Uptime Kuma)
5. ✅ Configurar CI/CD (GitHub Actions → deploy automático)
6. ✅ Documentar processos no wiki do projeto

---

**Dúvidas?** Abra uma issue no [GitHub](https://github.com/projetocidadao/projetocidadao/issues) 🚀
