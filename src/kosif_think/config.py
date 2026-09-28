"""
Configuration and runtime environment settings for KOSIF Think.
"""

import os
from pathlib import Path
from typing import Dict, Any

# Root data and KOSIF directories
DEFAULT_DATA_DIR = Path.home() / "Documents" / "KOSIF Chrome Control" / "data"
THINK_DATA_DIR = Path(os.environ.get("KOSIF_THINK_DATA", str(DEFAULT_DATA_DIR / "think")))
THINK_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Token files and audit paths
TRACE_FILE = THINK_DATA_DIR / "think_audit.jsonl"
MEMORY_DB = THINK_DATA_DIR / "think_memory.json"
TOKEN_FILE = THINK_DATA_DIR / "think_token.txt"

# Default live endpoints
DEFAULT_LIVE_URL = os.environ.get("KOSIF_LIVE_URL", "http://127.0.0.1:49325/command")
DEFAULT_CHROME_RUN_URL = os.environ.get("KOSIF_RUN_URL", "http://127.0.0.1:18766/run")
DEFAULT_CHROME_HEALTH_URL = os.environ.get("KOSIF_CHROME_HEALTH", "http://127.0.0.1:18766/health")
DEFAULT_JEV_REMOTE_URL = os.environ.get("KOSIF_JEV_URL", "http://127.0.0.1:8888")

# Unified Server Port
DEFAULT_SERVER_PORT = int(os.environ.get("KOSIF_THINK_PORT", "49400"))
DEFAULT_SERVER_HOST = os.environ.get("KOSIF_THINK_HOST", "127.0.0.1")

# Safety thresholds
MAX_CONSECUTIVE_FAILURES = 3
DEFAULT_STEP_TIMEOUT_MS = 15000
CIRCUIT_COOLDOWN_SEC = 10.0

def get_auth_token() -> str:
    """Retrieves or creates a secure local token for IPC/Server authentication."""
    if TOKEN_FILE.exists():
        val = TOKEN_FILE.read_text(encoding="utf-8").strip()
        if val:
            return val
    import secrets
    tok = secrets.token_hex(32)
    TOKEN_FILE.write_text(tok, encoding="utf-8")
    return tok
