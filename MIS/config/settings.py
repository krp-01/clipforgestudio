from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "mis.db"
SCHEMA_PATH = BASE_DIR / "database" / "schema.sql"
LOG_PATH = DATA_DIR / "mis.log"

DEFAULT_USER_NAME = "Utilizator"
DEFAULT_RESPONSE_STYLE = "echilibrat"
DEFAULT_DETAIL_LEVEL = "mediu"
DEFAULT_GOALS = "Înțelegerea utilizatorului"

AI_MOCK_MODE = True

EMOTION_KEYS = ["risk", "curiosity", "reward", "stress", "attachment"]
GOAL_KEYS = [
    "understand_user",
    "maintain_coherence",
    "improve_responses",
    "support_user_goals",
    "clarify_ambiguity",
]
