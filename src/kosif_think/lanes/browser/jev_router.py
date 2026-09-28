"""
Jev Decision Router: Fast local ranking for deterministic element selection,
falling back to TypeSafe Jev bounded model decision only when ambiguous.
"""

from typing import Dict, Any, List, Optional
import re
import time

class JevDecisionRouter:
    """Selects actions using deterministic ranking with bounded Jev routing."""

    def __init__(self):
        self._action_history: List[str] = []

    def rank_candidates(self, elements: List[Dict[str, Any]], goal: str) -> List[Dict[str, Any]]:
        """Scores elements deterministically based on keyword similarity and visual hierarchy."""
        words = set(re.findall(r'\w+', goal.lower()))
        scored = []

        for el in elements:
            text = f"{el.get('text', '')} {el.get('name', '')} {el.get('placeholder', '')} {el.get('role', '')}".lower()
            score = 0.0

            # Match words
            for w in words:
                if len(w) > 2 and w in text:
                    score += 25.0

            # Boost input/search elements for search goals
            if any(k in goal.lower() for k in ["ابحث", "search", "find", "google"]):
                if el.get("tag") in ("input", "textarea") or el.get("role") in ("searchbox", "combobox"):
                    score += 40.0

            # In viewport boost
            if el.get("in_viewport"):
                score += 15.0

            scored.append({"element": el, "score": score})

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored

    def choose_action(self, elements: List[Dict[str, Any]], goal: str) -> Dict[str, Any]:
        """Chooses the next action, enforcing loop prevention."""
        candidates = self.rank_candidates(elements, goal)
        if not candidates or candidates[0]["score"] == 0:
            # Ambiguity or no obvious match
            return {"action": "scroll", "amount": 450, "reason": "No high-confidence match found. Scrolling to reveal new candidates."}

        top = candidates[0]
        runner_up = candidates[1] if len(candidates) > 1 else None

        # Check for ambiguity: if top two are tied with high score, bounded Jev choice is used
        is_ambiguous = runner_up and abs(top["score"] - runner_up["score"]) < 5.0 and top["score"] > 20.0

        target_el = top["element"]
        target_id = target_el.get("id")

        # Anti-loop check: do not repeatedly select the exact same target if it produced no progress
        if len(self._action_history) >= 2 and self._action_history[-1] == target_id and self._action_history[-2] == target_id:
            # Loop detected: select alternative candidate or scroll
            if runner_up and runner_up["score"] > 0:
                target_el = runner_up["element"]
                target_id = target_el.get("id")
            else:
                return {"action": "scroll", "amount": 400, "reason": "Loop detected on candidate. Breaking loop with scroll."}

        self._action_history.append(target_id)
        if len(self._action_history) > 20:
            self._action_history.pop(0)

        # Decide operation
        tag = target_el.get("tag", "")
        role = target_el.get("role", "")
        if tag in ("input", "textarea") or role in ("searchbox", "textbox", "combobox"):
            # Extract query
            clean_query = re.sub(r'^(?:ابحث عن|بحث عن|search for|find|google)\s*', '', goal, flags=re.I).strip()
            return {
                "action": "type",
                "target_id": target_id,
                "text": clean_query or goal,
                "press_enter": True,
                "is_ambiguous": is_ambiguous,
                "score": top["score"]
            }

        return {
            "action": "click",
            "target_id": target_id,
            "is_ambiguous": is_ambiguous,
            "score": top["score"]
        }
