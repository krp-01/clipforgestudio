from __future__ import annotations

import sqlite3
from pathlib import Path
from threading import Lock
from typing import Any


class DBManager:
    def __init__(self, db_path: str, schema_path: str = "database/schema.sql") -> None:
        self.db_path = Path(db_path)
        self.schema_path = Path(schema_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()
        self._initialize_database()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _initialize_database(self) -> None:
        schema_sql = self.schema_path.read_text(encoding="utf-8")
        with self._connect() as conn:
            conn.executescript(schema_sql)
            conn.commit()

    def execute(self, query: str, params: tuple[Any, ...] = ()) -> int:
        with self._lock:
            with self._connect() as conn:
                cursor = conn.execute(query, params)
                conn.commit()
                return cursor.lastrowid

    def fetch_one(self, query: str, params: tuple[Any, ...] = ()) -> dict[str, Any] | None:
        with self._lock:
            with self._connect() as conn:
                row = conn.execute(query, params).fetchone()
                return dict(row) if row else None

    def fetch_all(self, query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        with self._lock:
            with self._connect() as conn:
                rows = conn.execute(query, params).fetchall()
                return [dict(row) for row in rows]

    def health_check(self) -> bool:
        try:
            row = self.fetch_one("PRAGMA integrity_check;")
            return bool(row) and next(iter(row.values())) == "ok"
        except Exception:
            return False
