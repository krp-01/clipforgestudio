from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def normalize_scores(items: Iterable[float]) -> list[float]:
    values = list(items)
    total = sum(values)
    if total <= 0:
        return [0.0 for _ in values]
    return [v / total for v in values]
