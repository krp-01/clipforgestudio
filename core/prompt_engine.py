from __future__ import annotations

from core.profile_manager import UserProfile


class PromptEngine:
    def __init__(self, max_chars: int = 7000) -> None:
        self.max_chars = max_chars

    def build_prompt(
        self,
        system_instruction: str,
        profile: UserProfile,
        short_term_memory: list[dict],
        long_term_candidates: list[dict],
        current_message: str,
    ) -> str:
        profile_block = (
            f"User profile:\n"
            f"- Name: {profile.display_name}\n"
            f"- Risk tolerance: {profile.risk_tolerance:.2f}\n"
            f"- Communication style: {profile.communication_style}\n"
            f"- Emotional preference: {profile.emotional_tone_preference}\n"
            f"- Ambition level: {profile.ambition_level:.2f}\n"
            f"- Goals: {profile.goals or 'Not set'}\n"
        )

        recent_block = "\n".join(
            f"[{m['role']}] {m['content']}" for m in short_term_memory[-8:]
        )

        prioritized_memory = sorted(
            long_term_candidates,
            key=lambda m: (m.get("is_important", 0), m.get("created_at", "")),
            reverse=True,
        )[:6]
        long_term_block = "\n".join(
            f"({m['category']}) {m['content'][:220]}" for m in prioritized_memory
        )

        prompt = (
            f"{system_instruction}\n\n"
            f"{profile_block}\n"
            f"Recent conversation context:\n{recent_block or 'No recent messages'}\n\n"
            f"Relevant long-term memories:\n{long_term_block or 'No relevant long-term memories'}\n\n"
            f"Current user message:\n{current_message}\n\n"
            "Instruction: Adapt your response to the user's profile and current emotional signal."
        )

        if len(prompt) > self.max_chars:
            overflow = len(prompt) - self.max_chars
            trunc_len = max(40, len(long_term_block) - overflow)
            long_term_block = long_term_block[:trunc_len] + " ...[truncated]"
            prompt = (
                f"{system_instruction}\n\n{profile_block}\n"
                f"Recent conversation context:\n{recent_block or 'No recent messages'}\n\n"
                f"Relevant long-term memories:\n{long_term_block}\n\n"
                f"Current user message:\n{current_message}"
            )
        return prompt
