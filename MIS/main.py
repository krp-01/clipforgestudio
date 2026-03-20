from __future__ import annotations

from config.settings import AI_MOCK_MODE
from core.ai_connector import AIConnector
from core.decision_engine import DecisionEngine
from core.emotion_engine import EmotionEngine
from core.goals_manager import GoalsManager
from core.identity_core import IdentityCore
from core.learning_engine import LearningEngine
from core.memory_manager import MemoryManager
from core.perception import PerceptionModule
from core.prompt_builder import PromptBuilder
from database.db_manager import DatabaseManager
from utils.logger import setup_logger


class MISSystem:
    def __init__(self) -> None:
        self.logger = setup_logger("mis.system")
        self.db = DatabaseManager()

        self.perception = PerceptionModule()
        self.memory = MemoryManager(self.db)
        self.emotions = EmotionEngine(self.db)
        self.identity = IdentityCore(self.db)
        self.goals = GoalsManager(self.db)
        self.decision_engine = DecisionEngine()
        self.prompt_builder = PromptBuilder()
        self.ai = AIConnector(mock_mode=AI_MOCK_MODE)
        self.learning = LearningEngine(self.memory, self.emotions, self.identity, self.goals)

        self.user_id: int | None = None

    def onboard_user(self, name: str, objectives: str, response_style: str, detail_level: str) -> int:
        self.user_id = self.db.ensure_user(name, objectives, response_style, detail_level)
        self.logger.info("Onboarding finalizat pentru user_id=%s", self.user_id)
        return self.user_id

    def process_message(self, user_text: str) -> dict:
        if not self.user_id:
            raise RuntimeError("Utilizatorul nu este inițializat.")

        perception = self.perception.analyze(user_text).to_dict()
        relevant_memories = self.memory.retrieve_relevant_memories(self.user_id, perception["keywords"])

        current_emotions = self.emotions.get_or_create_state(self.user_id)
        updated_emotions = self.emotions.evaluate(
            current=current_emotions,
            tone=perception["tone"],
            importance=perception["importance"],
            novelty=perception["novelty"],
        )

        current_identity = self.identity.get_or_create_identity(self.user_id)
        evolved_identity = self.identity.evolve(
            current=current_identity,
            memories=relevant_memories,
            perception=perception,
            emotions=updated_emotions,
        )
        identity_influence = self.identity.influence(evolved_identity)

        goals = self.goals.get_or_create_goals(self.user_id)
        evaluated_goals = self.goals.evaluate(goals, perception)

        decision = self.decision_engine.decide(
            perception=perception,
            emotions=updated_emotions,
            identity_influence=identity_influence,
            goals=evaluated_goals,
            memories=relevant_memories,
        )

        prompt = self.prompt_builder.build(
            user_text=user_text,
            perception=perception,
            memories=relevant_memories,
            emotions=updated_emotions,
            identity=evolved_identity,
            goals=evaluated_goals,
            decision=decision,
        )
        response_text = self.ai.generate(prompt, decision, user_text)

        self.learning.learn(
            user_id=self.user_id,
            user_text=user_text,
            response_text=response_text,
            perception=perception,
            emotions=updated_emotions,
            identity=evolved_identity,
            goals=evaluated_goals,
        )

        self.logger.info("Buclă cognitivă completată. intent=%s tone=%s", perception["intent"], perception["tone"])

        return {
            "response": response_text,
            "perception": perception,
            "emotions": updated_emotions,
            "identity": evolved_identity,
            "goals": evaluated_goals,
            "memories": relevant_memories,
            "decision": decision,
        }


if __name__ == "__main__":
    from gui_app import run_app

    run_app()
