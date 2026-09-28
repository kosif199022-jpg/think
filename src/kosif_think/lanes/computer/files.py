"""
File Operations: Safe read/write, directory validation, and export packaging.
"""

from pathlib import Path
from typing import Dict, Any, Optional

class FileControl:
    """Manages file interactions safely."""

    def read_text(self, file_path: str, max_chars: int = 20000) -> Dict[str, Any]:
        p = Path(file_path)
        if not p.exists():
            return {"status": "error", "error": f"File {file_path} not found"}
        try:
            content = p.read_text(encoding="utf-8", errors="ignore")
            return {"status": "ok", "path": str(p), "size_bytes": p.stat().st_size, "content": content[:max_chars]}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def write_text(self, file_path: str, content: str) -> Dict[str, Any]:
        p = Path(file_path)
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
            return {"status": "ok", "path": str(p), "size_bytes": len(content.encode("utf-8")), "changed": True}
        except Exception as e:
            return {"status": "error", "error": str(e), "changed": False}
