from __future__ import annotations

import random
from abc import ABC, abstractmethod


class AIConnector(ABC):
    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        raise NotImplementedError


class MockAIConnector(AIConnector):
    def generate_response(self, prompt: str) -> str:
        tone = "balanced"
        if "Risk tolerance: 0." in prompt:
            tone = "cautious"
        if "Ambition level: 0.8" in prompt or "Ambition level: 0.9" in prompt:
            tone = "ambitious"

        templates = {
            "cautious": "Here is a safe and structured plan: start small, validate assumptions, then scale.",
            "ambitious": "Let's optimize for upside: define a moonshot objective, fast milestones, and rapid execution loops.",
            "balanced": "Here is a pragmatic plan balancing risk, speed, and clarity for your next step.",
        }
        suffixes = [
            "I can refine this with more constraints.",
            "If useful, I can convert this into a checklist.",
            "Want me to break this into week-by-week actions?",
        ]
        return f"{templates[tone]} {random.choice(suffixes)}"


class SafeFallbackConnector(AIConnector):
    def __init__(self, primary: AIConnector) -> None:
        self.primary = primary

    def generate_response(self, prompt: str) -> str:
        try:
            return self.primary.generate_response(prompt)
        except Exception:
            return (
                "I'm currently experiencing an AI provider issue, but your data is safe. "
                "Please retry in a moment while I continue logging the conversation."
            )
