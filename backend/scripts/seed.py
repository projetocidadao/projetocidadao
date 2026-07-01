"""
Script de seed — popula o banco com áreas temáticas iniciais e usuário admin.

Uso: poetry run python scripts/seed.py
"""
import asyncio
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import AsyncSessionLocal
from src.models.area import Area
from src.models.usuario import Usuario, UserRole


AREAS_INICIAIS = [
    {
        "slug": "saude",
        "nome": "Saúde",
        "descricao": "Acompanhamento de gastos, fiscalização do SUS, listas de espera, qualidade do atendimento e uso de recursos públicos na saúde.",
        "icone": "🏥",
        "cor": "#EF4444",
        "artigo_cf": "Art. 6º, 196-200",
        "ordem": 1,
    },
    {
        "slug": "educacao",
        "nome": "Educação",
        "descricao": "Verificação de verbas do FUNDEB, IDEB, merenda escolar, qualidade do ensino e infraestrutura das escolas públicas.",
        "icone": "📚",
        "cor": "#3B82F6",
        "artigo_cf": "Art. 6º, 205-214",
        "ordem": 2,
    },
    {
        "slug": "alimentacao",
        "nome": "Alimentação",
        "descricao": "Combate à fome, merenda escolar, restaurantes populares, programas de segurança alimentar e balanço da desnutrição.",
        "icone": "🍽️",
        "cor": "#F59E0B",
        "artigo_cf": "Art. 6º, 227 §3º",
        "ordem": 3,
    },
    {
        "slug": "transporte",
        "nome": "Transporte",
        "descricao": "Fiscalização de rodovias, transporte público, gratuidade para idosos, obras de mobilidade e segurança viária.",
        "icone": "🚌",
        "cor": "#10B981",
        "artigo_cf": "Art. 6º, 21, 178",
        "ordem": 4,
    },
    {
        "slug": "seguranca",
        "nome": "Segurança Pública",
        "descricao": "Polícia, índices de criminalidade, câmeras de segurança, gastos com segurança pública e proteção de dados.",
        "icone": "🛡️",
        "cor": "#8B5CF6",
        "artigo_cf": "Art. 6º, 144",
        "ordem": 5,
    },
    {
        "slug": "saneamento",
        "nome": "Saneamento",
        "descricao": "Água potável, esgoto sanitário, coleta de lixo, tratamento de resíduos e qualidade dos serviços.",
        "icone": "💧",
        "cor": "#06B6D4",
        "artigo_cf": "Art. 6º, 21 XX, 23 IX",
        "ordem": 6,
    },
    {
        "slug": "financas",
        "nome": "Finanças Públicas",
        "descricao": "Gastos do governo, licitações, contratos, concursos, folha de pagamento e destinação do orçamento público.",
        "icone": "💰",
        "cor": "#FACC15",
        "artigo_cf": "Art. 163-169",
        "ordem": 7,
    },
    {
        "slug": "meio-ambiente",
        "nome": "Meio Ambiente",
        "descricao": "Desmatamento, queimadas, licenciamento ambiental, recursos hídricos, mudanças climáticas e áreas protegidas.",
        "icone": "🌳",
        "cor": "#22C55E",
        "artigo_cf": "Art. 225",
        "ordem": 8,
    },
    {
        "slug": "cultura",
        "nome": "Cultura",
        "descricao": "Lei Aldir Blanc, Lei Rouanet, patrimônio histórico, diversidade cultural, bibliotecas e espaços públicos.",
        "icone": "🎭",
        "cor": "#EC4899",
        "artigo_cf": "Art. 215-216",
        "ordem": 9,
    },
]


async def seed_areas(session: AsyncSession) -> int:
    """Cria áreas temáticas iniciais se não existirem."""
    count = 0
    for dados in AREAS_INICIAIS:
        result = await session.execute(select(Area).where(Area.slug == dados["slug"]))
        if not result.scalar_one_or_none():
            area = Area(**dados)
            session.add(area)
            count += 1
    await session.commit()
    return count


async def seed_admin(session: AsyncSession) -> bool:
    """Cria usuário admin inicial se não existir."""
    from passlib.hash import bcrypt
    admin_email = "admin@projetocidadao.org"
    result = await session.execute(select(Usuario).where(Usuario.email == admin_email))
    if result.scalar_one_or_none():
        return False
    admin = Usuario(
        email=admin_email,
        nome="Admin",
        senha_hash=bcrypt.hash("projeto2024"),  # trocar em produção!
        role=UserRole.ADMIN,
        pontos=0,
        nivel=10,
        verificado=True,
    )
    session.add(admin)
    await session.commit()
    return True


async def main():
    print("🌱 Iniciando seed do banco...")
    async with AsyncSessionLocal() as session:
        areas = await seed_areas(session)
        admin = await seed_admin(session)
        print(f"✅ {areas} áreas criadas")
        if admin:
            print("✅ Admin criado: admin@projetocidadao.org / projeto2024")
        else:
            print("⏭️  Admin já existe")
    print("🎉 Seed concluído!")


if __name__ == "__main__":
    asyncio.run(main())
