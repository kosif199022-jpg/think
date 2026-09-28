"""
Autonomous Debugger for KOSIF Think.
Implements the self-repair loop: Test -> Observe Traceback -> Localize Fault -> Patch -> Re-verify.
"""

import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from .sandbox import TestSandbox
from .patcher import AtomicPatcher

class AutonomousDebugger:
    """Diagnoses test failures, extracts failing lines, and verifies candidate fixes."""

    def __init__(self):
        self.sandbox = TestSandbox()
        self.patcher = AtomicPatcher()

    def parse_traceback(self, stderr: str) -> Dict[str, Any]:
        """Extracts failing file, line number, exception type, and message from a Python traceback."""
        file_matches = list(re.finditer(r'File "([^"]+)", line (\d+), in (\w+)', stderr))
        err_match = re.search(r'([A-Za-z_][A-Za-z0-9_]*Error|Exception):\s*(.*)', stderr)

        failing_file = None
        failing_line = None
        failing_scope = None

        if file_matches:
            last = file_matches[-1]
            failing_file = last.group(1)
            failing_line = int(last.group(2))
            failing_scope = last.group(3)

        error_type = err_match.group(1) if err_match else "UnknownError"
        error_msg = err_match.group(2) if err_match else ""

        return {
            "file": failing_file,
            "line": failing_line,
            "scope": failing_scope,
            "error_type": error_type,
            "error_message": error_msg
        }

    def run_debug_cycle(self, test_command: str, cwd: Optional[str] = None) -> Dict[str, Any]:
        """Runs test, inspects failure, and returns targeted diagnostic report."""
        test_res = self.sandbox.run_tests(test_command, cwd=cwd)
        if test_res["passed"]:
            return {
                "status": "healthy",
                "message": "All tests passed with exit code 0.",
                "duration_ms": test_res["duration_ms"]
            }

        diag = self.parse_traceback(test_res["stderr"] or test_res["stdout"])
        return {
            "status": "fault_detected",
            "diagnosis": diag,
            "raw_stderr": test_res["stderr"][:1000],
            "duration_ms": test_res["duration_ms"],
            "recommended_action": f"Inspect {diag['file']} around line {diag['line']} for {diag['error_type']} ({diag['error_message']})"
        }
