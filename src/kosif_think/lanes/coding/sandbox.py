"""
Test Sandbox & Command Runner for KOSIF Think.
Executes unit tests, static analysis, and command verification with strict timeouts.
"""

import subprocess
import time
from typing import Dict, Any, Optional

class TestSandbox:
    """Executes tests and processes in controlled subprocess environments."""

    def run_tests(self, command: str = "python -m unittest discover tests", cwd: Optional[str] = None, timeout_sec: int = 30) -> Dict[str, Any]:
        """Runs test command and captures structured pass/fail metrics."""
        t0 = time.perf_counter()
        try:
            proc = subprocess.run(
                command,
                cwd=cwd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout_sec
            )
            duration_ms = round((time.perf_counter() - t0) * 1000, 2)
            passed = proc.returncode == 0

            return {
                "passed": passed,
                "exit_code": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "duration_ms": duration_ms
            }
        except subprocess.TimeoutExpired:
            return {
                "passed": False,
                "exit_code": -1,
                "stdout": "",
                "stderr": f"Test execution timed out after {timeout_sec} seconds.",
                "duration_ms": round((time.perf_counter() - t0) * 1000, 2)
            }
        except Exception as e:
            return {
                "passed": False,
                "exit_code": -1,
                "stdout": "",
                "stderr": str(e),
                "duration_ms": round((time.perf_counter() - t0) * 1000, 2)
            }
