from __future__ import annotations

from dataclasses import dataclass

from database.db_manager import DBManager
from utils.helpers import utc_now_iso


@dataclass
class UserProfile:
    user_row_id: int
    external_user_id: str
    display_name: str
    risk_tolerance: float
    communication_style: str
    emotional_tone_preference: str
    ambition_level: float
    goals: str


class ProfileManager:
    def __init__(self, db: DBManager) -> None:
        self.db = db

    def get_or_create_user(self, external_user_id: str, display_name: str = "User") -> int:
        existing = self.db.fetch_one(
            "SELECT id FROM users WHERE external_user_id = ?", (external_user_id,)
        )
        if existing:
            return int(existing["id"])

        now = utc_now_iso()
        user_id = self.db.execute(
            """
            INSERT INTO users (external_user_id, display_name, created_at, updated_at)
            VALUES (?, ?, ?, ?)
            """,
            (external_user_id, display_name, now, now),
        )

        self.db.execute(
            """
            INSERT INTO profile_traits (
                user_id, risk_tolerance, communication_style,
                emotional_tone_preference, ambition_level, goals, updated_at
            ) VALUES (?, 0.5, 'balanced', 'balanced', 0.5, '', ?)
            """,
            (user_id, now),
        )
        return user_id

    def upsert_profile_from_onboarding(
        self,
        user_row_id: int,
        risk_tolerance: float,
        communication_style: str,
        emotional_tone_preference: str,
        ambition_level: float,
        goals: str,
    ) -> None:
        self.db.execute(
            """
            UPDATE profile_traits
            SET risk_tolerance = ?, communication_style = ?,
                emotional_tone_preference = ?, ambition_level = ?, goals = ?, updated_at = ?
            WHERE user_id = ?
            """,
            (
                risk_tolerance,
                communication_style,
                emotional_tone_preference,
                ambition_level,
                goals,
                utc_now_iso(),
                user_row_id,
            ),
        )

    def get_profile(self, external_user_id: str) -> UserProfile:
        row = self.db.fetch_one(
            """
            SELECT u.id as user_row_id, u.external_user_id, COALESCE(u.display_name, 'User') as display_name,
                   p.risk_tolerance, p.communication_style, p.emotional_tone_preference,
                   p.ambition_level, COALESCE(p.goals, '') as goals
            FROM users u
            JOIN profile_traits p ON p.user_id = u.id
            WHERE u.external_user_id = ?
            """,
            (external_user_id,),
        )
        if not row:
            user_row_id = self.get_or_create_user(external_user_id)
            return self.get_profile(external_user_id)

        return UserProfile(
            user_row_id=int(row["user_row_id"]),
            external_user_id=str(row["external_user_id"]),
            display_name=str(row["display_name"]),
            risk_tolerance=float(row["risk_tolerance"]),
            communication_style=str(row["communication_style"]),
            emotional_tone_preference=str(row["emotional_tone_preference"]),
            ambition_level=float(row["ambition_level"]),
            goals=str(row["goals"]),
        )

    def adapt_profile_from_behavior(self, user_row_id: int, message: str) -> None:
        profile = self.db.fetch_one(
            "SELECT risk_tolerance, ambition_level FROM profile_traits WHERE user_id = ?",
            (user_row_id,),
        )
        if not profile:
            return

        risk = float(profile["risk_tolerance"])
        ambition = float(profile["ambition_level"])

        lowered = message.lower()
        if any(word in lowered for word in ["safe", "secure", "stable", "avoid risk"]):
            risk = max(0.0, risk - 0.03)
        if any(word in lowered for word in ["aggressive", "scale fast", "moonshot", "bold"]):
            risk = min(1.0, risk + 0.04)
        if any(word in lowered for word in ["goal", "growth", "achieve", "ambitious"]):
            ambition = min(1.0, ambition + 0.03)

        self.db.execute(
            "UPDATE profile_traits SET risk_tolerance = ?, ambition_level = ?, updated_at = ? WHERE user_id = ?",
            (risk, ambition, utc_now_iso(), user_row_id),
        )
