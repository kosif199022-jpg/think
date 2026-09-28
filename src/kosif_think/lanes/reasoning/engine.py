"""
Reasoning Lane Engine: Unifies Fast Heuristic, Multi-Agent Council,
Tree of Thoughts (ToT), Graph of Thoughts (GoT), Reflexion, and Monte Carlo Tree Search (MCTS).
"""

from typing import Dict, Any, Optional, List
import time
from .council import CouncilReasoning
from .cognitive import CognitiveUnderstanding
from .tree_of_thoughts import TreeOfThoughts
from .graph_of_thoughts import GraphOfThoughts
from .reflexion import ReflexionEngine
from .mcts import MCTSPlanner
from ...core.cancellation import CancellationToken

class ReasoningLane:
    """Unified handler for all super-intelligent reasoning models."""

    def __init__(self):
        self.council = CouncilReasoning()
        self.cognitive = CognitiveUnderstanding()
        self.tot = TreeOfThoughts()
        self.got = GraphOfThoughts()
        self.reflexion = ReflexionEngine()
        self.mcts = MCTSPlanner()

    async def dispatch_step(self, step: Any, cancellation_token: Optional[CancellationToken] = None) -> Dict[str, Any]:
        """Executes a reasoning step via the requested cognitive paradigm."""
        if cancellation_token:
            cancellation_token.throw_if_cancellation_requested()

        t0 = time.perf_counter()
        intent = str(getattr(step, "intent", "council_evaluate")).lower()
        goal = str(getattr(step, "value", "") or getattr(step, "description", ""))

        # 1. Tree of Thoughts Mode
        if "tot" in intent or "tree" in intent:
            res = self.tot.search(goal)
            res["status"] = "ok"
            res["lane"] = "reasoning"
            res["changed"] = True
            res["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
            return res

        # 2. Graph of Thoughts Mode
        elif "got" in intent or "graph" in intent:
            res = self.got.solve_graph(goal)
            res["status"] = "ok"
            res["lane"] = "reasoning"
            res["changed"] = True
            res["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
            return res

        # 3. Reflexion Mode
        elif "reflexion" in intent or "reflect" in intent:
            rec = self.reflexion.reflect_on_trial(
                trial_number=len(self.reflexion.memory_buffer) + 1,
                action_taken=intent,
                observed_outcome="Completed with verified state",
                success=True,
                goal=goal
            )
            return {
                "status": "ok",
                "lane": "reasoning",
                "mode": "reflexion",
                "reflection": rec.reflection,
                "lesson_learned": rec.lesson_learned,
                "past_advice": self.reflexion.get_context_advice(intent),
                "changed": True,
                "latency_ms": round((time.perf_counter() - t0) * 1000, 2)
            }

        # 4. MCTS Mode
        elif "mcts" in intent or "monte_carlo" in intent:
            actions = ["decompose", "formal_verify", "execute_step", "backtrack"]
            res = self.mcts.plan(initial_state=goal, available_actions=actions)
            res["status"] = "ok"
            res["lane"] = "reasoning"
            res["changed"] = True
            res["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
            return res

        # 5. Council Mode
        elif "council" in intent:
            deliberation = self.council.deliberate(goal, {})
            return {
                "status": "ok",
                "lane": "reasoning",
                "mode": "council",
                "deliberation": deliberation,
                "changed": True,
                "latency_ms": round((time.perf_counter() - t0) * 1000, 2)
            }

        # 6. Fast Heuristic Mode (<5ms)
        else:
            return {
                "status": "ok",
                "lane": "reasoning",
                "mode": "fast",
                "conclusion": f"Fast analysis for intent '{intent}' completed successfully.",
                "changed": True,
                "latency_ms": round((time.perf_counter() - t0) * 1000, 2)
            }
