"""
Computer Lane Engine: Dispatches desktop application launches, UI automation,
process lifecycle, keystrokes, clipboard, file operations, and screen state queries.
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
        intent = str(getattr(step, "intent", "observe")).lower()
        target_ref = getattr(getattr(step, "target", None), "ref", "") or ""
        val = getattr(step, "value", None)
        args = getattr(step, "args", {}) or {}

        if intent in ("launch_app", "open_app", "run_app"):
            app_target = target_ref or str(val or "notepad.exe")
            res = self.apps.launch_app(app_target, args.get("args"))
            res["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
            return res

        elif intent in ("close_app", "terminate_app", "kill_app"):
            app_target = target_ref or str(val or "")
            res = self.apps.terminate_app(app_target)
            res["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
            return res

        elif intent in ("list_apps", "running_apps", "ps"):
            apps = self.apps.list_running_apps()
            return {"status": "ok", "apps": apps, "count": len(apps), "latency_ms": round((time.perf_counter() - t0) * 1000, 2)}

        elif intent in ("focus", "focus_window"):
            target = target_ref or str(val or "")
            res = self.apps.focus_window(target)
            res["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
            return res

        elif intent in ("send_keys", "type", "press_keys"):
            keys = str(val or target_ref or "")
            window = args.get("window")
            res = self.apps.send_keys(keys, window)
            res["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
            return res

        elif intent in ("clipboard_get", "get_clipboard"):
            clip_text = self.apps.get_clipboard_text()
            return {"status": "ok", "clipboard": clip_text, "latency_ms": round((time.perf_counter() - t0) * 1000, 2)}

        elif intent in ("clipboard_set", "set_clipboard"):
            text = str(val or target_ref or "")
            ok = self.apps.set_clipboard_text(text)
            return {"status": "ok" if ok else "error", "copied": ok, "latency_ms": round((time.perf_counter() - t0) * 1000, 2)}

        elif intent in ("screenshot", "capture_screen"):
            out_path = target_ref or str(val or "desktop_screenshot.png")
            res = self.apps.take_screenshot(out_path)
            res["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
            return res

        elif intent == "read_file":
            return self.files.read_text(target_ref)

        elif intent == "write_file":
            content = str(val or "")
            return self.files.write_text(target_ref, content)

        elif intent in ("ground", "locate", "find_element", "click_element"):
            instruction = str(val or getattr(step, "description", ""))
            res = self.grounding.ground_element(instruction)
            res["lane"] = "computer"
            res["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
            return res

        else:
            state = self.screen.get_state()
            state["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
            return state
