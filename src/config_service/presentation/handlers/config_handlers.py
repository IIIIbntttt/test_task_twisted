"""Standalone-хендлеры для HTTP-эндпоинтов.

Каждая функция получает нужный use case через functools.partial.
"""

import orjson
from twisted.internet import defer
from twisted.web.http import Request

from config_service.application.dto.requests import (
    GetConfigRequest,
    GetHistoryRequest,
    SaveConfigRequest,
)
from config_service.application.use_cases.get_config import GetConfigUseCase
from config_service.application.use_cases.get_history import GetHistoryUseCase
from config_service.application.use_cases.save_config import SaveConfigUseCase
from config_service.domain.exceptions import (
    ConfigurationNotFoundError,
    DuplicateVersionError,
    InvalidYamlError,
    ValidationError,
)
from config_service.presentation.utils.request_utils import parse_template_context


def _json(request: Request, status: int, data: object) -> bytes:
    """Формирует JSON-ответ с нужным статус-кодом."""
    request.setResponseCode(status)
    request.setHeader(b"Content-Type", b"application/json")
    return orjson.dumps(data)


@defer.inlineCallbacks
def create_config(
    save_uc: SaveConfigUseCase, request: Request, service: str
) -> defer.Deferred[bytes]:
    """Сохраняет новую конфигурацию для сервиса."""
    assert request.content is not None
    try:
        body = request.content.read().decode("utf-8")
    except UnicodeDecodeError:
        return _json(request, 400, {"error": "Request body must be UTF-8 encoded"})

    try:
        result = yield save_uc.execute(
            SaveConfigRequest(service=service, yaml_content=body)
        )
        return _json(request, 200, result.to_dict())
    except InvalidYamlError as exc:
        return _json(request, 400, {"error": str(exc)})
    except ValidationError as exc:
        return _json(request, 422, {"errors": exc.errors})
    except DuplicateVersionError as exc:
        return _json(request, 409, {"error": str(exc)})
    except Exception:
        return _json(request, 500, {"error": "Internal server error"})


@defer.inlineCallbacks
def get_config(
    get_uc: GetConfigUseCase, request: Request, service: str
) -> defer.Deferred[bytes]:
    """Возвращает конфигурацию сервиса. Поддерживает выбор версии и Jinja2-рендеринг."""
    args = request.args or {}
    version_raw = args.get(b"version", [None])[0]
    if version_raw is not None:
        try:
            version: int | None = int(version_raw)
        except ValueError:
            return _json(request, 400, {"error": "version must be an integer"})
    else:
        version = None

    use_template = args.get(b"template", [b"0"])[0] == b"1"

    try:
        result = yield get_uc.execute(
            GetConfigRequest(
                service=service,
                version=version,
                use_template=use_template,
                template_context=parse_template_context(request),
            )
        )
        return _json(request, 200, result.payload)
    except ConfigurationNotFoundError as exc:
        return _json(request, 404, {"error": str(exc)})
    except Exception:
        return _json(request, 500, {"error": "Internal server error"})


@defer.inlineCallbacks
def get_history(
    history_uc: GetHistoryUseCase, request: Request, service: str
) -> defer.Deferred[bytes]:
    """Возвращает историю версий конфигурации для сервиса."""
    try:
        result = yield history_uc.execute(GetHistoryRequest(service=service))
        return _json(request, 200, [item.to_dict() for item in result.items])
    except ConfigurationNotFoundError as exc:
        return _json(request, 404, {"error": str(exc)})
    except Exception:
        return _json(request, 500, {"error": "Internal server error"})
