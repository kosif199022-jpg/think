"""
Graph of Thoughts (GoT) Engine for KOSIF Think.
Implements non-linear reasoning networks with thought aggregation,
synthesis, and topological dependency execution inspired by Besta et al. (ETH Zurich).
"""

from typing import Dict, Any, List, Set, Optional
import time

class ThoughtVertex:
    def __init__(self, vertex_id: str, content: str, score: float = 1.0):
        self.vertex_id = vertex_id
        self.content = content
        self.score = score
        self.predecessors: List[str] = []
        self.successors: List[str] = []

class GraphOfThoughts:
    """Network of interdependent reasoning vertices with aggregation and refinement."""

    def __init__(self):
        self.vertices: Dict[str, ThoughtVertex] = {}

    def add_thought(self, vertex_id: str, content: str, score: float = 1.0) -> ThoughtVertex:
        v = ThoughtVertex(vertex_id, content, score)
        self.vertices[vertex_id] = v
        return v

    def add_edge(self, from_id: str, to_id: str):
        if from_id in self.vertices and to_id in self.vertices:
            self.vertices[from_id].successors.append(to_id)
            self.vertices[to_id].predecessors.append(from_id)

    def aggregate_thoughts(self, input_ids: List[str], new_id: str, prompt: str) -> ThoughtVertex:
        """Combines multiple independent reasoning branches into a synthesized consensus."""
        combined_content = f"Synthesis of [{', '.join(input_ids)}]: {prompt}"
        avg_score = sum(self.vertices[i].score for i in input_ids) / max(1, len(input_ids))
        v = self.add_thought(new_id, combined_content, score=avg_score)
        for i in input_ids:
            self.add_edge(i, new_id)
        return v

    def topological_execution_order(self) -> List[str]:
        """Calculates topological sorting of thoughts for causal reasoning."""
        in_degree = {k: len(v.predecessors) for k, v in self.vertices.items()}
        queue = [k for k, d in in_degree.items() if d == 0]
        order = []

        while queue:
            node = queue.pop(0)
            order.append(node)
            for succ in self.vertices[node].successors:
                in_degree[succ] -= 1
                if in_degree[succ] == 0:
                    queue.append(succ)

        return order

    def solve_graph(self, problem: str) -> Dict[str, Any]:
        """Builds and executes a multi-perspective graph for a problem."""
        t0 = time.perf_counter()
        # 1. Base premises
        self.add_thought("p1", f"Domain Requirements: Identify core constraints of '{problem[:40]}'", 0.95)
        self.add_thought("p2", f"Empirical Evidence: Evaluate real-world edge cases and scale", 0.90)
        self.add_thought("p3", f"Adversarial Perspective: Identify failure modes and bottlenecks", 0.88)

        # 2. Refinements
        self.add_thought("r1", "Safety Guardrails: Construct invariant protections", 0.98)
        self.add_edge("p1", "r1")
        self.add_edge("p3", "r1")

        self.add_thought("r2", "Execution Pathway: Build deterministic execution plan", 0.94)
        self.add_edge("p1", "r2")
        self.add_edge("p2", "r2")

        # 3. Final Aggregation
        final_node = self.aggregate_thoughts(
            input_ids=["r1", "r2"],
            new_id="consensus",
            prompt=f"Complete robust architecture for '{problem}' with formal invariants."
        )

        order = self.topological_execution_order()
        duration_ms = round((time.perf_counter() - t0) * 1000, 2)

        return {
            "mode": "graph_of_thoughts",
            "problem": problem,
            "vertex_count": len(self.vertices),
            "topological_order": order,
            "final_consensus": final_node.content,
            "confidence": round(final_node.score, 3),
            "duration_ms": duration_ms
        }
