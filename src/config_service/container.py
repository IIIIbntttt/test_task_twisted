"""Декларативный DI-контейнер. Граф зависимостей описан явно, pool передаётся снаружи."""

from dependency_injector import containers, providers
from klein import Klein
from twisted.enterprise import adbapi

from config_service.application.use_cases.get_config import GetConfigUseCase
from config_service.application.use_cases.get_history import GetHistoryUseCase
from config_service.application.use_cases.save_config import SaveConfigUseCase
from config_service.infrastructure.database.pg_configuration_repository import (
    PgConfigurationRepository,
)
from config_service.infrastructure.serialization.yaml_parser import YamlParser
from config_service.infrastructure.templating.jinja_processor import JinjaProcessor
from config_service.presentation.resources.config_resource import ConfigResource
from config_service.presentation.resources.routes import setup_routes


class AppContainer(containers.DeclarativeContainer):
    # Внешняя зависимость — передаётся через override при старте
    pool = providers.Dependency(instance_of=adbapi.ConnectionPool)

    # Инфраструктура
    repository = providers.Singleton(PgConfigurationRepository, pool=pool)
    yaml_parser = providers.Singleton(YamlParser)
    jinja_processor = providers.Singleton(JinjaProcessor)

    # Use cases
    save_uc = providers.Singleton(
        SaveConfigUseCase,
        repository=repository,
        yaml_parser=yaml_parser,
    )
    get_uc = providers.Singleton(
        GetConfigUseCase,
        repository=repository,
        jinja_processor=jinja_processor,
    )
    history_uc = providers.Singleton(
        GetHistoryUseCase,
        repository=repository,
    )

    # Presentation
    app = providers.Singleton(Klein)
    resource = providers.Singleton(
        ConfigResource,
        save_uc=save_uc,
        get_uc=get_uc,
        history_uc=history_uc,
    )
    app_with_routes = providers.Singleton(setup_routes, app=app, resource=resource)


def build(pool: adbapi.ConnectionPool) -> Klein:
    container = AppContainer()
    container.pool.override(providers.Object(pool))
    return container.app_with_routes()
