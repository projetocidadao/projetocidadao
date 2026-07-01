#!/bin/bash
set -e

echo "🚀 Projeto Cidadão - Installer"
echo "================================"
echo ""

# 1. Verifica Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não encontrado. Instale em: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker compose &> /dev/null; then
    echo "❌ Docker Compose não encontrado."
    exit 1
fi

echo "✅ Docker encontrado"

# 2. Pede a senha do Postgres
echo ""
echo "📝 Configuração do Banco de Dados"
echo "--------------------------------"
read -p "Senha do Postgres (ex: cidadao@123): " DB_PASSWORD
DB_PASSWORD_ENCODED=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$DB_PASSWORD', safe=''))")

echo ""
echo "🔐 Senha original: $DB_PASSWORD"
echo "🔐 Senha encoded:  $DB_PASSWORD_ENCODED"

# 3. Cria o .env
cat > .env << EENV
POSTGRES_USER=cidadao
POSTGRES_PASSWORD=${DB_PASSWORD}
POSTGRES_DB=projetocidadao
DATABASE_URL=postgresql+asyncpg://cidadao:${DB_PASSWORD_ENCODED}@db:5432/projetocidadao
EENV

echo "✅ Arquivo .env criado"

# 4. Sobe os containers
echo ""
echo "🐳 Subindo containers..."
docker compose down 2>/dev/null || true
docker compose up -d --build

# 5. Aguarda a API
echo ""
echo "⏳ Aguardando API ficar healthy..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ API online!"
        break
    fi
    sleep 2
done

echo ""
echo "🎉 Instalação concluída!"
echo ""
echo "📡 API:    http://localhost:8000"
echo "📚 Docs:   http://localhost:8000/docs"
echo "🗄  Banco:  localhost:5432"
echo ""
echo "📋 Comandos úteis:"
echo "  - Ver logs:    docker compose logs -f api"
echo "  - Parar:       docker compose down"
echo "  - Reiniciar:   docker compose restart"
