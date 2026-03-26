"""Доменные правила валидации конфигурации."""

# Поля, которые обязаны присутствовать в каждой загружаемой конфигурации.
# Задаются кортежами вложенных ключей: ("database", "host") означает payload["database"]["host"].
REQUIRED_FIELDS: list[tuple[str, ...]] = [
    ("database", "host"),
    ("database", "port"),
]


def validate_payload(payload: dict[str, object]) -> list[str]:
    """Вернуть список сообщений об ошибках валидации (пустой список — конфигурация валидна)."""
    errors: list[str] = []
    for path in REQUIRED_FIELDS:
        node: object = payload
        for key in path:
            if not isinstance(node, dict) or key not in node:
                errors.append(f"Missing required field: {'.'.join(path)}")
                break
            node = node[key]
    return errors
