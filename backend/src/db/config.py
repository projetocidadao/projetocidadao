"""
Configurações carregadas de variáveis de ambiente.
"""
from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    database_url: str = "postgresql+asyncpg://projetocidadao:changeme@localhost:5432/projetocidadao"
    database_url_sync: str = "postgresql+psycopg2://projetocidadao:changeme@localhost:5432/projetocidadao"
    redis_url: str = "redis://localhost:6379/0"

    jwt_secret: str = "changeme-super-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_expires_minutes: int = 60 * 24 * 7

    app_env: str = "development"
    app_debug: bool = True
    app_port: int = 8000
    app_cors_origins: List[str] = ["*"]

    s3_endpoint: str = ""
    s3_access_key: str = ""
    s3_secret_key: str = ""
    s3_bucket: str = "projetocidadao"
    s3_region: str = "us-east-1"

    telegram_bot_token: str = ""

    farejador_scheduler_enabled: bool = True
    farejador_cron: str = "0 */6 * * *"
    farejador_timezone: str = "America/Sao_Paulo"
    farejador_min_score: int = 30


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
