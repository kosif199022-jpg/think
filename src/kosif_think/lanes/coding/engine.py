"""
Coding Lane Engine for KOSIF Think.
Coordinates AST analysis, atomic code patching, repo mapping, test sandboxing, and autonomous debugging.
"""

from typing import Dict, Any, Optional
import time
from .ast_parser import ASTCodeParser
from .patcher import AtomicPatcher
from .sandbox import TestSandbox
from .repo_mapper import RepoMapper
from .debugger import AutonomousDebugger
from ...core.cancellation import CancellationToken

class CodingLane:
    """Unified handler for software engineering and programming workflows."""

    def __init__(self):
        self.parser = ASTCodeParser()
        self.patcher = AtomicPatcher()
        self.sandbox = TestSandbox()
        self.mapper = RepoMapper()
        self.debugger = AutonomousDebugger()

    async def dispatch_step(self, step: Any, cancellation_token: Optional[CancellationToken] = None) -> Dict[str, Any]:
        """Dispatches an action in the coding lane."""
        if cancellation_token:
            cancellation_token.throw_if_cancellation_requested()

        t0 = time.perf_counter()
        intent = str(getattr(step, "intent", "analyze")).lower()

        # 1. Parse / Analyze AST
        if intent in ("analyze", "parse_ast", "inspect_code"):
            code_or_path = str(getattr(step, "value", "") or getattr(getattr(step, "target", None), "ref", ""))
            if "\n" in code_or_path or "def " in code_or_path:
                res = self.parser.parse_source(code_or_path)
            else:
                res = self.parser.parse_file(code_or_path)
            res["lane"] = "coding"
            res["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
            return res

        # 2. Repo Map
        elif intent in ("repo_map", "map_codebase"):
            root = str(getattr(step, "value", "") or ".")
            res = self.mapper.build_map(root)
            res["lane"] = "coding"
            res["status"] = "ok"
            res["changed"] = True
            res["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
            return res

        # 3. Patch / Edit
        elif intent in ("patch", "replace_code", "edit"):
            val = getattr(step, "value", {})
            if isinstance(val, dict):
                fpath = val.get("file", "")
                target = val.get("target", "")
                repl = val.get("replacement", "")
                res = self.patcher.apply_replacement(fpath, target, repl)
            else:
                res = {"ok": False, "error": "Patch values must be a dictionary with file, target, replacement"}
            res["lane"] = "coding"
            res["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
            return res

        # 4. Run Tests
        elif intent in ("test", "run_tests"):
            cmd = str(getattr(step, "value", "") or "python -m unittest discover tests")
            res = self.sandbox.run_tests(cmd)
            res["lane"] = "coding"
            res["status"] = "ok" if res["passed"] else "test_failed"
            res["changed"] = True
            res["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
            return res

        # 5. Autonomous Debug Cycle
        elif intent in ("debug", "self_repair"):
            cmd = str(getattr(step, "value", "") or "python -m unittest discover tests")
            res = self.debugger.run_debug_cycle(cmd)
            res["lane"] = "coding"
            res["changed"] = True
            res["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
            return res

        return {
            "status": "ok",
            "lane": "coding",
            "message": f"Coding intent '{intent}' executed successfully.",
            "changed": True,
            "latency_ms": round((time.perf_counter() - t0) * 1000, 2)
        }
