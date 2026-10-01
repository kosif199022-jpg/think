"""
Self-Consistency & Majority Voting Reasoning Engine for KOSIF Think.
Inspired by Google DeepMind (Wang et al. 2022).
Generates diverse reasoning rollouts across independent perspectives,
clusters conclusions, and selects the majority-consensus solution with entropy metrics.
With a model client the samples are real chains of thought (see ``strategies.self_consistency``); without one
the rollouts are fixed perspective templates and the result is marked ``simulated: True``.
"""

from typing import Dict, Any, List, Optional
from collections import Counter
import math
import time

class ReasoningPath:
    """Represents an independent reasoning rollout."""
    def __init__(self, path_id: int, perspective: str, thoughts: List[str], conclusion: str, confidence: float):
        self.path_id = path_id
        self.perspective = perspective
        self.thoughts = thoughts
        self.conclusion = conclusion
        self.confidence = confidence

    def to_dict(self) -> Dict[str, Any]:
        return {
            "path_id": self.path_id,
            "perspective": self.perspective,
            "thoughts": self.thoughts,
            "conclusion": self.conclusion,
            "confidence": self.confidence
        }


class SelfConsistencyEngine:
    """Samples multiple diverse reasoning trajectories and votes on majority consensus."""

    def __init__(self, client: Optional[Any] = None):
        self.client = client

    PERSPECTIVES = [
        "Analytical & First-Principles",
        "Empirical & Historical Heuristics",
        "Safety Invariants & Risk Minimization",
        "Algorithmic Efficiency & Scalability",
        "Edge-Case Adversarial Auditing"
    ]

    def sample_rollouts(self, problem: str, count: int = 5) -> List[ReasoningPath]:
        """Generates diverse reasoning paths across multiple cognitive perspectives."""
        rollouts = []
        clean_problem = problem.strip()

        for idx in range(min(count, len(self.PERSPECTIVES))):
            persp = self.PERSPECTIVES[idx]
            thoughts = [
                f"[{persp}] Analyze core constraints of: '{clean_problem[:50]}'",
                f"[{persp}] Formulate candidate intermediate state representation",
                f"[{persp}] Verify safety invariants and observable post-conditions"
            ]

            # Determine prospective conclusion based on perspective lens
            if "Safety" in persp:
                conclusion = "Enforce strict bounded execution with human confirmation on risk gates."
                conf = 0.98
            elif "Algorithmic" in persp:
                conclusion = "Apply topological sorting and asynchronous concurrent lane execution."
                conf = 0.94
            elif "Edge-Case" in persp:
                conclusion = "Guard with exponential backoff retries and viewport recovery scroll."
                conf = 0.92
            else:
                conclusion = "Decompose into atomic verifiable contracts and execute sequentially."
                conf = 0.95

            rollouts.append(ReasoningPath(idx + 1, persp, thoughts, conclusion, conf))

        return rollouts

    def compute_entropy(self, counts: List[int], total: int) -> float:
        """Calculates Shannon entropy across candidate answers."""
        if total <= 1:
            return 0.0
        entropy = 0.0
        for c in counts:
            if c > 0:
                p = c / total
                entropy -= p * math.log2(p)
        return round(entropy, 3)

    def evaluate_consensus(self, problem: str, num_samples: int = 5) -> Dict[str, Any]:
        """Executes self-consistency voting and returns the winning consensus."""
        if self.client is not None:
            from .strategies import self_consistency
            res = self_consistency(self.client, problem, samples=num_samples)
            res.update({"problem": problem, "total_samples": num_samples, "majority_conclusion": res["answer"],
                        "vote_distribution": res["votes"]})
            return res
        t0 = time.perf_counter()
        rollouts = self.sample_rollouts(problem, count=num_samples)

        # Count conclusion votes
        conclusions = [r.conclusion for r in rollouts]
        vote_counter = Counter(conclusions)
        majority_conclusion, top_votes = vote_counter.most_common(1)[0]

        total_votes = len(rollouts)
        confidence_ratio = round(top_votes / total_votes, 2)
        entropy = self.compute_entropy(list(vote_counter.values()), total_votes)

        duration_ms = round((time.perf_counter() - t0) * 1000, 2)

        return {
            "mode": "self_consistency",
            "simulated": True,
            "problem": problem,
            "total_samples": total_votes,
            "majority_conclusion": majority_conclusion,
            "vote_distribution": dict(vote_counter),
            "consensus_ratio": confidence_ratio,
            "entropy": entropy,
            "unanimous": top_votes == total_votes,
            "duration_ms": duration_ms,
            "rollouts": [r.to_dict() for r in rollouts]
        }
