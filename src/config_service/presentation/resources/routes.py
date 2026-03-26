"""Регистрация маршрутов на существующем Klein-приложении."""

from functools import partial, update_wrapper
from typing import Any, Callable

from klein import Klein

from config_service.presentation.handlers.config_handlers import (
    create_config,
    get_config,
    get_history,
)
from config_service.presentation.resources.config_resource import ConfigResource


def _bind(func: Callable[..., Any], *args: Any) -> Callable[..., Any]:
    """Создаёт partial с сохранённым __name__.

    Klein требует __name__ при регистрации маршрута.
    """
    p = partial(func, *args)
    update_wrapper(p, func)
    return p


def setup_routes(app: Klein, resource: ConfigResource) -> Klein:
    """Регистрирует все маршруты на переданном приложении.

    Само приложение не создаёт.
    """
    app.route("/config/<string:service>", methods=["POST"])(
        _bind(create_config, resource.save_uc)
    )
    app.route("/config/<string:service>", methods=["GET"])(
        _bind(get_config, resource.get_uc)
    )
    app.route("/config/<string:service>/history", methods=["GET"])(
        _bind(get_history, resource.history_uc)
    )

    return app
