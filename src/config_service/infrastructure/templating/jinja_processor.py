from jinja2 import Template


def render_jinja(
    payload: dict[str, object],
    context: dict[str, str],
) -> dict[str, object]:
    """Рекурсивно рендерит Jinja2-шаблоны в строковых значениях payload."""
    return _render_node(payload, context)  # type: ignore[return-value]


def _render_node(node: object, context: dict[str, str]) -> object:
    if isinstance(node, str):
        return Template(node).render(**context)
    if isinstance(node, dict):
        return {k: _render_node(v, context) for k, v in node.items()}
    if isinstance(node, list):
        return [_render_node(item, context) for item in node]
    return node
