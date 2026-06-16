"""
Script de seed — popula o banco com dados iniciais
Áreas temáticas + usuário admin + categorias de heurísticas

Uso: python -m src.db.seed
"""
import asyncio
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.db.models.usuario import Usuario, Role
from src.db.models.area import Area
from src.db.session import async_session, engine


AREAS_INICIAIS = [
    {
        "slug": "saude",
        "nome": "Saúde",
        "descricao": "SUS, programas de saúde, dados epidemiológicos, fiscalização de unidades e gastos da saúde pública.",
        "icone": "hospital",
        "cor": "#E11D48",
        "ordem": 1,
    },
    {
        "slug": "educacao",
        "nome": "Educação",
        "descricao": "MEC, IDEB, financiamento da educação, fiscalização de merenda, transporte escolar e condições das escolas.",
        "icone": "graduation-cap",
        "cor": "#2563EB",
        "ordem": 2,
    },
    {
        "slug": "alimentacao",
        "nome": "Alimentação",
        "descricao": "Segurança alimentar, combate à fome, balanço da desnutrição, programas de alimentação escolar e suplementar.",
        "icone": "utensils",
        "cor": "#F59E0B",
        "ordem": 3,
    },
    {
        "slug": "transporte",
        "nome": "Transporte",
        "descricao": "DNIT, ANTT, mobilidade urbana, fiscalização de obras, transporte público e qualidade das vias.",
        "icone": "bus",
        "cor": "#0EA5E9",
        "ordem": 4,
    },
    {
        "slug": "seguranca",
        "nome": "Segurança Pública",
        "descricao": "Polícias, sistema prisional, violência, câmeras de vigilância e gastos com segurança pública.",
        "icone": "shield",
        "cor": "#7C3AED",
        "ordem": 5,
    },
    {
        "slug": "saneamento",
        "nome": "Saneamento",
        "descricao": "ANA, água, esgoto, resíduos sólidos, qualidade da água e fiscalização de contratos de saneamento.",
        "icone": "droplet",
        "cor": "#06B6D4",
        "ordem": 6,
    },
    {
        "slug": "financas",
        "nome": "Finanças Públicas",
        "descricao": "Orçamento público, gastos governamentais, dívida pública, transferências e fiscalização tributária.",
        "icone": "dollar-sign",
        "cor": "#16A34A",
        "ordem": 7,
    },
    {
        "slug": "meio-ambiente",
        "nome": "Meio Ambiente",
        "descricao": "Desmatamento, queimadas, licenciamento ambiental, recursos hídricos, unidades de conservação e mudanças climáticas.",
        "icone": "leaf",
        "cor": "#22C55E",
        "ordem": 8,
    },
    {
        "slug": "cultura",
        "nome": "Cultura",
        "descricao": "Lei Rouanet, Lei Aldir Blanc, patrimônio histórico, diversidade cultural e acesso a bens culturais.",
        "icone": "book-open",
        "cor": "#EC4899",
        "ordem": 9,
    },
]


async def seed_areas(session: AsyncSession) -> int:
    """Cria as áreas temáticas iniciais se não existirem"""
    criadas = 0
    for area_data in AREAS_INICIAIS:
        result = await session.execute(
            select(Area).where(Area.slug == area_data["slug"])
        )
        existing = result.scalar_one_or_none()
        if not existing:
            area = Area(**area_data)
            session.add(area)
            criadas += 1
    await session.commit()
    return criadas


async def seed_admin(session: AsyncSession) -> Usuario | None:
    """Cria um usuário admin inicial se não existir nenhum admin"""
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    result = await session.execute(
        select(Usuario).where(Usuario.role == Role.ADMIN)
    )
    existing = result.scalar_one_or_none()
    if existing:
        return None

    admin = Usuario(
        id=uuid.uuid4(),
        email="admin@projetocidadao.org",
        nome="Admin",
        senha_hash=pwd_context.hash("changeme"),
        role=Role.ADMIN,
        pontos=0,
        consentimento_lgpd=True,
        data_consentimento=datetime.now(timezone.utc),
        apto_a_criar=True,
    )
    session.add(admin)
    await session.commit()
    return admin


async def main() -> None:
    print("🌱 Iniciando seed do banco de dados...")
    print(f"   DATABASE_URL: {settings.DATABASE_URL.split('@')[-1]}")  # esconde senha

    async with async_session() as session:
        print("📦 Criando áreas temáticas...")
        n_areas = await seed_areas(session)
        print(f"   ✅ {n_areas} áreas criadas")

        print("👤 Criando admin padrão...")
        admin = await seed_admin(session)
        if admin:
            print(f"   ✅ Admin criado: {admin.email}")
        else:
            print("   ⏭️  Admin já existe, pulando")

    print("🎉 Seed concluído!")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
