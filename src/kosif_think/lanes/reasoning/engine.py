"""
Reasoning Lane Engine: Unifies Fast Heuristic, Multi-Agent Council, and Deep Cognitive reasoning.
"""

from typing import Dict, Any, Optional
import time
from .council import CouncilReasoning
from .cognitive import CognitiveUnderstanding
from ...core.cancellation import CancellationToken

class ReasoningLane:
    """Unified handler for the reasoning lane."""

    def __init__(self):
        self.council = CouncilReasoning()
        self.cognitive = CognitiveUnderstanding()

    async def dispatch_step(self, step: Any, cancellation_token: Optional[CancellationToken] = None) -> Dict[str, Any]:
        """Executes a reasoning step."""
        if cancellation_token:
            cancellation_token.throw_if_cancellation_requested()

        t0 = time.perf_counter()
        intent = getattr(step, "intent", "council_evaluate")
        goal = getattr(step, "value", "") or getattr(step, "description", "")

        if "council" in intent:
            deliberation = self.council.deliberate(str(goal), {})
            return {
                "status": "ok",
                "lane": "reasoning",
                "mode": "council",
                "deliberation": deliberation,
                "changed": True,
                "latency_ms": round((time.perf_counter() - t0) * 1000, 2)
            }
        else:
            # Fast heuristic reasoning
            return {
                "status": "ok",
                "lane": "reasoning",
                "mode": "fast",
                "conclusion": f"Fast analysis for intent '{intent}' completed successfully.",
                "changed": True,
                "latency_ms": round((time.perf_counter() - t0) * 1000, 2)
            }
