from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from config.settings import DB_PATH, SCHEMA_PATH
from utils.helpers import utc_now_iso


class DatabaseManager:
    def __init__(self, db_path: Path = DB_PATH, schema_path: Path = SCHEMA_PATH) -> None:
        self.db_path = db_path
        self.schema_path = schema_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize_schema(self) -> None:
        schema = self.schema_path.read_text(encoding="utf-8")
        with self._connect() as conn:
            conn.executescript(schema)
            conn.commit()

    def execute(self, query: str, params: tuple[Any, ...] = ()) -> None:
        with self._connect() as conn:
            conn.execute(query, params)
            conn.commit()

    def fetch_one(self, query: str, params: tuple[Any, ...] = ()) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(query, params).fetchone()
            return dict(row) if row else None

    def fetch_all(self, query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]

    def ensure_user(self, name: str, objectives: str, response_style: str, detail_level: str) -> int:
        now = utc_now_iso()
        existing = self.fetch_one("SELECT * FROM users ORDER BY id ASC LIMIT 1")
        if existing:
            self.execute(
                """
                UPDATE users SET name=?, objectives=?, response_style=?, detail_level=?, updated_at=?
                WHERE id=?
                """,
                (name, objectives, response_style, detail_level, now, existing["id"]),
            )
            return int(existing["id"])

        with self._connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO users(name, objectives, response_style, detail_level, created_at, updated_at)
                VALUES(?,?,?,?,?,?)
                """,
                (name, objectives, response_style, detail_level, now, now),
            )
            conn.commit()
            return int(cursor.lastrowid)

    @staticmethod
    def json_dumps(value: Any) -> str:
        return json.dumps(value, ensure_ascii=False)

    @staticmethod
    def json_loads(value: str, fallback: Any) -> Any:
        try:
            return json.loads(value)
        except (TypeError, json.JSONDecodeError):
            return fallback
