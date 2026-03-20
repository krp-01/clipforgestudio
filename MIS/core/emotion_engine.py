from __future__ import annotations

from config.settings import EMOTION_KEYS
from database.db_manager import DatabaseManager
from utils.helpers import clamp, utc_now_iso


class EmotionEngine:
    def __init__(self, db: DatabaseManager) -> None:
        self.db = db

    def get_or_create_state(self, user_id: int) -> dict[str, float]:
        row = self.db.fetch_one("SELECT * FROM emotions WHERE user_id=? ORDER BY id DESC LIMIT 1", (user_id,))
        if row:
            return {k: float(row[k]) for k in EMOTION_KEYS}

        default = {"risk": 0.35, "curiosity": 0.6, "reward": 0.5, "stress": 0.3, "attachment": 0.4}
        self._save(user_id, default)
        return default

    def evaluate(self, current: dict[str, float], tone: str, importance: float, novelty: float) -> dict[str, float]:
        updated = dict(current)
        updated["curiosity"] = clamp(updated["curiosity"] * 0.85 + novelty * 0.15)
        updated["stress"] = clamp(updated["stress"] + (0.2 if tone == "urgent" else -0.05) + (importance * 0.05))
        updated["risk"] = clamp(updated["risk"] + (0.15 if tone == "frustrated" else -0.03))
        updated["reward"] = clamp(updated["reward"] + (0.1 if tone == "warm" else 0.01) - updated["stress"] * 0.05)
        updated["attachment"] = clamp(updated["attachment"] + 0.04)
        return {k: round(v, 3) for k, v in updated.items()}

    def emotional_valence(self, state: dict[str, float]) -> float:
        positive = (state["reward"] + state["attachment"] + state["curiosity"]) / 3
        negative = (state["risk"] + state["stress"]) / 2
        return round(clamp(positive - negative, -1.0, 1.0), 3)

    def save_state(self, user_id: int, state: dict[str, float]) -> None:
        self._save(user_id, state)

    def _save(self, user_id: int, state: dict[str, float]) -> None:
        self.db.execute(
            """
            INSERT INTO emotions(user_id, risk, curiosity, reward, stress, attachment, updated_at)
            VALUES(?,?,?,?,?,?,?)
            """,
            (
                user_id,
                state["risk"],
                state["curiosity"],
                state["reward"],
                state["stress"],
                state["attachment"],
                utc_now_iso(),
            ),
        )
