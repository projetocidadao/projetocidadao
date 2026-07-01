"""Cria um admin inicial para testes."""
import asyncio
from sqlalchemy import select
from src.db.session import AsyncSessionLocal
from src.db.models.usuario import Usuario
from src.core.security import hash_senha

async def main():
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Usuario).where(Usuario.email == "admin@projetocidadao.org")
        )
        existing = result.scalar_one_or_none()
        if existing:
            print(f"Admin já existe: {existing.email}")
            existing.is_admin = True
            existing.is_superuser = True
            await db.commit()
            print("Permissões atualizadas.")
            return

        admin = Usuario(
            email="admin@projetocidadao.org",
            nome="Administrador",
            senha_hash=hash_senha("admin123"),
            is_admin=True,
            is_superuser=True,
            ativo=True,
        )
        db.add(admin)
        await db.commit()
        await db.refresh(admin)
        print(f"Admin criado! id={admin.id}, email={admin.email}, senha=admin123")

asyncio.run(main())
