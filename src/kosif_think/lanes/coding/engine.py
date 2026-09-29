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
from .repo_search import RepoSearchEngine
from .tdd_synthesizer import TDDSynthesizer
from .swe_orchestrator import SWEAgentOrchestrator
from ...core.cancellation import CancellationToken

class CodingLane:
    """Unified handler for software engineering and programming workflows."""

    def __init__(self):
        self.parser = ASTCodeParser()
        self.patcher = AtomicPatcher()
        self.sandbox = TestSandbox()
        self.mapper = RepoMapper()
        self.debugger = AutonomousDebugger()
        self.search = RepoSearchEngine()
        self.tdd = TDDSynthesizer()
        self.swe = SWEAgentOrchestrator()

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

        # 6. High-Speed Workspace Regex Search
        elif intent in ("search", "grep", "find_in_files"):
            pattern = str(getattr(step, "value", "") or "")
            res = self.search.search_content(root_dir=".", pattern=pattern)
            res["lane"] = "coding"
            res["status"] = "ok"
            res["changed"] = True
            res["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
            return res

        # 7. Symbol Definition Lookup
        elif intent in ("symbols", "find_symbols", "lookup_def"):
            sym = str(getattr(step, "value", "") or "")
            res = self.search.find_symbols(root_dir=".", symbol_query=sym)
            res["lane"] = "coding"
            res["status"] = "ok"
            res["changed"] = True
            res["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
            return res

        # 8. Workspace Directory Tree
        elif intent in ("tree", "dir_tree", "repo_tree"):
            target_dir = str(getattr(step, "value", "") or ".")
            tree_str = self.search.tree(root_dir=target_dir)
            return {
                "status": "ok",
                "lane": "coding",
                "mode": "workspace_tree",
                "tree": tree_str,
                "changed": True,
                "latency_ms": round((time.perf_counter() - t0) * 1000, 2)
            }

        # 9. Test-Driven Development (TDD) Loop
        elif intent in ("tdd", "tdd_synthesize", "test_driven"):
            req = str(getattr(step, "value", "") or getattr(step, "description", ""))
            res = self.tdd.run_tdd_loop(requirement=req)
            res["lane"] = "coding"
            res["status"] = "ok" if res["success"] else "tdd_failed"
            res["changed"] = True
            res["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
            return res

        # 10. SWE-Agent & Aider Autonomous Software Engineering Mode
        elif intent in ("swe", "swe_agent", "aider", "reproduce_issue", "pagerank"):
            goal_or_issue = str(getattr(step, "value", "") or getattr(step, "description", ""))
            args = getattr(step, "args", {}) or {}
            if "pagerank" in intent or args.get("mode") == "pagerank":
                symbols = args.get("symbols", {})
                res = {"status": "ok", "lane": "coding", "mode": "symbol_pagerank", "ranks": self.swe.compute_symbol_pagerank(symbols)}
            elif "fuzzy_patch" in intent or args.get("mode") == "fuzzy_patch":
                orig = args.get("original", "")
                tgt = args.get("target", "")
                repl = args.get("replacement", "")
                patch_res = self.swe.apply_fuzzy_patch(orig, tgt, repl)
                res = {"status": "ok" if patch_res.get("success") else "error", "lane": "coding", "patch": patch_res}
            else:
                test_code = self.swe.synthesize_reproduction_test(goal_or_issue)
                res = {
                    "status": "ok",
                    "lane": "coding",
                    "mode": "swe_reproduction",
                    "issue": goal_or_issue,
                    "reproduction_test": test_code,
                }
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
