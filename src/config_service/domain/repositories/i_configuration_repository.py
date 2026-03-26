from abc import ABC, abstractmethod

from twisted.internet.defer import Deferred

from config_service.domain.entities.configuration import Configuration


class IConfigurationRepository(ABC):
    @abstractmethod
    def save(self, config: Configuration) -> Deferred[None]:
        """Сохранить новую версию конфигурации.

        Бросает DuplicateVersionError если версия уже существует.
        """

    @abstractmethod
    def get_latest(self, service: str) -> Deferred[Configuration]:
        """Вернуть последнюю Configuration для сервиса.

        Бросает ConfigurationNotFoundError.
        """

    @abstractmethod
    def get_by_version(self, service: str, version: int) -> Deferred[Configuration]:
        """Вернуть конкретную версию. Бросает ConfigurationNotFoundError."""

    @abstractmethod
    def get_next_version(self, service: str) -> Deferred[int]:
        """Вернуть max(version)+1 для сервиса (1 если версий ещё нет)."""

    @abstractmethod
    def get_history(self, service: str) -> Deferred[list[Configuration]]:
        """Вернуть список Configuration (без payload), отсортированный по version asc.

        Бросает ConfigurationNotFoundError если конфигураций для сервиса не существует.
        """
