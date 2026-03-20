from __future__ import annotations

from config.settings import GOAL_KEYS
from database.db_manager import DatabaseManager
from utils.helpers import clamp, utc_now_iso


GOAL_DESCRIPTIONS = {
    "understand_user": "Înțelege utilizatorul",
    "maintain_coherence": "Menține coerența",
    "improve_responses": "Îmbunătățește răspunsurile",
    "support_user_goals": "Susține obiectivele utilizatorului",
    "clarify_ambiguity": "Clarifică ambiguitățile",
}


class GoalsManager:
    def __init__(self, db: DatabaseManager) -> None:
        self.db = db

    def get_or_create_goals(self, user_id: int) -> list[dict]:
        rows = self.db.fetch_all("SELECT * FROM goals WHERE user_id=? ORDER BY priority DESC", (user_id,))
        if rows:
            return rows

        now = utc_now_iso()
        defaults = [
            ("understand_user", 0.95, 0.8),
            ("maintain_coherence", 0.9, 0.75),
            ("improve_responses", 0.88, 0.72),
            ("support_user_goals", 0.92, 0.8),
            ("clarify_ambiguity", 0.78, 0.6),
        ]
        for key, priority, intensity in defaults:
            self.db.execute(
                "INSERT INTO goals(user_id, goal_key, description, priority, intensity, updated_at) VALUES(?,?,?,?,?,?)",
                (user_id, key, GOAL_DESCRIPTIONS[key], priority, intensity, now),
            )
        return self.get_or_create_goals(user_id)

    def evaluate(self, goals: list[dict], perception: dict) -> list[dict]:
        adjusted = []
        for goal in goals:
            intensity = float(goal["intensity"])
            if goal["goal_key"] == "clarify_ambiguity" and perception["intent"] == "question":
                intensity += 0.12
            if goal["goal_key"] == "support_user_goals" and perception["intent"] == "guidance":
                intensity += 0.15
            if goal["goal_key"] == "maintain_coherence":
                intensity += 0.04
            goal = dict(goal)
            goal["intensity"] = round(clamp(intensity), 3)
            adjusted.append(goal)
        return sorted(adjusted, key=lambda g: (g["priority"] * g["intensity"]), reverse=True)

    def save(self, user_id: int, goals: list[dict]) -> None:
        now = utc_now_iso()
        for goal in goals:
            self.db.execute(
                "UPDATE goals SET intensity=?, updated_at=? WHERE id=? AND user_id=?",
                (goal["intensity"], now, goal["id"], user_id),
            )

    def goal_relevance(self, goals: list[dict]) -> float:
        if not goals:
            return 0.4
        top = goals[0]
        return round(clamp(float(top["priority"]) * float(top["intensity"])), 3)
