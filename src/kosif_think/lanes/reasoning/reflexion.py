"""
Reflexion Engine for KOSIF Think.
Implements autonomous self-reflection, learning from trial failures,
and episodic verbal memory reinforcement inspired by Shinn et al. (MIT/Northeastern).
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import time

@dataclass
class ReflectionRecord:
    trial_number: int
    action_taken: str
    observed_outcome: str
    success: bool
    reflection: str
    lesson_learned: str

class ReflexionEngine:
    """Self-improving agent loop that converts execution errors into verbal insights."""

    def __init__(self):
        self.memory_buffer: List[ReflectionRecord] = []

    def reflect_on_trial(
        self,
        trial_number: int,
        action_taken: str,
        observed_outcome: str,
        success: bool,
        goal: str
    ) -> ReflectionRecord:
        """Analyzes why an action succeeded or failed, and synthesizes a permanent lesson."""
        if success:
            reflection = f"Action '{action_taken}' successfully met observable postconditions for '{goal[:40]}'."
            lesson = f"Strategy '{action_taken}' is valid and reproducible."
        else:
            reflection = f"Action '{action_taken}' produced unexpected outcome: '{observed_outcome[:80]}'."
            lesson = f"Avoid repeating '{action_taken}' under identical state; verify pre-requisites and mutate approach."

        rec = ReflectionRecord(
            trial_number=trial_number,
            action_taken=action_taken,
            observed_outcome=observed_outcome,
            success=success,
            reflection=reflection,
            lesson_learned=lesson
        )
        self.memory_buffer.append(rec)
        return rec

    def get_context_advice(self, current_intent: str) -> List[str]:
        """Retrieves lessons learned from past failed or successful trials."""
        advice = []
        for r in self.memory_buffer:
            if not r.success:
                advice.append(f"[Past Failure Insight (Trial {r.trial_number})]: {r.lesson_learned}")
            else:
                advice.append(f"[Confirmed Success Prior]: {r.lesson_learned}")
        return advice[-5:]
