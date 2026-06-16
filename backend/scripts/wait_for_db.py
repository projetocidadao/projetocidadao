"""
Aguarda o banco de dados Postgres estar pronto antes de prosseguir.
Usado no entrypoint do Docker.
"""
import os
import sys
import time
from urllib.parse import urlparse

import psycopg2


def wait_for_db(url: str, max_attempts: int = 30, delay: int = 2) -> None:
    parsed = urlparse(url)
    dbname = parsed.path.lstrip("/")
    user = parsed.username
    password = parsed.password
    host = parsed.hostname
    port = parsed.port or 5432

    print(f"⏳ Aguardando {host}:{port}/{dbname}...")

    for attempt in range(1, max_attempts + 1):
        try:
            conn = psycopg2.connect(
                dbname=dbname,
                user=user,
                password=password,
                host=host,
                port=port,
                connect_timeout=3,
            )
            conn.close()
            print(f"✅ Banco de dados pronto (tentativa {attempt}/{max_attempts})")
            return
        except psycopg2.OperationalError as e:
            print(f"   [{attempt}/{max_attempts}] ainda não disponível: {e}")
            if attempt == max_attempts:
                print("❌ Timeout aguardando o banco de dados")
                sys.exit(1)
            time.sleep(delay)


if __name__ == "__main__":
    url = os.getenv(
        "DATABASE_URL_SYNC",
        "postgresql+psycopg2://projetocidadao:changeme@localhost:5432/projetocidadao",
    )
    wait_for_db(url)
