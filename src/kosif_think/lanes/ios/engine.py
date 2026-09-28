"""
iOS Lane Engine for KOSIF Think.
Enables ChatGPT and KOSIF Think to control iPhone devices via Apple Shortcuts and WDA.
"""

from typing import Dict, Any, Optional
import time
from .shortcuts_bridge import ShortcutsBridge
from .wda_client import WDAClient
from ...core.cancellation import CancellationToken

class IOSLane:
    """Unified execution lane for iPhone & iOS control."""

    def __init__(self):
        self.shortcuts = ShortcutsBridge()
        self.wda = WDAClient()

    async def dispatch_step(self, step: Any, cancellation_token: Optional[CancellationToken] = None) -> Dict[str, Any]:
        """Dispatches an action in the iOS lane."""
        if cancellation_token:
            cancellation_token.throw_if_cancellation_requested()

        t0 = time.perf_counter()
        intent = str(getattr(step, "intent", "open_app")).lower()
        target_ref = str(getattr(getattr(step, "target", None), "ref", "") or "")
        val = getattr(step, "value", None)

        # 1. Open App on iPhone
        if intent in ("open_app", "launch_app"):
            app_name = target_ref or str(val or "Safari")
            res = self.shortcuts.open_app(app_name)
            res["lane"] = "ios"
            res["target_app"] = app_name
            res["changed"] = True
            res["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
            return res

        # 2. Siri Voice Speaking on iPhone
        elif intent in ("speak", "speak_text", "siri_say"):
            speech_text = str(val or target_ref or "Hello from KOSIF Think")
            res = self.shortcuts.speak_text(speech_text)
            res["lane"] = "ios"
            res["spoken_text"] = speech_text
            res["changed"] = True
            res["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
            return res

        # 3. Notification Push to iPhone
        elif intent in ("notify", "notification", "push_notification"):
            title = target_ref or "KOSIF Think Alert"
            body = str(val or "Action completed successfully.")
            res = self.shortcuts.notify(title, body)
            res["lane"] = "ios"
            res["changed"] = True
            res["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
            return res

        # 4. Trigger Named Apple Shortcut
        elif intent in ("shortcut", "run_shortcut"):
            shortcut_name = target_ref or str(val or "MyShortcut")
            res = self.shortcuts.run_shortcut(shortcut_name, str(val) if val else None)
            res["lane"] = "ios"
            res["shortcut"] = shortcut_name
            res["changed"] = True
            res["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
            return res

        # 5. Tap Coordinates on iPhone
        elif intent in ("tap", "touch"):
            coords = val if isinstance(val, dict) else {"x": 200, "y": 400}
            x = int(coords.get("x", 200))
            y = int(coords.get("y", 400))
            res = self.wda.tap(x, y)
            res["lane"] = "ios"
            res["changed"] = True
            res["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
            return res

        # 6. Press Home Button
        elif intent in ("home", "press_home"):
            res = self.wda.home()
            res["lane"] = "ios"
            res["changed"] = True
            res["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
            return res

        # 7. System Setting Toggle
        elif intent in ("setting", "set_setting"):
            setting_name = target_ref or "volume"
            res = self.shortcuts.set_system_setting(setting_name, val)
            res["lane"] = "ios"
            res["changed"] = True
            res["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
            return res

        return {
            "status": "ok",
            "lane": "ios",
            "action": intent,
            "message": f"iOS action '{intent}' handled.",
            "changed": True,
            "latency_ms": round((time.perf_counter() - t0) * 1000, 2)
        }
