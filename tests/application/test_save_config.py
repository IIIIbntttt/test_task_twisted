from unittest.mock import MagicMock

import pytest

from config_service.application.dto.requests import SaveConfigRequest
from config_service.application.use_cases.save_config import SaveConfigUseCase
from config_service.domain.exceptions import DuplicateVersionError, ValidationError
from config_service.infrastructure.serialization.yaml_parser import parse_yaml
from tests.conftest import resolved

_VALID_YAML = """
version: 1
database:
  host: db.local
  port: 5432
"""

_YAML_NO_VERSION = """
database:
  host: db.local
  port: 5432
"""

_INVALID_YAML = "key: [unclosed"

_YAML_MISSING_DB = """
version: 1
features:
  flag: true
"""


def _make_use_case(repo: MagicMock) -> SaveConfigUseCase:
    return SaveConfigUseCase(repo, parse_yaml)


@pytest.inlineCallbacks  # type: ignore[misc]
def test_save_config_with_explicit_version() -> None:
    repo = MagicMock()
    repo.save.return_value = resolved(None)

    uc = _make_use_case(repo)
    result = yield uc.execute(
        SaveConfigRequest(service="svc", yaml_content=_VALID_YAML)
    )

    assert result.version == 1
    assert result.status == "saved"
    assert result.service == "svc"
    repo.get_next_version.assert_not_called()


@pytest.inlineCallbacks  # type: ignore[misc]
def test_save_config_auto_assigns_version() -> None:
    repo = MagicMock()
    repo.get_next_version.return_value = resolved(3)
    repo.save.return_value = resolved(None)

    uc = _make_use_case(repo)
    result = yield uc.execute(
        SaveConfigRequest(service="svc", yaml_content=_YAML_NO_VERSION)
    )

    assert result.version == 3
    repo.get_next_version.assert_called_once_with("svc")


@pytest.inlineCallbacks  # type: ignore[misc]
def test_invalid_yaml_raises_error() -> None:
    repo = MagicMock()
    uc = _make_use_case(repo)

    from config_service.domain.exceptions import InvalidYamlError

    with pytest.raises(InvalidYamlError):
        yield uc.execute(SaveConfigRequest(service="svc", yaml_content=_INVALID_YAML))


@pytest.inlineCallbacks  # type: ignore[misc]
def test_missing_required_fields_raises_validation_error() -> None:
    repo = MagicMock()
    uc = _make_use_case(repo)

    with pytest.raises(ValidationError) as exc_info:
        yield uc.execute(
            SaveConfigRequest(service="svc", yaml_content=_YAML_MISSING_DB)
        )

    assert exc_info.value.errors


@pytest.inlineCallbacks  # type: ignore[misc]
def test_duplicate_version_propagates() -> None:
    repo = MagicMock()
    repo.save.side_effect = DuplicateVersionError("already exists")

    uc = _make_use_case(repo)

    with pytest.raises(DuplicateVersionError):
        yield uc.execute(SaveConfigRequest(service="svc", yaml_content=_VALID_YAML))
