"""
Configurações da aplicação via variáveis de ambiente
"""
from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # App
    APP_NAME: str = "Projeto Cidadão API"
    APP_VERSION: str = "0.1.0"
    APP_ENV: str = Field(default="development")
    DEBUG: bool = Field(default=True)

    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://projetocidadao:changeme@localhost:5432/projetocidadao"
    )
    DATABASE_URL_SYNC: str = Field(
        default="postgresql+psycopg2://projetocidadao:changeme@localhost:5432/projetocidadao"
    )
    DB_ECHO: bool = Field(default=False)
    DB_POOL_SIZE: int = Field(default=10)
    DB_MAX_OVERFLOW: int = Field(default=20)

    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0")

    # Auth
    JWT_SECRET: str = Field(default="changeme-in-production")
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_EXPIRES_MINUTES: int = Field(default=60 * 24 * 7)  # 7 dias

    # CORS
    CORS_ORIGINS: list[str] = Field(default=["*"])

    # LGPD
    LGPD_ENABLED: bool = Field(default=True)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
