from __future__ import annotations

from datetime import datetime, timezone


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def basic_emotion_signal(text: str) -> str:
    lowered = text.lower()
    anxious_words = {"worried", "anxious", "afraid", "confused", "overwhelmed"}
    positive_words = {"great", "excited", "confident", "happy", "energized"}

    if any(w in lowered for w in anxious_words):
        return "anxious"
    if any(w in lowered for w in positive_words):
        return "positive"
    if "?" in lowered and len(text) < 100:
        return "uncertain"
    return "neutral"


def infer_communication_complexity(text: str) -> str:
    long_sentence = len(text.split()) > 28
    technical_markers = any(t in text.lower() for t in ["architecture", "abstraction", "latency", "model"])
    if long_sentence or technical_markers:
        return "detailed"
    return "simple"
