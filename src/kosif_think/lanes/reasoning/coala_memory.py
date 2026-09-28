"""
CoALA Cognitive Architecture Memory System for KOSIF Think.
Implements the 4-tier cognitive memory model (Working, Episodic, Semantic, Procedural)
inspired by the Princeton/CMU/DeepMind CoALA framework (Sumers et al.).
"""

import time
import json
from typing import Dict, Any, List, Optional
from pathlib import Path

class CoALAMemorySystem:
    """Multi-tiered human-like cognitive memory for language agents."""

    def __init__(self):
        # 1. Working Memory (Active focus and transient scratchpad)
        self.working_memory: Dict[str, Any] = {
            "current_goal": None,
            "active_step": 0,
            "scratchpad": [],
            "focus_entities": []
        }

        # 2. Episodic Memory (Autobiographical history of actions and outcomes)
        self.episodic_memory: List[Dict[str, Any]] = []

        # 3. Semantic Memory (Factual knowledge, schemas, invariants)
        self.semantic_memory: Dict[str, str] = {
            "invariants.safety": "High-risk actions (financial, deletion, 2FA) require human confirmation.",
            "invariants.verification": "Observable real-world proof (DOM, file, process) required before completion.",
            "invariants.recovery": "Action loops must be broken via viewport scrolling or strategy rerouting."
        }

        # 4. Procedural Memory (How-to knowledge, executable skills, recipes)
        self.procedural_memory: Dict[str, Dict[str, Any]] = {
            "browser.search": {"steps": ["navigate_engine", "type_query", "press_enter", "verify_results"]},
            "computer.app": {"steps": ["verify_installed", "launch_process", "wait_for_window"]},
            "coding.patch": {"steps": ["parse_ast", "find_unique_context", "apply_diff", "run_sandbox_tests"]},
            "ios.shortcut": {"steps": ["resolve_scheme", "enqueue_command", "wait_for_ios_ack"]}
        }

    def set_working_focus(self, goal: str, entities: Optional[List[str]] = None):
        """Updates working memory focus."""
        self.working_memory["current_goal"] = goal
        self.working_memory["focus_entities"] = entities or []
        self.working_memory["scratchpad"].append(f"Focus set to: {goal}")

    def append_scratchpad(self, note: str):
        self.working_memory["scratchpad"].append(note)

    def record_episode(self, goal: str, actions_taken: List[str], outcome: str, success: bool):
        """Consolidates completed task into episodic memory."""
        episode = {
            "timestamp": time.time(),
            "goal": goal,
            "actions": actions_taken,
            "outcome": outcome,
            "success": success
        }
        self.episodic_memory.append(episode)
        if len(self.episodic_memory) > 200:
            self.episodic_memory.pop(0)

    def learn_semantic_fact(self, key: str, fact: str):
        """Stores a persistent fact into semantic memory."""
        self.semantic_memory[key] = fact

    def register_procedure(self, name: str, steps: List[str]):
        """Registers a reusable procedure into procedural memory."""
        self.procedural_memory[name] = {"steps": steps, "created_at": time.time()}

    def retrieve_relevant_context(self, query: str) -> Dict[str, Any]:
        """Performs associative retrieval across all 4 memory tiers."""
        relevant_episodes = [
            e for e in self.episodic_memory[-5:]
            if any(w.lower() in e["goal"].lower() for w in query.split() if len(w) > 3)
        ]
        relevant_semantics = {
            k: v for k, v in self.semantic_memory.items()
            if any(w.lower() in k.lower() or w.lower() in v.lower() for w in query.split() if len(w) > 3)
        }
        matched_procedures = {
            k: v for k, v in self.procedural_memory.items()
            if any(w.lower() in k.lower() for w in query.split() if len(w) > 3)
        }

        return {
            "working_memory": self.working_memory,
            "relevant_episodes": relevant_episodes,
            "relevant_semantics": relevant_semantics,
            "matched_procedures": matched_procedures
        }
