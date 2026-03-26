from twisted.internet import defer

from config_service.application.dto.requests import GetConfigRequest
from config_service.application.dto.responses import GetConfigResponse
from config_service.domain.repositories.i_configuration_repository import (
    IConfigurationRepository,
)
from config_service.infrastructure.templating.jinja_processor import JinjaProcessor


class GetConfigUseCase:
    def __init__(
        self,
        repository: IConfigurationRepository,
        jinja_processor: JinjaProcessor,
    ) -> None:
        self._repository = repository
        self._jinja_processor = jinja_processor

    @defer.inlineCallbacks
    def execute(self, request: GetConfigRequest) -> defer.Deferred:
        if request.version is not None:
            config = yield self._repository.get_by_version(
                request.service, request.version
            )
        else:
            config = yield self._repository.get_latest(request.service)

        payload = config.payload

        if request.use_template:
            payload = self._jinja_processor.render(payload, request.template_context)

        return GetConfigResponse(payload=payload)
