from typing import cast

from jinja2.sandbox import SandboxedEnvironment

_env = SandboxedEnvironment()


def render_jinja(
    payload: dict[str, object],
    context: dict[str, str],
) -> dict[str, object]:
    """Рекурсивно рендерит Jinja2-шаблоны в строковых значениях payload.

    Использует SandboxedEnvironment для защиты от template injection.
    """
    return cast(dict[str, object], _render_node(payload, context))


def _render_node(node: object, context: dict[str, str]) -> object:
    if isinstance(node, str):
        return _env.from_string(node).render(**context)
    if isinstance(node, dict):
        return {k: _render_node(v, context) for k, v in node.items()}
    if isinstance(node, list):
        return [_render_node(item, context) for item in node]
    return node
