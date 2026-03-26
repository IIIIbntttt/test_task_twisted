import json

import psycopg2
from twisted.enterprise import adbapi
from twisted.internet import defer

from config_service.domain.entities.configuration import Configuration
from config_service.domain.exceptions import (
    ConfigurationNotFoundError,
    DuplicateVersionError,
)
from config_service.domain.repositories.i_configuration_repository import (
    IConfigurationRepository,
)


def _row_to_configuration(row: tuple) -> Configuration:  # type: ignore[type-arg]
    payload = row[3]
    if isinstance(payload, str):
        payload = json.loads(payload)
    return Configuration(
        id=row[0],
        service=row[1],
        version=row[2],
        payload=payload,
        created_at=row[4],
    )


class PgConfigurationRepository(IConfigurationRepository):
    def __init__(self, pool: adbapi.ConnectionPool) -> None:
        self._pool = pool

    @defer.inlineCallbacks
    def save(self, config: Configuration) -> defer.Deferred:
        try:
            yield self._pool.runOperation(
                """
                INSERT INTO configurations (service, version, payload)
                VALUES (%s, %s, %s::jsonb)
                """,
                (config.service, config.version, json.dumps(config.payload)),
            )
        except psycopg2.IntegrityError:
            raise DuplicateVersionError(
                f"Version {config.version} already exists"
                f" for service '{config.service}'"
            )

    @defer.inlineCallbacks
    def get_latest(self, service: str) -> defer.Deferred:
        rows = yield self._pool.runQuery(
            """
            SELECT id, service, version, payload, created_at
            FROM configurations
            WHERE service = %s
            ORDER BY version DESC
            LIMIT 1
            """,
            (service,),
        )
        if not rows:
            raise ConfigurationNotFoundError(f"Service '{service}' not found")
        return _row_to_configuration(rows[0])

    @defer.inlineCallbacks
    def get_by_version(self, service: str, version: int) -> defer.Deferred:
        rows = yield self._pool.runQuery(
            """
            SELECT id, service, version, payload, created_at
            FROM configurations
            WHERE service = %s AND version = %s
            """,
            (service, version),
        )
        if not rows:
            raise ConfigurationNotFoundError(
                f"Version {version} of service '{service}' not found"
            )
        return _row_to_configuration(rows[0])

    @defer.inlineCallbacks
    def get_next_version(self, service: str) -> defer.Deferred:
        rows = yield self._pool.runQuery(
            "SELECT COALESCE(MAX(version), 0) + 1"
            " FROM configurations WHERE service = %s",
            (service,),
        )
        return int(rows[0][0])

    @defer.inlineCallbacks
    def get_history(self, service: str) -> defer.Deferred:
        rows = yield self._pool.runQuery(
            """
            SELECT id, service, version, NULL AS payload, created_at
            FROM configurations
            WHERE service = %s
            ORDER BY version ASC
            """,
            (service,),
        )
        if not rows:
            raise ConfigurationNotFoundError(f"Service '{service}' not found")
        return [
            Configuration(
                id=row[0],
                service=row[1],
                version=row[2],
                payload={},
                created_at=row[4],
            )
            for row in rows
        ]
