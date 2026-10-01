"""
Tree of Thoughts (ToT) Engine for KOSIF Think.
Implements multi-branch search, self-evaluation, pruning, and backtracking
inspired by the Princeton/DeepMind Tree of Thoughts paradigm.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
import time
import math

@dataclass
class ThoughtNode:
    thought_id: str
    text: str
    depth: int
    score: float = 0.0
    parent: Optional["ThoughtNode"] = None
    children: List["ThoughtNode"] = field(default_factory=list)
    state: Dict[str, Any] = field(default_factory=dict)
    is_terminal: bool = False

    def path(self) -> List[str]:
        curr = self
        res = []
        while curr:
            res.append(curr.text)
            curr = curr.parent
        return list(reversed(res))


class TreeOfThoughts:
    """Explores problem spaces via branched tree search, evaluation, and pruning."""

    def __init__(self, branching_factor: int = 3, max_depth: int = 3, prune_threshold: float = 0.4,
                 client: Optional[Any] = None):
        self.client = client
        self.branching_factor = branching_factor
        self.max_depth = max_depth
        self.prune_threshold = prune_threshold

    def search(
        self,
        problem: str,
        generator_fn: Optional[Callable[[str, int], List[str]]] = None,
        evaluator_fn: Optional[Callable[[str, List[str]], float]] = None
    ) -> Dict[str, Any]:
        """Runs a tree-of-thoughts search to find the optimal path to solve a problem.

        With a model client and no custom generator/evaluator this is the propose/value BFS of Yao et al.
        (see ``strategies.tree_of_thoughts``). Otherwise the given or built-in template functions are used.
        """
        if self.client is not None and generator_fn is None and evaluator_fn is None:
            from .strategies import tree_of_thoughts
            return tree_of_thoughts(self.client, problem, breadth=self.branching_factor, depth=self.max_depth,
                                    beam=self.branching_factor)
        simulated = generator_fn is None
        t0 = time.perf_counter()
        root = ThoughtNode(thought_id="root", text=f"Problem: {problem}", depth=0, score=1.0)

        # Default generator if none provided
        if not generator_fn:
            def default_gen(node_text: str, depth: int) -> List[str]:
                if depth == 1:
                    return [
                        f"Approach A (Decomposition): Break '{problem[:40]}' into isolated sub-problems.",
                        f"Approach B (Analogy): Map problem to standard algorithmic pattern.",
                        f"Approach C (Constraint Satisfaction): Establish hard invariants and prune invalid states."
                    ]
                elif depth == 2:
                    return [
                        f"Step 2.1: Formalize state transitions and edge cases for {node_text[:30]}.",
                        f"Step 2.2: Optimize resource complexity and verify feasibility."
                    ]
                else:
                    return [
                        f"Synthesis & Verification: Produce verifiable solution and validate observable outcomes."
                    ]
            generator_fn = default_gen

        # Default evaluator if none provided
        if not evaluator_fn:
            def default_eval(thought: str, path: List[str]) -> float:
                score = 0.75
                if "Constraint" in thought or "Optimize" in thought or "Verification" in thought:
                    score += 0.20
                if "Decomposition" in thought:
                    score += 0.15
                return min(1.0, score)
            evaluator_fn = default_eval

        # Breadth-first / beam search over thoughts
        active_nodes = [root]
        best_leaf: Optional[ThoughtNode] = None
        best_score: float = -1.0
        total_nodes = 1

        for depth in range(1, self.max_depth + 1):
            next_nodes = []
            for parent in active_nodes:
                candidate_texts = generator_fn(parent.text, depth)
                for i, c_text in enumerate(candidate_texts[:self.branching_factor]):
                    path_so_far = parent.path() + [c_text]
                    score = evaluator_fn(c_text, path_so_far)
                    child = ThoughtNode(
                        thought_id=f"d{depth}_{i}",
                        text=c_text,
                        depth=depth,
                        score=score,
                        parent=parent,
                        is_terminal=(depth == self.max_depth)
                    )
                    parent.children.append(child)
                    total_nodes += 1

                    if score >= self.prune_threshold:
                        next_nodes.append(child)

                    if child.is_terminal and score > best_score:
                        best_score = score
                        best_leaf = child

            # Keep top-k beam
            next_nodes.sort(key=lambda n: n.score, reverse=True)
            active_nodes = next_nodes[:self.branching_factor]
            if not active_nodes:
                break

        if not best_leaf and active_nodes:
            best_leaf = active_nodes[0]
            best_score = best_leaf.score

        optimal_path = best_leaf.path() if best_leaf else [root.text]
        duration_ms = round((time.perf_counter() - t0) * 1000, 2)

        return {
            "mode": "tree_of_thoughts",
            "simulated": simulated,
            "problem": problem,
            "best_score": round(best_score, 3),
            "total_thoughts_explored": total_nodes,
            "optimal_reasoning_path": optimal_path,
            "duration_ms": duration_ms
        }
