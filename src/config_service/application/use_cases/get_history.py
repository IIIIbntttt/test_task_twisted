from twisted.internet import defer

from config_service.application.dto.requests import GetHistoryRequest
from config_service.application.dto.responses import GetHistoryResponse, HistoryItem
from config_service.domain.repositories.i_configuration_repository import (
    IConfigurationRepository,
)


class GetHistoryUseCase:
    def __init__(self, repository: IConfigurationRepository) -> None:
        self._repository = repository

    @defer.inlineCallbacks
    def execute(self, request: GetHistoryRequest) -> defer.Deferred:
        configs = yield self._repository.get_history(request.service)

        items = [
            HistoryItem(version=c.version, created_at=c.created_at)  # type: ignore[arg-type]
            for c in configs
        ]
        return GetHistoryResponse(items=items)
