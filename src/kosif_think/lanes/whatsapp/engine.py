"""
WhatsApp Lane Engine: Coordinates text, media, documents, and delivery verification.
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
        """Dispatches an action in the WhatsApp lane."""
        if cancellation_token:
            cancellation_token.throw_if_cancellation_requested()

        t0 = time.perf_counter()
        intent = getattr(step, "intent", "send_message")
        recipient = getattr(getattr(step, "target", None), "ref", "") or "default_chat"
        message_text = str(getattr(step, "value", ""))

        res = self.bridge.dispatch_text_message(recipient, message_text)
        res["lane"] = "whatsapp"
        res["changed"] = True
        res["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
        return res
