from dataclasses import dataclass
from datetime import datetime


@dataclass
class SaveConfigResponse:
    service: str
    version: int
    status: str


@dataclass
class GetConfigResponse:
    payload: dict[str, object]


@dataclass
class HistoryItem:
    version: int
    created_at: datetime

    def to_dict(self) -> dict[str, object]:
        return {"version": self.version, "created_at": self.created_at.isoformat()}


@dataclass
class GetHistoryResponse:
    items: list[HistoryItem]
