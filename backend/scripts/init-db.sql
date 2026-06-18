-- =============================================================================
-- Projeto Cidadão — Inicialização do banco
-- =============================================================================
-- Rodado automaticamente na primeira inicialização do Postgres
-- =============================================================================

-- Extensões necessárias
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS btree_gin;
CREATE EXTENSION IF NOT EXISTS btree_gist;

-- Fuso horário
ALTER DATABASE projetocidadao SET timezone = 'America/Sao_Paulo';

-- Mensagem de log
DO $$
BEGIN
    RAISE NOTICE 'Projeto Cidadão — extensões criadas: postgis, uuid-ossp, pg_trgm';
END
$$;
