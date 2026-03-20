from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Decision:
    response_type: str
    tone: str
    depth: str
    action: str


class DecisionEngine:
    def decide(
        self,
        perception: dict,
        emotions: dict,
        identity_influence: dict,
        goals: list[dict],
        memories: list[dict],
    ) -> Decision:
        intent = perception["intent"]
        top_goal = goals[0]["goal_key"] if goals else "maintain_coherence"

        if emotions["stress"] > 0.7 or perception["tone"] == "urgent":
            tone = "calm_supportive"
            response_type = "stabilization"
            action = "warn_and_guide"
        elif intent == "question":
            tone = "clarifying"
            response_type = "answer"
            action = "answer_with_context"
        elif intent == "guidance":
            tone = "structured"
            response_type = "guide"
            action = "stepwise_guidance"
        else:
            tone = "reflective"
            response_type = "reflection"
            action = "ask_or_confirm"

        if identity_influence["detail_level"] == "ridicat" or top_goal == "improve_responses":
            depth = "detaliat"
        elif len(memories) >= 3:
            depth = "mediu"
        else:
            depth = "scurt"

        return Decision(response_type=response_type, tone=tone, depth=depth, action=action)
