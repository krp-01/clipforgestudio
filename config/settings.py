from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class AppSettings:
    app_name: str = "MIS - Memory Identity Stratified"
    db_path: str = "data/mis.db"
    log_path: str = "data/mis.log"
    short_term_memory_limit: int = 12
    max_prompt_chars: int = 7000
    memory_search_limit: int = 12
    summary_trigger_messages: int = 120
    ai_mode: str = "mock"
    user_id: str = "default_user"


class SettingsManager:
    """Loads and persists JSON configuration only."""

    def __init__(self, config_file: str = "config/settings.json") -> None:
        self.config_file = Path(config_file)
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self.settings = self._load_or_create()

    def _load_or_create(self) -> AppSettings:
        if not self.config_file.exists():
            defaults = AppSettings()
            self.save(defaults)
            return defaults

        try:
            raw = json.loads(self.config_file.read_text(encoding="utf-8"))
            return AppSettings(**raw)
        except Exception:
            defaults = AppSettings()
            self.save(defaults)
            return defaults

    def save(self, settings: AppSettings) -> None:
        self.config_file.write_text(
            json.dumps(asdict(settings), indent=2),
            encoding="utf-8",
        )
        self.settings = settings
