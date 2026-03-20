from __future__ import annotations

from core.decision_engine import Decision


class PromptBuilder:
    def build(
        self,
        user_text: str,
        perception: dict,
        memories: list[dict],
        emotions: dict,
        identity: dict,
        goals: list[dict],
        decision: Decision,
    ) -> str:
        memory_lines = [f"- {m['content']} (relevanță {m['relevance']})" for m in memories[:4]]
        goal_lines = [f"- {g['description']} (intensitate {g['intensity']})" for g in goals[:3]]

        return (
            "Sistem MIS (arhitectură cognitivă stratificată).\n"
            f"Intrare utilizator: {user_text}\n"
            f"Percepție: intenție={perception['intent']}, ton={perception['tone']}, importanță={perception['importance']}\n"
            f"Emoții: {emotions}\n"
            f"Identitate: {identity['dynamic_summary']}\n"
            f"Decizie: tip={decision.response_type}, ton={decision.tone}, profunzime={decision.depth}, acțiune={decision.action}\n"
            "Memorii relevante:\n"
            + ("\n".join(memory_lines) if memory_lines else "- niciuna")
            + "\nScopuri active:\n"
            + ("\n".join(goal_lines) if goal_lines else "- niciun scop")
            + "\nRăspunde exclusiv în română, empatic, coerent și orientat pe acțiune."
        )
