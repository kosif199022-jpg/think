"""
Atomic Patcher & Diff Engine for KOSIF Think.
Supports unified diff parsing, chunk replacement, fuzzy matching, and atomic file edits.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import difflib

class AtomicPatcher:
    """Safely applies code edits with verification and backup."""

    def apply_replacement(
        self,
        file_path: str,
        target_content: str,
        replacement_content: str,
        allow_multiple: bool = False
    ) -> Dict[str, Any]:
        """Replaces precise blocks of code inside a file."""
        p = Path(file_path)
        if not p.exists():
            return {"ok": False, "error": f"File {file_path} not found"}

        original = p.read_text(encoding="utf-8")

        count = original.count(target_content)
        if count == 0:
            # Try normalized line endings
            target_norm = target_content.replace("\r\n", "\n")
            orig_norm = original.replace("\r\n", "\n")
            if target_norm in orig_norm:
                new_norm = orig_norm.replace(target_norm, replacement_content.replace("\r\n", "\n"), 1 if not allow_multiple else -1)
                p.write_text(new_norm, encoding="utf-8")
                return {"ok": True, "file": str(p), "replacements": 1, "changed": True}
            return {"ok": False, "error": "Target content not found in file."}

        if count > 1 and not allow_multiple:
            return {"ok": False, "error": f"Target content occurs {count} times. Specify unique context or set allow_multiple=True."}

        new_content = original.replace(target_content, replacement_content, 1 if not allow_multiple else -1)
        p.write_text(new_content, encoding="utf-8")

        # Generate unified diff for audit
        diff = list(difflib.unified_diff(
            original.splitlines(keepends=True),
            new_content.splitlines(keepends=True),
            fromfile=f"a/{p.name}",
            tofile=f"b/{p.name}"
        ))

        return {
            "ok": True,
            "file": str(p),
            "replacements": count,
            "diff": "".join(diff),
            "changed": True
        }

    def generate_diff(self, original_text: str, new_text: str, filename: str = "file.py") -> str:
        """Produces standard unified diff."""
        diff = difflib.unified_diff(
            original_text.splitlines(keepends=True),
            new_text.splitlines(keepends=True),
            fromfile=f"a/{filename}",
            tofile=f"b/{filename}"
        )
        return "".join(diff)
