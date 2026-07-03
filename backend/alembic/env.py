"""Configuração do Alembic."""
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

from src.db.config import settings
from src.db.base import Base
import src.models  # noqa: F401  (registra todos os models na Base.metadata)

config = context.config

# Sobrescreve a URL do banco com a do settings
config.set_main_option("sqlalchemy.url", settings.database_url_sync)

# Configuração de log
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


# === FILTRO POSTGIS (adicionado em 2026-07-03) ===
# Tabelas do PostGIS TIGER geocoder devem ser ignoradas pelo Alembic
POSTGIS_TABLES = [
    'layer', 'topology', 'edges', 'addrfeat', 'state_lookup',
    'zip_lookup', 'zip_lookup_all', 'zcta5', 'zcta510',
    'geocode_settings', 'geocode_settings_default', 'pagc_gaz',
    'pagc_lex', 'pagc_rules', 'place_lookup', 'secondary_unit_lookup',
    'street_type_lookup', 'countysub_lookup', 'county_lookup',
    'direction_lookup', 'state', 'featnames', 'faces',
    'place', 'cousub', 'county', 'bg', 'tract',
    'tabblock', 'tabblock20', 'loader_variables', 'loader_platform',
    'loader_lookuptables', 'spatial_ref_sys', 'addr',
    'zip_state', 'zip_state_loc', 'zip_lookup_base',
]


def include_object(object, name, type_, reflected, compare_to):
    """Ignorar tabelas do PostGIS TIGER geocoder durante autogenerate."""
    if type_ == 'table' and name in POSTGIS_TABLES:
        return False
    if type_ == 'index':
        tbl = getattr(object, 'table', None)
        if tbl is not None and tbl.name in POSTGIS_TABLES:
            return False
    if type_ == 'column':
        tbl = getattr(object, 'table', None)
        if tbl is not None and tbl.name in POSTGIS_TABLES:
            return False
    return True
# === FIM FILTRO POSTGIS ===


def run_migrations_offline() -> None:
    """Roda migrations em modo 'offline' (gera SQL sem conectar)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        include_object=include_object,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Roda migrations em modo 'online' (conectando ao banco)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            include_object=include_object,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
