"""
Computer Lane Engine: Dispatches desktop application launches, UI automation,
file operations, and screen state queries.
"""

from typing import Dict, Any, Optional
import time
from .app_control import AppControl
from .files import FileControl
from .screen_state import ScreenState
from .gui_grounding import GUIGroundingEngine
from ...core.cancellation import CancellationToken

class ComputerLane:
    """Unified handler for the computer lane."""

    def __init__(self):
        self.apps = AppControl()
        self.files = FileControl()
        self.screen = ScreenState()
        self.grounding = GUIGroundingEngine()

    async def dispatch_step(self, step: Any, cancellation_token: Optional[CancellationToken] = None) -> Dict[str, Any]:
        """Dispatches an action in the computer lane."""
        if cancellation_token:
            cancellation_token.throw_if_cancellation_requested()

        t0 = time.perf_counter()
        intent = getattr(step, "intent", "observe")

        if intent == "launch_app":
            app_target = getattr(getattr(step, "target", None), "ref", "notepad.exe") or "notepad.exe"
            res = self.apps.launch_app(app_target)
            res["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
            return res

        elif intent == "read_file":
            path_target = getattr(getattr(step, "target", None), "ref", "")
            return self.files.read_text(path_target)

        elif intent == "write_file":
            path_target = getattr(getattr(step, "target", None), "ref", "")
            content = str(getattr(step, "value", ""))
            return self.files.write_text(path_target, content)

        elif intent in ("ground", "locate", "find_element", "click_element"):
            instruction = str(getattr(step, "value", "") or getattr(step, "description", ""))
            res = self.grounding.ground_element(instruction)
            res["lane"] = "computer"
            res["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
            return res

        else:
            # Screen inspection
            state = self.screen.get_state()
            state["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
            return state
