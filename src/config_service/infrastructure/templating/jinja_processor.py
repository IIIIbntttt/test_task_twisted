from jinja2 import Template


class JinjaProcessor:
    """Рендерит Jinja2-шаблоны, встроенные в строковые значения payload конфигурации."""

    def render(
        self,
        payload: dict[str, object],
        context: dict[str, str],
    ) -> dict[str, object]:
        return self._render_node(payload, context)  # type: ignore[return-value]

    def _render_node(self, node: object, context: dict[str, str]) -> object:
        if isinstance(node, str):
            return Template(node).render(**context)
        if isinstance(node, dict):
            return {k: self._render_node(v, context) for k, v in node.items()}
        if isinstance(node, list):
            return [self._render_node(item, context) for item in node]
        return node
