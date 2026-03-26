"""Standalone-хендлеры для HTTP-эндпоинтов. Каждая функция получает нужный use case через functools.partial."""

import json

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


def _json(request: Request, status: int, data: object) -> bytes:
    """Формирует JSON-ответ с нужным статус-кодом."""
    request.setResponseCode(status)
    request.setHeader(b"Content-Type", b"application/json")
    return json.dumps(data).encode()


@defer.inlineCallbacks
def post_config(save_uc: SaveConfigUseCase, request: Request, service: str) -> defer.Deferred[bytes]:
    """Сохраняет новую конфигурацию для сервиса."""
    body = request.content.read().decode("utf-8")
    try:
        result = yield save_uc.execute(
            SaveConfigRequest(service=service, yaml_content=body)
        )
        return _json(request, 200, {
            "service": result.service,
            "version": result.version,
            "status": result.status,
        })
    except InvalidYamlError as exc:
        return _json(request, 400, {"error": str(exc)})
    except ValidationError as exc:
        return _json(request, 422, {"errors": exc.errors})
    except DuplicateVersionError as exc:
        return _json(request, 409, {"error": str(exc)})


@defer.inlineCallbacks
def get_config(get_uc: GetConfigUseCase, request: Request, service: str) -> defer.Deferred[bytes]:
    """Возвращает конфигурацию сервиса. Поддерживает выбор версии и Jinja2-рендеринг."""
    version_raw = request.args.get(b"version", [None])[0]
    version = int(version_raw) if version_raw is not None else None

    use_template = request.args.get(b"template", [b"0"])[0] == b"1"

    context: dict[str, str] = {}
    if use_template:
        for key, values in request.args.items():
            if key not in (b"version", b"template"):
                context[key.decode()] = values[0].decode()

    try:
        result = yield get_uc.execute(
            GetConfigRequest(
                service=service,
                version=version,
                use_template=use_template,
                template_context=context,
            )
        )
        return _json(request, 200, result.payload)
    except ConfigurationNotFoundError as exc:
        return _json(request, 404, {"error": str(exc)})


@defer.inlineCallbacks
def get_history(history_uc: GetHistoryUseCase, request: Request, service: str) -> defer.Deferred[bytes]:
    """Возвращает историю версий конфигурации для сервиса."""
    try:
        result = yield history_uc.execute(GetHistoryRequest(service=service))
        items = [
            {
                "version": item.version,
                "created_at": item.created_at.isoformat(),
            }
            for item in result.items
        ]
        return _json(request, 200, items)
    except ConfigurationNotFoundError as exc:
        return _json(request, 404, {"error": str(exc)})
