from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Configuration:
    service: str
    version: int
    payload: dict[str, object]
    id: int | None = field(default=None)
    created_at: datetime | None = field(default=None)
