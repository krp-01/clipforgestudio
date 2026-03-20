from __future__ import annotations

from core.decision_engine import Decision


class AIConnector:
    def __init__(self, mock_mode: bool = True) -> None:
        self.mock_mode = mock_mode

    def generate(self, prompt: str, decision: Decision, user_text: str) -> str:
        if self.mock_mode:
            return self._mock_response(decision, user_text)
        return "Conectorul API nu este configurat încă. Modul simulare este recomandat momentan."

    def _mock_response(self, decision: Decision, user_text: str) -> str:
        if decision.response_type == "stabilization":
            return (
                "Observ tensiune în mesaj. Hai să reducem presiunea: 1) respiră 30 secunde, "
                "2) spune-mi exact ce blocaj ai, 3) îți propun un plan clar în pași mici."
            )
        if decision.response_type == "answer":
            return (
                "Am analizat contextul tău și răspund țintit: "
                f"pentru «{user_text[:80]}», recomand să clarificăm obiectivul, constrângerile și criteriul de succes."
            )
        if decision.response_type == "guide":
            return (
                "Îți propun un ghid MIS în 3 pași: definim scopul, extragem experiențele relevante și alegem "
                "următoarea acțiune cu risc minim și valoare maximă."
            )
        return "Înțeleg. Reformulez ce ai spus, verific dacă am înțeles corect și apoi continui cu o recomandare concretă."
