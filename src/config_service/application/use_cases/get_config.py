from collections.abc import Callable

from twisted.internet import defer

from config_service.application.dto.requests import GetConfigRequest
from config_service.application.dto.responses import GetConfigResponse
from config_service.domain.repositories.i_configuration_repository import (
    IConfigurationRepository,
)


class GetConfigUseCase:
    def __init__(
        self,
        repository: IConfigurationRepository,
        jinja_renderer: Callable[
            [dict[str, object], dict[str, str]], dict[str, object]
        ],
    ) -> None:
        self._repository = repository
        self._jinja_renderer = jinja_renderer

    @defer.inlineCallbacks  # type: ignore[arg-type]
    def execute(  # type: ignore[misc]
        self, request: GetConfigRequest
    ) -> defer.Deferred[GetConfigResponse]:
        if request.version is not None:
            config = yield self._repository.get_by_version(
                request.service, request.version
            )
        else:
            config = yield self._repository.get_latest(request.service)

        payload = config.payload

        if request.use_template:
            payload = self._jinja_renderer(payload, request.template_context)

        return GetConfigResponse(payload=payload)
