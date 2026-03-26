import json
import os

import psycopg2.extras
from twisted.enterprise import adbapi


def _setup_connection(conn: object) -> None:
    """Регистрирует кодек JSON/JSONB, чтобы колонки payload возвращались как dict."""
    psycopg2.extras.register_default_jsonb(conn, loads=json.loads)  # type: ignore[arg-type]


def create_connection_pool() -> adbapi.ConnectionPool:
    return adbapi.ConnectionPool(
        "psycopg2",
        host=os.environ.get("DB_HOST", "localhost"),
        port=int(os.environ.get("DB_PORT", "5432")),
        dbname=os.environ.get("DB_NAME", "configs"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASSWORD", "postgres"),
        cp_reconnect=True,
        cp_min=1,
        cp_max=5,
        cp_openfun=_setup_connection,
    )
