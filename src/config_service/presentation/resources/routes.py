"""Регистрация маршрутов на существующем Klein-приложении."""

from functools import partial

from klein import Klein

from config_service.presentation.handlers.config_handlers import (
    get_config,
    get_history,
    post_config,
)
from config_service.presentation.resources.config_resource import ConfigResource


def setup_routes(app: Klein, resource: ConfigResource) -> Klein:
    """Регистрирует все маршруты на переданном приложении. Само приложение не создаёт."""
    app.route("/config/<string:service>", methods=["POST"])(
        partial(post_config, resource.save_uc)
    )
    app.route("/config/<string:service>", methods=["GET"])(
        partial(get_config, resource.get_uc)
    )
    app.route("/config/<string:service>/history", methods=["GET"])(
        partial(get_history, resource.history_uc)
    )

    return app
