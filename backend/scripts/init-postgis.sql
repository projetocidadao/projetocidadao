-- =============================================================================
-- Script de inicialização do PostGIS (executado automaticamente pelo container)
-- Garante que as extensões de geolocalização e busca textual estejam ativas.
-- =============================================================================

-- Extensão de geolocalização (usada para denúncias com lat/lng)
CREATE EXTENSION IF NOT EXISTS postgis;

-- Extensão de busca textual trigrama (busca fuzzy em títulos/descrições)
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Extensão para gerar UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- (Opcional) Mostra versão
SELECT 'PostGIS initialized: ' || postgis_version() AS info;
