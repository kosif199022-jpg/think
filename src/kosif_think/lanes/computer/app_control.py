"""
App Control: Manages application lifecycle, window state, and process management on Windows.
"""

import subprocess
import os
import time
from typing import Dict, Any, Optional

class AppControl:
    """Controls desktop applications and windows."""

    def launch_app(self, app_path: str, args: Optional[str] = None) -> Dict[str, Any]:
        """Launches an application asynchronously."""
        try:
            cmd = f'start "" "{app_path}" {args or ""}'
            subprocess.Popen(cmd, shell=True)
            return {"status": "ok", "app": app_path, "launched": True, "changed": True}
        except Exception as e:
            return {"status": "error", "app": app_path, "error": str(e), "changed": False}

    def is_process_running(self, process_name: str) -> bool:
        """Checks if a named process is active."""
        try:
            output = subprocess.check_output(f'tasklist /fi "imagename eq {process_name}"', shell=True, text=True)
            return process_name.lower() in output.lower()
        except Exception:
            return False
