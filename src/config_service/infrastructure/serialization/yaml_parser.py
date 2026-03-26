import yaml

from config_service.domain.exceptions import InvalidYamlError


class YamlParser:
    def parse(self, content: str) -> dict[str, object]:
        try:
            result = yaml.safe_load(content)
        except yaml.YAMLError as exc:
            raise InvalidYamlError(f"Invalid YAML: {exc}") from exc

        if not isinstance(result, dict):
            raise InvalidYamlError("YAML must be a mapping at the top level")

        return result  # type: ignore[return-value]
