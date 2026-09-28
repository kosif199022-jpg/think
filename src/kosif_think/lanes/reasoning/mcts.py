"""
Monte Carlo Tree Search (MCTS) Engine for KOSIF Think.
Provides decision exploration for complex multi-step reasoning with UCB1 balance.
"""

import math
import random
import time
from typing import Dict, Any, List, Optional

class MCTSNode:
    def __init__(self, state_desc: str, parent: Optional["MCTSNode"] = None, action_taken: Optional[str] = None):
        self.state_desc = state_desc
        self.parent = parent
        self.action_taken = action_taken
        self.children: List["MCTSNode"] = []
        self.visits = 0
        self.value = 0.0

    @property
    def ucb1(self) -> float:
        if self.visits == 0:
            return float("inf")
        c = 1.414  # Exploration constant
        return (self.value / self.visits) + c * math.sqrt(math.log(self.parent.visits) / self.visits)

class MCTSPlanner:
    """Plans optimal sequence of strategic actions using Monte Carlo simulations."""

    def __init__(self, simulations: int = 100):
        self.simulations = simulations

    def plan(self, initial_state: str, available_actions: List[str]) -> Dict[str, Any]:
        t0 = time.perf_counter()
        root = MCTSNode(state_desc=initial_state)

        for _ in range(self.simulations):
            node = root

            # 1. Selection
            while node.children:
                node = max(node.children, key=lambda c: c.ucb1)

            # 2. Expansion
            if node.visits > 0 or node == root:
                for act in available_actions:
                    child = MCTSNode(state_desc=f"{node.state_desc} + [{act}]", parent=node, action_taken=act)
                    node.children.append(child)
                if node.children:
                    node = node.children[0]

            # 3. Simulation (Rollout)
            # Evaluate heuristic score
            score = 0.5 + 0.1 * random.random()
            if "verify" in node.state_desc.lower():
                score += 0.3
            if "fail" in node.state_desc.lower():
                score -= 0.4
            score = max(0.0, min(1.0, score))

            # 4. Backpropagation
            curr: Optional[MCTSNode] = node
            while curr:
                curr.visits += 1
                curr.value += score
                curr = curr.parent

        # Best action from root
        best_child = max(root.children, key=lambda c: c.visits) if root.children else None
        duration_ms = round((time.perf_counter() - t0) * 1000, 2)

        return {
            "mode": "mcts",
            "initial_state": initial_state,
            "simulations_run": self.simulations,
            "best_action": best_child.action_taken if best_child else (available_actions[0] if available_actions else None),
            "expected_reward": round(best_child.value / max(1, best_child.visits), 3) if best_child else 0.5,
            "duration_ms": duration_ms
        }
