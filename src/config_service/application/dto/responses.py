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


@dataclass
class GetHistoryResponse:
    items: list[HistoryItem]
