"""
Memory Engine: Manages short-term working context snapshots, active tabs,
and persistent episodic memory across execution tasks.
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from ..config import MEMORY_DB

class MemoryEngine:
    """Stores task execution context and learned element priors."""

    def __init__(self, storage_path: Path = MEMORY_DB):
        self.storage_path = storage_path
        self._working_memory: Dict[str, Any] = {}
        self._load()

    def _load(self):
        if self.storage_path.exists():
            try:
                self._working_memory = json.loads(self.storage_path.read_text(encoding="utf-8"))
            except Exception:
                self._working_memory = {}

    def _persist(self):
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            self.storage_path.write_text(json.dumps(self._working_memory, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass

    def store_context(self, key: str, value: Any):
        self._working_memory[key] = {
            "value": value,
            "updated_at": time.time()
        }
        self._persist()

    def get_context(self, key: str, default: Any = None) -> Any:
        entry = self._working_memory.get(key)
        if entry:
            return entry.get("value")
        return default

    def record_task_summary(self, task_id: str, goal: str, success: bool, steps_count: int):
        tasks = self._working_memory.setdefault("recent_tasks", [])
        tasks.append({
            "task_id": task_id,
            "goal": goal,
            "success": success,
            "steps": steps_count,
            "timestamp": time.time()
        })
        if len(tasks) > 100:
            tasks.pop(0)
        self._persist()
