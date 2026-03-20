from __future__ import annotations

from core.ai_connector import AIConnector
from core.memory_manager import MemoryManager
from core.profile_manager import ProfileManager
from core.prompt_engine import PromptEngine
from utils.helpers import basic_emotion_signal, infer_communication_complexity


class ReasoningEngine:
    def __init__(
        self,
        profile_manager: ProfileManager,
        memory_manager: MemoryManager,
        prompt_engine: PromptEngine,
        ai_connector: AIConnector,
        summary_trigger_messages: int = 120,
    ) -> None:
        self.profile_manager = profile_manager
        self.memory_manager = memory_manager
        self.prompt_engine = prompt_engine
        self.ai_connector = ai_connector
        self.summary_trigger_messages = summary_trigger_messages

        self.system_instruction = (
            "You are MIS, a cognitive twin AI. Always adapt to the user's identity profile, "
            "long-term context, and emotional signals while keeping responses useful and truthful."
        )

    def process_user_message(self, external_user_id: str, content: str) -> str:
        profile = self.profile_manager.get_profile(external_user_id)

        user_tags = [basic_emotion_signal(content), infer_communication_complexity(content)]
        self.memory_manager.store_message(
            profile.user_row_id,
            role="user",
            content=content,
            category="chat",
            tags=user_tags,
        )

        self.profile_manager.adapt_profile_from_behavior(profile.user_row_id, content)
        profile = self.profile_manager.get_profile(external_user_id)

        short_term = self.memory_manager.get_short_term_context(profile.user_row_id)
        long_term = self.memory_manager.search_long_term_memory(
            profile.user_row_id,
            query=content[:80],
            limit=12,
        )

        prompt = self.prompt_engine.build_prompt(
            system_instruction=self.system_instruction,
            profile=profile,
            short_term_memory=short_term,
            long_term_candidates=long_term,
            current_message=content,
        )

        response = self.ai_connector.generate_response(prompt)
        self.memory_manager.store_message(
            profile.user_row_id,
            role="assistant",
            content=response,
            category="response",
            is_important=False,
            tags=["generated"],
        )
        self.memory_manager.summarize_if_needed(profile.user_row_id, self.summary_trigger_messages)
        return response
