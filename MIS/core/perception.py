from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass
class PerceptionResult:
    raw_input: str
    intent: str
    keywords: list[str]
    tone: str
    novelty: float
    importance: float

    def to_dict(self) -> dict:
        return asdict(self)


class PerceptionModule:
    def __init__(self) -> None:
        self.seen_signatures: set[str] = set()

    def analyze(self, text: str) -> PerceptionResult:
        normalized = text.strip().lower()
        words = [w.strip(".,!?;:()[]{}\"'") for w in normalized.split() if w]
        keywords = [w for w in words if len(w) > 3][:8]

        intent = self._infer_intent(normalized)
        tone = self._infer_tone(normalized)

        signature = " ".join(keywords[:4])
        novelty = 0.9 if signature and signature not in self.seen_signatures else 0.35
        if signature:
            self.seen_signatures.add(signature)

        importance = min(1.0, 0.25 + (0.08 * len(keywords)) + (0.15 if "?" in text else 0.0))

        return PerceptionResult(
            raw_input=text,
            intent=intent,
            keywords=keywords,
            tone=tone,
            novelty=round(novelty, 3),
            importance=round(importance, 3),
        )

    def _infer_intent(self, text: str) -> str:
        if "?" in text or any(k in text for k in ["cum", "ce", "de ce", "când", "unde"]):
            return "question"
        if any(k in text for k in ["ajută", "plan", "ghid", "sfat"]):
            return "guidance"
        if any(k in text for k in ["mă simt", "simt", "anxios", "fericit", "trist"]):
            return "emotional_disclosure"
        return "statement"

    def _infer_tone(self, text: str) -> str:
        if any(k in text for k in ["urgent", "repede", "acum", "panică"]):
            return "urgent"
        if any(k in text for k in ["mulțumesc", "te rog", "apreciez"]):
            return "warm"
        if any(k in text for k in ["nu merge", "problemă", "greșit"]):
            return "frustrated"
        return "neutral"
