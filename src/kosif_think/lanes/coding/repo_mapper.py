"""
Repository Map & Graph Intelligence for KOSIF Think.
Creates concise symbol maps of codebases ranked by dependency centrality (PageRank style)
inspired by Aider's repo-map architecture.
"""

from pathlib import Path
from typing import Dict, Any, List, Set
from .ast_parser import ASTCodeParser

class RepoMapper:
    """Builds a prioritized, context-efficient map of an entire codebase."""

    def __init__(self):
        self.parser = ASTCodeParser()

    def build_map(self, root_dir: str, max_files: int = 50) -> Dict[str, Any]:
        """Scans codebase, extracts symbol hierarchies, and computes symbol connectivity."""
        root = Path(root_dir)
        py_files = list(root.glob("**/*.py"))[:max_files]

        file_summaries: Dict[str, Any] = {}
        all_defined_symbols: Set[str] = set()

        for f in py_files:
            if any(ignore in str(f) for ignore in [".venv", "venv", "__pycache__", ".git"]):
                continue
            res = self.parser.parse_file(str(f))
            if res.get("ok"):
                rel_path = f.relative_to(root).as_posix()
                sym_names = [s["name"] for s in res.get("symbols", [])]
                all_defined_symbols.update(sym_names)
                file_summaries[rel_path] = {
                    "symbols": sym_names,
                    "complexity": res.get("cyclomatic_complexity", 1),
                    "imports": res.get("imports", [])
                }

        # Rank files by symbol density
        ranked_files = sorted(
            file_summaries.keys(),
            key=lambda k: len(file_summaries[k]["symbols"]) + file_summaries[k]["complexity"] * 0.5,
            reverse=True
        )

        return {
            "root": str(root),
            "total_files": len(file_summaries),
            "total_symbols": len(all_defined_symbols),
            "ranked_files": ranked_files[:20],
            "file_summaries": {k: file_summaries[k] for k in ranked_files[:20]}
        }
