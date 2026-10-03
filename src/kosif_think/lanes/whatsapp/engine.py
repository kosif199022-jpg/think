"""
WhatsApp Lane Engine: prepares authenticated KOSIF WhatsApp MCP execution and
never converts a local plan into a fabricated send result.
"""

from typing import Dict, Any, Optional
import time
from .bridge import WhatsAppBridge
from ...core.cancellation import CancellationToken


class WhatsAppLane:
    """Unified handler for the WhatsApp lane."""

    def __init__(self):
        self.bridge = WhatsAppBridge()

    async def dispatch_step(self, step: Any, cancellation_token: Optional[CancellationToken] = None) -> Dict[str, Any]:
        """Prepare WhatsApp execution; the host MCP must provide real send evidence."""
        if cancellation_token:
            cancellation_token.throw_if_cancellation_requested()

        t0 = time.perf_counter()
        intent = getattr(step, "intent", "send_message")
        recipient = getattr(getattr(step, "target", None), "ref", "") or "default_chat"
        message_text = str(getattr(step, "value", ""))

        if intent in ("status", "check_status", "connection_status"):
            res = self.bridge.check_connection()
        elif intent == "send_message":
            res = self.bridge.dispatch_text_message(recipient, message_text)
        else:
            res = {
                "status": "failed",
                "requires_host_execution": False,
                "dispatched": False,
                "changed": False,
                "error": f"unsupported_whatsapp_intent:{intent}",
            }

        res["lane"] = "whatsapp"
        res["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
        return res
