from collections.abc import Callable

from twisted.internet import defer

from config_service.application.dto.requests import SaveConfigRequest
from config_service.application.dto.responses import SaveConfigResponse
from config_service.domain.entities.configuration import Configuration
from config_service.domain.exceptions import ValidationError
from config_service.domain.repositories.i_configuration_repository import (
    IConfigurationRepository,
)
from config_service.domain.services.configuration_domain_service import validate_payload


class SaveConfigUseCase:
    def __init__(
        self,
        repository: IConfigurationRepository,
        yaml_parser: Callable[[str], dict[str, object]],
    ) -> None:
        self._repository = repository
        self._yaml_parser = yaml_parser

    @defer.inlineCallbacks  # type: ignore[arg-type]
    def execute(  # type: ignore[misc]
        self, request: SaveConfigRequest
    ) -> defer.Deferred[SaveConfigResponse]:
        payload = self._yaml_parser(request.yaml_content)

        errors = validate_payload(payload)
        if errors:
            raise ValidationError(errors)

        if "version" not in payload:
            next_version = yield self._repository.get_next_version(request.service)
            payload["version"] = next_version

        version = int(str(payload["version"]))

        config = Configuration(
            service=request.service,
            version=version,
            payload=payload,
        )
        yield self._repository.save(config)

        return SaveConfigResponse(
            service=request.service,
            version=version,
            status="saved",
        )
