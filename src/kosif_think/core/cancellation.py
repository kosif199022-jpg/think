"""
Cancellation token mechanism for safe interruption before consequential actions.
"""

import threading
from typing import Optional

class OperationCancelledException(Exception):
    """Raised when an operation is cancelled via CancellationToken."""
    pass

class CancellationToken:
    """Read-only cancellation token inspected by runners and lanes."""

    def __init__(self, source: Optional["CancellationSource"] = None):
        self._source = source

    @property
    def is_cancellation_requested(self) -> bool:
        if self._source:
            return self._source.is_cancellation_requested
        return False

    def throw_if_cancellation_requested(self):
        if self.is_cancellation_requested:
            raise OperationCancelledException("Operation was cancelled before the next side effect.")


class CancellationSource:
    """Manages cancellation state and signals tokens."""

    def __init__(self):
        self._cancelled = False
        self._lock = threading.Lock()

    @property
    def is_cancellation_requested(self) -> bool:
        with self._lock:
            return self._cancelled

    @property
    def token(self) -> CancellationToken:
        return CancellationToken(self)

    def cancel(self):
        with self._lock:
            self._cancelled = True

    def reset(self):
        with self._lock:
            self._cancelled = False
