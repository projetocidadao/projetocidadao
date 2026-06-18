#!/bin/bash
set -e

echo "==> Aguardando banco de dados..."
python << 'EOF'
import asyncio, asyncpg, os, time
async def wait():
    db_url = os.environ.get('DATABASE_URL', '')
    pg_url = db_url.replace('postgresql+asyncpg://', 'postgresql://')
    for i in range(30):
        try:
            conn = await asyncpg.connect(pg_url)
            await conn.close()
            print('Banco OK')
            return
        except Exception as e:
            print(f'Tentativa {i+1}/30: {e}')
            await asyncio.sleep(2)
    raise Exception('Banco não respondeu')
asyncio.run(wait())
EOF

echo "==> Rodando migrations..."
alembic upgrade head || echo "Aviso: migrations falharam (talvez seja a primeira vez)"

echo "==> Criando admin padrão (se não existir)..."
python << 'EOF' || echo "Aviso: não criou admin"
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
        existing = result.scalar_one_or_none()
        if not existing:
            u = Usuario(
                email='admin@projetocidadao.local',
                nome='Administrador',
                senha_hash=hash_password('admin123'),
                role=UserRole.ADMIN,
                verificado=True,
                ativo=True,
            )
            s.add(u)
            await s.commit()
            print('Admin criado: admin@projetocidadao.local / admin123')
        else:
            print('Admin já existe')
    await engine.dispose()

asyncio.run(main())
EOF

echo "==> Iniciando API..."
exec uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers ${WORKERS:-2} --proxy-headers
