import yaml

from config_service.domain.exceptions import InvalidYamlError


def parse_yaml(content: str) -> dict[str, object]:
    """Парсит YAML-строку в словарь. Бросает InvalidYamlError при невалидном вводе."""
    try:
        result = yaml.safe_load(content)
    except yaml.YAMLError as exc:
        raise InvalidYamlError(f"Invalid YAML: {exc}") from exc

    if not isinstance(result, dict):
        raise InvalidYamlError("YAML must be a mapping at the top level")

    return result  # type: ignore[return-value]
