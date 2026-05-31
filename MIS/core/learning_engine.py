from __future__ import annotations

from core.memory_manager import MemoryManager
from core.identity_core import IdentityCore
from core.goals_manager import GoalsManager
from core.emotion_engine import EmotionEngine


class LearningEngine:
    def __init__(
        self,
        memory_manager: MemoryManager,
        emotion_engine: EmotionEngine,
        identity_core: IdentityCore,
        goals_manager: GoalsManager,
    ) -> None:
        self.memory_manager = memory_manager
        self.emotion_engine = emotion_engine
        self.identity_core = identity_core
        self.goals_manager = goals_manager

    def learn(
        self,
        user_id: int,
        user_text: str,
        response_text: str,
        perception: dict,
        emotions: dict,
        identity: dict,
        goals: list[dict],
    ) -> None:
        goal_relevance = self.goals_manager.goal_relevance(goals)
        emotional_valence = self.emotion_engine.emotional_valence(emotions)

        self.memory_manager.store_experience(
            user_id=user_id,
            content=user_text,
            context={"intent": perception["intent"], "tone": perception["tone"]},
            emotional_valence=emotional_valence,
            result=response_text,
            category=perception["intent"],
            importance=perception["importance"],
            novelty=perception["novelty"],
            goal_relevance=goal_relevance,
        )

        if perception["keywords"]:
            top_keywords = ", ".join(perception["keywords"][:5])
            self.memory_manager.upsert_semantic_memory(user_id, "interests_recent", top_keywords, perception["importance"])

        self.emotion_engine.save_state(user_id, emotions)
        self.identity_core.save_identity(user_id, identity)
        self.goals_manager.save(user_id, goals)
