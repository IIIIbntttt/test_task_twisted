from twisted.internet import defer

from config_service.application.dto.requests import GetHistoryRequest
from config_service.application.dto.responses import GetHistoryResponse, HistoryItem
from config_service.domain.repositories.i_configuration_repository import (
    IConfigurationRepository,
)


class GetHistoryUseCase:
    def __init__(self, repository: IConfigurationRepository) -> None:
        self._repository = repository

    @defer.inlineCallbacks  # type: ignore[arg-type]
    def execute(  # type: ignore[misc]
        self, request: GetHistoryRequest
    ) -> defer.Deferred[GetHistoryResponse]:
        configs = yield self._repository.get_history(request.service)

        items = [
            HistoryItem(version=config.version, created_at=config.created_at)
            for config in configs
        ]
        return GetHistoryResponse(items=items)
