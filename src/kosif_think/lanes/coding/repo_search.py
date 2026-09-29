"""
High-Speed Workspace & Repository Search Engine for KOSIF Think.
Inspired by Ripgrep (rg) and Git Grep.
Provides fast multi-threaded file search, regex content matching with context lines,
symbol definition indexing, and directory tree visualization.
Zero external dependencies. Pure Python.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import re
import time

IGNORE_DIRS = {
    ".git", "__pycache__", ".venv", "venv", "node_modules",
    ".idea", ".vscode", "dist", "build", ".eggs", ".system_generated"
}

class RepoSearchEngine:
    """Workspace search providing regex grep, symbol indexing, and file path discovery."""

    def search_content(
        self,
        root_dir: str,
        pattern: str,
        file_ext: Optional[str] = None,
        context_lines: int = 1,
        max_matches: int = 50
    ) -> Dict[str, Any]:
        """Searches file contents for regex pattern and returns matches with context."""
        t0 = time.perf_counter()
        regex = re.compile(pattern, re.IGNORECASE)
        base_path = Path(root_dir).resolve()
        matches = []
        files_scanned = 0

        for path in base_path.rglob("*"):
            if not path.is_file():
                continue
            if any(ign in path.parts for ign in IGNORE_DIRS):
                continue
            if file_ext and not path.name.endswith(file_ext):
                continue

            files_scanned += 1
            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
                lines = content.splitlines()
                for i, line in enumerate(lines):
                    if regex.search(line):
                        start_idx = max(0, i - context_lines)
                        end_idx = min(len(lines), i + context_lines + 1)
                        context = [
                            {"line_num": idx + 1, "text": lines[idx], "is_match": idx == i}
                            for idx in range(start_idx, end_idx)
                        ]
                        rel_path = str(path.relative_to(base_path)).replace("\\", "/")
                        matches.append({
                            "file": rel_path,
                            "line": i + 1,
                            "matched_text": line.strip(),
                            "context": context
                        })
                        if len(matches) >= max_matches:
                            break
            except Exception:
                continue

            if len(matches) >= max_matches:
                break

        duration_ms = round((time.perf_counter() - t0) * 1000, 2)
        return {
            "query": pattern,
            "root_dir": str(base_path),
            "files_scanned": files_scanned,
            "total_matches": len(matches),
            "matches": matches,
            "duration_ms": duration_ms
        }

    def find_symbols(self, root_dir: str, symbol_query: str) -> Dict[str, Any]:
        """Locates class, function, and async definitions matching query."""
        pattern = rf"^\s*(?:def|class|async\s+def)\s+([a-zA-Z0-9_]*{re.escape(symbol_query)}[a-zA-Z0-9_]*)"
        return self.search_content(root_dir, pattern, file_ext=".py", context_lines=0)

    def tree(self, root_dir: str, max_depth: int = 3) -> str:
        """Generates an ASCII directory tree of the workspace."""
        base_path = Path(root_dir).resolve()
        lines = [f"📁 {base_path.name}/"]

        def _walk(curr: Path, prefix: str, depth: int):
            if depth > max_depth:
                return
            items = sorted(
                [p for p in curr.iterdir() if p.name not in IGNORE_DIRS],
                key=lambda x: (not x.is_dir(), x.name.lower())
            )
            count = len(items)
            for idx, item in enumerate(items):
                is_last = idx == count - 1
                connector = "└── " if is_last else "├── "
                sub_prefix = "    " if is_last else "│   "
                if item.is_dir():
                    lines.append(f"{prefix}{connector}📁 {item.name}/")
                    _walk(item, prefix + sub_prefix, depth + 1)
                else:
                    lines.append(f"{prefix}{connector}📄 {item.name}")

        _walk(base_path, "", 1)
        return "\n".join(lines)
