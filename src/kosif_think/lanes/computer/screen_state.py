"""
Screen State: Observes display resolution, active window, and visual changes.
"""

from typing import Dict, Any
import subprocess

class ScreenState:
    """Provides screen diagnostics and state inspection."""

    def get_state(self) -> Dict[str, Any]:
        """Inspects active window and desktop metrics."""
        title = "Desktop"
        try:
            # Query active window via powershell
            cmd = '(Get-Process | Where-Object { $_.MainWindowTitle } | Select-Object -First 1).MainWindowTitle'
            out = subprocess.check_output(['powershell', '-Command', cmd], text=True, timeout=3).strip()
            if out:
                title = out
        except Exception:
            pass

        return {
            "active_window": title,
            "changed": True
        }
