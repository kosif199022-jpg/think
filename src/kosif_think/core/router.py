"""
Capability Router: Selects the optimal execution lane and adapter based on intent,
surface health, measured latency, and circuit breaker states across all 7 lanes.
"""

from typing import Dict, Any, List, Optional
import time

class CapabilityRouter:
    """Manages adaptive lane routing and health metrics across 7 lanes."""

    def __init__(self):
        self._lane_health: Dict[str, Dict[str, Any]] = {
            "reasoning": {"available": True, "latency_ms": 15.0, "failure_count": 0, "circuit_open": False},
            "coding": {"available": True, "latency_ms": 20.0, "failure_count": 0, "circuit_open": False},
            "graphics": {"available": True, "latency_ms": 25.0, "failure_count": 0, "circuit_open": False},
            "computer": {"available": True, "latency_ms": 35.0, "failure_count": 0, "circuit_open": False},
            "browser": {"available": True, "latency_ms": 45.0, "failure_count": 0, "circuit_open": False},
            "whatsapp": {"available": True, "latency_ms": 60.0, "failure_count": 0, "circuit_open": False},
            "ios": {"available": True, "latency_ms": 40.0, "failure_count": 0, "circuit_open": False},
            "voice": {"available": True, "latency_ms": 25.0, "failure_count": 0, "circuit_open": False},
        }

    def route_step(self, lane_preference: str, intent: str) -> str:
        """Determines the active lane, falling back if a circuit is open."""
        lane = lane_preference.lower()
        health = self._lane_health.get(lane, {"available": True, "circuit_open": False})

        if health.get("available") and not health.get("circuit_open"):
            return lane

        # Fallback hierarchy
        if lane == "browser":
            return "computer"
        elif lane == "whatsapp":
            return "browser"
        elif lane == "coding":
            return "computer"
        elif lane == "graphics":
            return "coding"
        elif lane == "ios":
            return "computer"
        elif lane == "voice":
            return "reasoning"
        return "reasoning"

    def record_lane_metric(self, lane: str, success: bool, latency_ms: float):
        """Updates exponential health metrics for a lane."""
        h = self._lane_health.setdefault(lane, {"available": True, "latency_ms": 50.0, "failure_count": 0, "circuit_open": False})
        if success:
            h["failure_count"] = max(0, h["failure_count"] - 1)
            h["latency_ms"] = (h["latency_ms"] * 0.8) + (latency_ms * 0.2)
        else:
            h["failure_count"] += 1
            if h["failure_count"] >= 3:
                h["circuit_open"] = True

    def reset_circuit(self, lane: str):
        if lane in self._lane_health:
            self._lane_health[lane]["circuit_open"] = False
            self._lane_health[lane]["failure_count"] = 0
