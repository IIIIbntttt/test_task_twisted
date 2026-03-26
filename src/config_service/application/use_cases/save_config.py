from twisted.internet import defer

from config_service.application.dto.requests import SaveConfigRequest
from config_service.application.dto.responses import SaveConfigResponse
from config_service.domain.entities.configuration import Configuration
from config_service.domain.exceptions import ValidationError
from config_service.domain.repositories.i_configuration_repository import (
    IConfigurationRepository,
)
from config_service.domain.services.configuration_domain_service import validate_payload
from config_service.infrastructure.serialization.yaml_parser import YamlParser


class SaveConfigUseCase:
    def __init__(
        self,
        repository: IConfigurationRepository,
        yaml_parser: YamlParser,
    ) -> None:
        self._repository = repository
        self._yaml_parser = yaml_parser

    @defer.inlineCallbacks
    def execute(self, request: SaveConfigRequest) -> defer.Deferred:
        payload = self._yaml_parser.parse(request.yaml_content)

        errors = validate_payload(payload)
        if errors:
            raise ValidationError(errors)

        if "version" not in payload:
            next_version = yield self._repository.get_next_version(request.service)
            payload["version"] = next_version

        version = int(payload["version"])  # type: ignore[arg-type]

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
