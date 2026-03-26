"""Утилиты для разбора HTTP-запросов Twisted."""

from twisted.web.http import Request

RESERVED_PARAMS = frozenset([b"version", b"template"])


def parse_template_context(request: Request) -> dict[str, str]:
    """Извлекает query-параметры запроса как контекст для Jinja2-шаблонов.

    Параметры version и template считаются служебными и исключаются.
    """
    return {
        key.decode(): values[0].decode()
        for key, values in (request.args or {}).items()
        if key not in RESERVED_PARAMS
    }
