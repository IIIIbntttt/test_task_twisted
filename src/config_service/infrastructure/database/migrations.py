from twisted.enterprise import adbapi
from twisted.internet.defer import Deferred

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS configurations (
    id         SERIAL PRIMARY KEY,
    service    TEXT    NOT NULL,
    version    INTEGER NOT NULL,
    payload    JSONB   NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (service, version)
);
"""


def run_migrations(pool: adbapi.ConnectionPool) -> Deferred:
    return pool.runOperation(_CREATE_TABLE)  # type: ignore[return-value]
