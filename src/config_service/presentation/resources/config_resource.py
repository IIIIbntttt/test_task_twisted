"""Держатель зависимостей для HTTP-слоя. Хранит use cases, хендлеры живут отдельно."""

from config_service.application.use_cases.get_config import GetConfigUseCase
from config_service.application.use_cases.get_history import GetHistoryUseCase
from config_service.application.use_cases.save_config import SaveConfigUseCase


class ConfigResource:
    def __init__(
        self,
        save_uc: SaveConfigUseCase,
        get_uc: GetConfigUseCase,
        history_uc: GetHistoryUseCase,
    ) -> None:
        self.save_uc = save_uc
        self.get_uc = get_uc
        self.history_uc = history_uc
