from dataclasses import dataclass, field


@dataclass
class SaveConfigRequest:
    service: str
    yaml_content: str


@dataclass(frozen=True, slots=True)
class GetConfigRequest:
    service: str
    version: int | None = None
    use_template: bool =False
    template_context: dict[str, str] = field(default_factory=dict)


@dataclass
class GetHistoryRequest:
    service: str
