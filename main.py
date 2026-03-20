from __future__ import annotations

from config.settings import SettingsManager
from core.ai_connector import MockAIConnector, SafeFallbackConnector
from core.memory_manager import MemoryManager
from core.profile_manager import ProfileManager
from core.prompt_engine import PromptEngine
from core.reasoning_engine import ReasoningEngine
from database.db_manager import DBManager
from gui_app import MISApp
from utils.logger import configure_logger


def build_app() -> MISApp:
    settings_manager = SettingsManager()
    settings = settings_manager.settings

    logger = configure_logger(settings.log_path)
    logger.info("Initializing MIS application")

    db = DBManager(settings.db_path)
    if not db.health_check():
        logger.error("Database integrity check failed; app will continue with caution")

    profile_manager = ProfileManager(db)
    user_row_id = profile_manager.get_or_create_user(settings.user_id, display_name="Default User")

    memory_manager = MemoryManager(db, short_limit=settings.short_term_memory_limit)
    memory_manager.load_recent_to_short_term(user_row_id)

    prompt_engine = PromptEngine(max_chars=settings.max_prompt_chars)
    ai = SafeFallbackConnector(MockAIConnector())

    reasoning_engine = ReasoningEngine(
        profile_manager=profile_manager,
        memory_manager=memory_manager,
        prompt_engine=prompt_engine,
        ai_connector=ai,
        summary_trigger_messages=settings.summary_trigger_messages,
    )

    return MISApp(
        settings=settings,
        reasoning_engine=reasoning_engine,
        profile_manager=profile_manager,
        memory_manager=memory_manager,
    )


if __name__ == "__main__":
    app = build_app()
    app.mainloop()
