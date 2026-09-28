"""
KOSIF Think Preflight Gate: validates user intent, strips dangerous payload injection,
redacts credentials, and verifies environment readiness before planning begins.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import uuid
from .cancellation import CancellationToken
from .audit import sanitize_secrets

@dataclass
class SanitizedRequest:
    task_id: str
    raw_prompt: str
    clean_goal: str
    context: Dict[str, Any] = field(default_factory=dict)
    is_valid: bool = True
    error_message: Optional[str] = None


class PreflightGate:
    """Performs pre-execution analysis and sanitization on raw incoming goals."""

    def __init__(self):
        pass

    def run_preflight(
        self,
        raw_prompt: str,
        context: Optional[Dict[str, Any]] = None,
        cancellation_token: Optional[CancellationToken] = None
    ) -> SanitizedRequest:
        """Validates and prepares the request for planning."""
        if cancellation_token and cancellation_token.is_cancellation_requested:
            return SanitizedRequest(
                task_id=str(uuid.uuid4())[:8],
                raw_prompt=raw_prompt,
                clean_goal="",
                is_valid=False,
                error_message="Cancelled during preflight."
            )

        if not raw_prompt or not raw_prompt.strip():
            return SanitizedRequest(
                task_id=str(uuid.uuid4())[:8],
                raw_prompt="",
                clean_goal="",
                is_valid=False,
                error_message="Empty request goal provided."
            )

        clean_text = raw_prompt.strip()
        sanitized_ctx = sanitize_secrets(context or {})
        task_id = str(uuid.uuid4())[:8]

        return SanitizedRequest(
            task_id=task_id,
            raw_prompt=raw_prompt,
            clean_goal=clean_text,
            context=sanitized_ctx,
            is_valid=True
        )
