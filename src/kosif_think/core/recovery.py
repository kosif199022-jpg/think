"""
Recovery Engine & Circuit Breaker: Detects action loops, recovers from stuck states,
and breaks repetitive failure cycles autonomously.
"""

import time
import logging
from typing import Dict, Any, List, Optional
from ..config import CIRCUIT_COOLDOWN_SEC, MAX_CONSECUTIVE_FAILURES

logger = logging.getLogger("kosif_think.recovery")

class CircuitBreaker:
    """Protects execution routes from cascading failures."""

    def __init__(self, failure_threshold: int = MAX_CONSECUTIVE_FAILURES, cooldown: float = CIRCUIT_COOLDOWN_SEC):
        self.failure_threshold = failure_threshold
        self.cooldown = cooldown
        self.failure_count = 0
        self.open_until: float = 0.0

    @property
    def is_open(self) -> bool:
        if self.open_until > time.time():
            return True
        if self.open_until > 0.0:
            # Cooldown passed, half-open
            self.open_until = 0.0
            self.failure_count = 0
        return False

    def record_success(self):
        self.failure_count = 0
        self.open_until = 0.0

    def record_failure(self):
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.open_until = time.time() + self.cooldown
            logger.warning(f"Circuit breaker tripped open for {self.cooldown} seconds.")


class RecoveryEngine:
    """Diagnoses stuck loops and calculates recovery actions."""

    def __init__(self):
        self._action_history: List[Dict[str, Any]] = []

    def record_action(self, action: Dict[str, Any]):
        self._action_history.append(action)
        if len(self._action_history) > 30:
            self._action_history.pop(0)

    def detect_action_loop(self) -> bool:
        """Detects if the last 3 click actions targeted the exact same element with no progress."""
        if len(self._action_history) < 3:
            return False

        recent = self._action_history[-3:]
        clicks = [a.get("target") for a in recent if a.get("action") == "click"]
        if len(clicks) == 3 and len(set(clicks)) == 1:
            return True

        return False

    def plan_recovery_action(self, current_url: str, goal: str) -> Dict[str, Any]:
        """Provides an autonomous recovery recommendation."""
        # Check if page is on a bot-wall
        if "google.com/sorry" in current_url:
            return {
                "strategy": "reroute_search_engine",
                "recommended_action": "navigate",
                "target_url": f"https://www.bing.com/search?q={goal}",
                "reason": "Google Sorry rate limit detected. Rerouting to clean alternative search engine."
            }

        # Standard loop recovery: smooth scroll and refresh action graph
        return {
            "strategy": "scroll_and_reindex",
            "recommended_action": "scroll",
            "amount": 500,
            "reason": "Repeated click detected with zero progress. Scrolling viewport to reveal fresh targets."
        }
