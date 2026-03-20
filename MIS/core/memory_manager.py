from __future__ import annotations

from typing import Any

from database.db_manager import DatabaseManager
from utils.helpers import clamp, utc_now_iso


class MemoryManager:
    def __init__(self, db: DatabaseManager) -> None:
        self.db = db

    def store_experience(
        self,
        user_id: int,
        content: str,
        context: dict[str, Any],
        emotional_valence: float,
        result: str,
        category: str,
        importance: float,
        novelty: float,
        goal_relevance: float,
    ) -> None:
        memory_freq = self._increment_memory_frequency(user_id, content)
        weight = self.calculate_weight(
            emotional_intensity=abs(emotional_valence),
            importance=importance,
            frequency=memory_freq,
            goal_relevance=goal_relevance,
        )

        self.db.execute(
            """
            INSERT INTO experiences(user_id, content, context, emotional_valence, result, timestamp, weight, category, importance, novelty)
            VALUES(?,?,?,?,?,?,?,?,?,?)
            """,
            (
                user_id,
                content,
                self.db.json_dumps(context),
                emotional_valence,
                result,
                utc_now_iso(),
                weight,
                category,
                importance,
                novelty,
            ),
        )

    def _increment_memory_frequency(self, user_id: int, content: str) -> int:
        key = content.strip().lower()[:120]
        now = utc_now_iso()
        existing = self.db.fetch_one(
            "SELECT * FROM memory WHERE user_id=? AND memory_type='episodic' AND key=?",
            (user_id, key),
        )
        if existing:
            freq = int(existing["frequency"]) + 1
            self.db.execute(
                "UPDATE memory SET frequency=?, last_accessed=? WHERE id=?",
                (freq, now, existing["id"]),
            )
            return freq

        self.db.execute(
            """
            INSERT INTO memory(user_id, memory_type, key, value, weight, last_accessed, frequency)
            VALUES(?,?,?,?,?,?,?)
            """,
            (user_id, "episodic", key, content, 0.4, now, 1),
        )
        return 1

    def upsert_semantic_memory(self, user_id: int, key: str, value: str, weight: float) -> None:
        now = utc_now_iso()
        existing = self.db.fetch_one(
            "SELECT * FROM memory WHERE user_id=? AND memory_type='semantic' AND key=?",
            (user_id, key),
        )
        if existing:
            merged_weight = clamp((existing["weight"] * 0.7) + (weight * 0.3))
            self.db.execute(
                "UPDATE memory SET value=?, weight=?, last_accessed=?, frequency=frequency+1 WHERE id=?",
                (value, merged_weight, now, existing["id"]),
            )
            return

        self.db.execute(
            """
            INSERT INTO memory(user_id, memory_type, key, value, weight, last_accessed, frequency)
            VALUES(?,?,?,?,?,?,?)
            """,
            (user_id, "semantic", key, value, weight, now, 1),
        )

    def retrieve_relevant_memories(self, user_id: int, keywords: list[str], limit: int = 5) -> list[dict]:
        rows = self.db.fetch_all(
            "SELECT * FROM experiences WHERE user_id=? ORDER BY timestamp DESC LIMIT 80",
            (user_id,),
        )
        scored = []
        keyset = set(k.lower() for k in keywords)
        for row in rows:
            content_words = set(row["content"].lower().split())
            overlap = len(content_words.intersection(keyset))
            relevance = self.relevance_score(float(row["weight"]), overlap)
            scored.append((relevance, row))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [dict(item[1], relevance=round(item[0], 3)) for item in scored[:limit]]

    def relevance_score(self, memory_weight: float, keyword_overlap: int) -> float:
        return clamp((memory_weight * 0.75) + min(0.25, keyword_overlap * 0.06), 0.0, 1.0)

    def calculate_weight(
        self,
        emotional_intensity: float,
        importance: float,
        frequency: int,
        goal_relevance: float,
    ) -> float:
        frequency_factor = min(1.0, 0.2 + (0.1 * min(6, frequency)))
        return round(
            clamp(
                0.35 * emotional_intensity
                + 0.25 * importance
                + 0.2 * frequency_factor
                + 0.2 * goal_relevance
            ),
            3,
        )
