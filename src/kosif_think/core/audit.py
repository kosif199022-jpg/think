"""
Structured audit logger and trace recorder for KOSIF Think.
"""

import json
import logging
import re
import threading
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from ..config import TRACE_FILE

logger = logging.getLogger("kosif_think.audit")

SECRET_PATTERN = re.compile(
    r"(bearer\s+[a-zA-Z0-9_\-\.]{15,}|ghp_[a-zA-Z0-9]{20,}|gho_[a-zA-Z0-9]{20,}|sk-[a-zA-Z0-9_\-]{20,}|token['\":\s=]+[a-zA-Z0-9_\-]{16,}|password['\":\s=]+[^\s,'\"]+)",
    re.IGNORECASE
)

def sanitize_secrets(obj: Any) -> Any:
    """Recursively redacts API keys, passwords, and tokens from dictionaries/strings."""
    if isinstance(obj, str):
        return SECRET_PATTERN.sub("[REDACTED_SECRET]", obj)
    elif isinstance(obj, dict):
        cleaned = {}
        for k, v in obj.items():
            if any(s in k.lower() for s in ["token", "secret", "password", "api_key", "auth"]):
                cleaned[k] = "[REDACTED_SECRET]"
            else:
                cleaned[k] = sanitize_secrets(v)
        return cleaned
    elif isinstance(obj, list):
        return [sanitize_secrets(item) for item in obj]
    return obj


class AuditLogger:
    """Thread-safe event auditor logging all system-level state transitions."""

    def __init__(self, log_path: Path = TRACE_FILE):
        self.log_path = log_path
        self._lock = threading.Lock()
        self._recent_events: List[Dict[str, Any]] = []

    def record_event(
        self,
        event_type: str,
        task_id: str,
        lane: str,
        details: Dict[str, Any],
        status: str = "ok"
    ) -> Dict[str, Any]:
        """Records a timestamped audit entry, sanitizing any sensitive parameters."""
        sanitized_details = sanitize_secrets(details)
        entry = {
            "timestamp": time.time(),
            "iso_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "task_id": task_id,
            "lane": lane,
            "event": event_type,
            "status": status,
            "details": sanitized_details
        }

        with self._lock:
            self._recent_events.append(entry)
            if len(self._recent_events) > 500:
                self._recent_events.pop(0)

            try:
                self.log_path.parent.mkdir(parents=True, exist_ok=True)
                with self.log_path.open("a", encoding="utf-8") as f:
                    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            except Exception as e:
                logger.error(f"Failed to append to audit trace: {e}")

        return entry

    def get_recent_events(self, limit: int = 50, task_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Returns recent events from memory or disc."""
        with self._lock:
            if task_id:
                filtered = [e for e in self._recent_events if e.get("task_id") == task_id]
                return filtered[-limit:]
            return self._recent_events[-limit:]
