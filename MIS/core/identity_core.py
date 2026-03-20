from __future__ import annotations

from typing import Any

from database.db_manager import DatabaseManager
from utils.helpers import clamp, utc_now_iso


class IdentityCore:
    def __init__(self, db: DatabaseManager) -> None:
        self.db = db

    def get_or_create_identity(self, user_id: int) -> dict[str, Any]:
        row = self.db.fetch_one("SELECT * FROM identity WHERE user_id=? ORDER BY id DESC LIMIT 1", (user_id,))
        if row:
            return self._deserialize(row)

        default = {
            "traits": {"analitic": 0.5, "deschis": 0.5, "orientat_spre_acțiune": 0.5},
            "preferences": {"stil": "echilibrat", "detaliu": "mediu"},
            "communication_style": "clar și empatic",
            "interests": ["dezvoltare personală", "rezolvare de probleme"],
            "risk_profile": 0.45,
            "dynamic_summary": "Identitate inițială în formare.",
            "stability": 0.8,
        }
        self.save_identity(user_id, default)
        return default

    def evolve(self, current: dict[str, Any], memories: list[dict], perception: dict, emotions: dict) -> dict[str, Any]:
        updated = dict(current)
        traits = dict(updated["traits"])

        memory_signal = min(1.0, sum(float(m["weight"]) for m in memories[:5]) / 3.0) if memories else 0.2
        emotional_pressure = (emotions["stress"] + emotions["risk"]) / 2

        traits["analitic"] = round(clamp(traits.get("analitic", 0.5) * 0.95 + 0.05 * perception["importance"]), 3)
        traits["deschis"] = round(clamp(traits.get("deschis", 0.5) * 0.97 + 0.03 * emotions["curiosity"]), 3)
        traits["orientat_spre_acțiune"] = round(
            clamp(traits.get("orientat_spre_acțiune", 0.5) * 0.96 + 0.04 * (1 - emotional_pressure)), 3
        )

        updated["traits"] = traits
        updated["risk_profile"] = round(clamp(updated["risk_profile"] * 0.97 + emotional_pressure * 0.03), 3)
        updated["stability"] = round(clamp(updated["stability"] * 0.99 + 0.01 * memory_signal), 3)
        updated["dynamic_summary"] = (
            f"Identitate stabilă ({updated['stability']:.2f}), "
            f"analitică ({traits['analitic']:.2f}) și orientată pe claritate."
        )
        return updated

    def influence(self, identity: dict[str, Any]) -> dict[str, Any]:
        return {
            "preferred_style": identity["preferences"].get("stil", "echilibrat"),
            "detail_level": identity["preferences"].get("detaliu", "mediu"),
            "risk_profile": identity["risk_profile"],
            "stability": identity["stability"],
        }

    def save_identity(self, user_id: int, identity: dict[str, Any]) -> None:
        self.db.execute(
            """
            INSERT INTO identity(user_id, traits, preferences, communication_style, interests, risk_profile, dynamic_summary, stability, updated_at)
            VALUES(?,?,?,?,?,?,?,?,?)
            """,
            (
                user_id,
                self.db.json_dumps(identity["traits"]),
                self.db.json_dumps(identity["preferences"]),
                identity["communication_style"],
                self.db.json_dumps(identity["interests"]),
                identity["risk_profile"],
                identity["dynamic_summary"],
                identity["stability"],
                utc_now_iso(),
            ),
        )

    def _deserialize(self, row: dict[str, Any]) -> dict[str, Any]:
        return {
            "traits": self.db.json_loads(row["traits"], {}),
            "preferences": self.db.json_loads(row["preferences"], {}),
            "communication_style": row["communication_style"],
            "interests": self.db.json_loads(row["interests"], []),
            "risk_profile": float(row["risk_profile"]),
            "dynamic_summary": row["dynamic_summary"],
            "stability": float(row["stability"]),
        }
