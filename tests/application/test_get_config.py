from datetime import datetime
from unittest.mock import MagicMock

import pytest

from config_service.application.dto.requests import GetConfigRequest, GetHistoryRequest
from config_service.application.use_cases.get_config import GetConfigUseCase
from config_service.application.use_cases.get_history import GetHistoryUseCase
from config_service.domain.entities.configuration import Configuration
from config_service.domain.exceptions import ConfigurationNotFoundError
from config_service.infrastructure.templating.jinja_processor import JinjaProcessor
from tests.conftest import resolved

_PAYLOAD = {
    "version": 2,
    "database": {"host": "db.local", "port": 5432},
}

_TEMPLATE_PAYLOAD = {
    "version": 2,
    "welcome_message": "Hello {{ user }}!",
}

_TS = datetime(2025, 8, 19, 12, 0, 0)


def _config(payload: dict = _PAYLOAD) -> Configuration:  # type: ignore[type-arg]
    return Configuration(service="svc", version=2, payload=payload, created_at=_TS)


def _make_get_uc(repo: MagicMock) -> GetConfigUseCase:
    return GetConfigUseCase(repo, JinjaProcessor())


# --- GetConfigUseCase ---


@pytest.inlineCallbacks  # type: ignore[misc]
def test_get_latest_config() -> None:
    repo = MagicMock()
    repo.get_latest.return_value = resolved(_config())

    uc = _make_get_uc(repo)
    result = yield uc.execute(GetConfigRequest(service="svc"))

    assert result.payload == _PAYLOAD
    repo.get_latest.assert_called_once_with("svc")


@pytest.inlineCallbacks  # type: ignore[misc]
def test_get_config_by_version() -> None:
    repo = MagicMock()
    repo.get_by_version.return_value = resolved(_config())

    uc = _make_get_uc(repo)
    result = yield uc.execute(GetConfigRequest(service="svc", version=2))

    assert result.payload["version"] == 2
    repo.get_by_version.assert_called_once_with("svc", 2)


@pytest.inlineCallbacks  # type: ignore[misc]
def test_template_rendering() -> None:
    repo = MagicMock()
    repo.get_latest.return_value = resolved(_config(_TEMPLATE_PAYLOAD))

    uc = _make_get_uc(repo)
    result = yield uc.execute(
        GetConfigRequest(service="svc", use_template=True, template_context={"user": "Alice"})
    )

    assert result.payload["welcome_message"] == "Hello Alice!"


@pytest.inlineCallbacks  # type: ignore[misc]
def test_not_found_propagates() -> None:
    repo = MagicMock()
    repo.get_latest.side_effect = ConfigurationNotFoundError("not found")

    uc = _make_get_uc(repo)

    with pytest.raises(ConfigurationNotFoundError):
        yield uc.execute(GetConfigRequest(service="missing"))


# --- GetHistoryUseCase ---


@pytest.inlineCallbacks  # type: ignore[misc]
def test_get_history_returns_items() -> None:
    configs = [
        Configuration(service="svc", version=1, payload={}, created_at=_TS),
        Configuration(service="svc", version=2, payload={}, created_at=_TS),
    ]
    repo = MagicMock()
    repo.get_history.return_value = resolved(configs)

    uc = GetHistoryUseCase(repo)
    result = yield uc.execute(GetHistoryRequest(service="svc"))

    assert len(result.items) == 2
    assert result.items[0].version == 1
    assert result.items[1].version == 2
