from __future__ import annotations

from collections import deque

from database.db_manager import DBManager
from utils.helpers import basic_emotion_signal, utc_now_iso


class MemoryManager:
    def __init__(self, db: DBManager, short_limit: int = 12) -> None:
        self.db = db
        self.short_limit = short_limit
        self.short_term: dict[int, deque[dict[str, str]]] = {}

    def _ensure_queue(self, user_row_id: int) -> deque[dict[str, str]]:
        if user_row_id not in self.short_term:
            self.short_term[user_row_id] = deque(maxlen=self.short_limit)
        return self.short_term[user_row_id]

    def load_recent_to_short_term(self, user_row_id: int) -> None:
        queue = self._ensure_queue(user_row_id)
        queue.clear()
        rows = self.db.fetch_all(
            """
            SELECT role, content, created_at
            FROM messages
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (user_row_id, self.short_limit),
        )
        for row in reversed(rows):
            queue.append(row)

    def store_message(
        self,
        user_row_id: int,
        role: str,
        content: str,
        category: str = "general",
        is_important: bool = False,
        tags: list[str] | None = None,
    ) -> int:
        message_id = self.db.execute(
            """
            INSERT INTO messages (user_id, role, content, category, is_important, emotion_signal, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_row_id,
                role,
                content,
                category,
                1 if is_important else 0,
                basic_emotion_signal(content),
                utc_now_iso(),
            ),
        )

        for tag in (tags or []):
            self.db.execute(
                "INSERT INTO memory_tags (message_id, tag, created_at) VALUES (?, ?, ?)",
                (message_id, tag.lower(), utc_now_iso()),
            )

        queue = self._ensure_queue(user_row_id)
        queue.append({"role": role, "content": content, "created_at": utc_now_iso()})
        return message_id

    def get_short_term_context(self, user_row_id: int) -> list[dict[str, str]]:
        return list(self._ensure_queue(user_row_id))

    def search_long_term_memory(self, user_row_id: int, query: str, limit: int = 10) -> list[dict]:
        pattern = f"%{query.lower()}%"
        return self.db.fetch_all(
            """
            SELECT DISTINCT m.id, m.role, m.content, m.category, m.created_at, m.is_important
            FROM messages m
            LEFT JOIN memory_tags t ON t.message_id = m.id
            WHERE m.user_id = ?
              AND (
                LOWER(m.content) LIKE ? OR
                LOWER(m.category) LIKE ? OR
                LOWER(COALESCE(t.tag, '')) LIKE ?
              )
            ORDER BY m.is_important DESC, m.id DESC
            LIMIT ?
            """,
            (user_row_id, pattern, pattern, pattern, limit),
        )

    def fetch_recent_messages(self, user_row_id: int, limit: int = 30) -> list[dict]:
        return self.db.fetch_all(
            """
            SELECT id, role, content, category, created_at, is_important, emotion_signal
            FROM messages
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (user_row_id, limit),
        )

    def summarize_if_needed(self, user_row_id: int, trigger: int) -> None:
        count_row = self.db.fetch_one(
            "SELECT COUNT(*) as cnt FROM messages WHERE user_id = ?", (user_row_id,)
        )
        if not count_row or int(count_row["cnt"]) < trigger:
            return

        old_rows = self.db.fetch_all(
            """
            SELECT content FROM messages
            WHERE user_id = ?
            ORDER BY id ASC
            LIMIT 30
            """,
            (user_row_id,),
        )
        if not old_rows:
            return

        bullets = [f"- {row['content'][:120]}" for row in old_rows[:8]]
        summary = "Memory summary\n" + "\n".join(bullets)
        self.store_message(
            user_row_id=user_row_id,
            role="assistant",
            content=summary,
            category="summary",
            is_important=True,
            tags=["summary", "compression"],
        )
