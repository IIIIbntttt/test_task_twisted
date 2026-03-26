from dataclasses import dataclass, field


@dataclass
class SaveConfigRequest:
    service: str
    yaml_content: str


@dataclass
class GetConfigRequest:
    service: str
    version: int | None = field(default=None)
    use_template: bool = field(default=False)
    template_context: dict[str, str] = field(default_factory=dict)


@dataclass
class GetHistoryRequest:
    service: str
