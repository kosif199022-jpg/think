"""
Browser Lane Engine: Coordinates the semantic action graph, Jev decision routing,
Playwright CDP execution, and anti-bot human checkpoints.
"""

from typing import Dict, Any, Optional
import time
from .action_graph import ActionGraph, INDEX_JS
from .jev_router import JevDecisionRouter
from .playwright_cdp import PlaywrightCDPClient
from ...core.cancellation import CancellationToken

class BrowserLane:
    """Unified handler for the browser execution lane."""

    def __init__(self):
        self.action_graph = ActionGraph()
        self.jev_router = JevDecisionRouter()
        self.cdp_client = PlaywrightCDPClient()

    async def dispatch_step(self, step: Any, cancellation_token: Optional[CancellationToken] = None) -> Dict[str, Any]:
        """Dispatches an action in the browser lane."""
        if cancellation_token:
            cancellation_token.throw_if_cancellation_requested()

        t0 = time.perf_counter()
        intent = getattr(step, "intent", "observe")

        # 1. Navigation
        if intent == "navigate":
            target_url = getattr(getattr(step, "target", None), "ref", "") or "https://www.google.com"
            res = await self.cdp_client.navigate(target_url)
            res["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
            return res

        # 2. Click
        elif intent == "click":
            raw_target = getattr(getattr(step, "target", None), "ref", "")
            action_id = self.action_graph.resolve_target(raw_target) or raw_target
            selector = f'[data-kosif-action="{action_id}"]' if not action_id.startswith(("[", "#", ".")) else action_id
            res = await self.cdp_client.click(selector)
            res["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
            return res

        # 3. Type
        elif intent in ("type", "fill"):
            raw_target = getattr(getattr(step, "target", None), "ref", "")
            action_id = self.action_graph.resolve_target(raw_target) or raw_target
            selector = f'[data-kosif-action="{action_id}"]' if not action_id.startswith(("[", "#", ".")) else action_id
            text_val = str(getattr(step, "value", ""))
            res = await self.cdp_client.fill_and_enter(selector, text_val)
            res["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
            return res

        # 4. Search and Assess (Dual Engine)
        elif intent == "search_and_assess":
            query = str(getattr(step, "value", ""))
            nav_url = f"https://www.google.com/search?q={query}"
            res = await self.cdp_client.navigate(nav_url)
            res["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
            return res

        # 5. Scroll
        elif intent == "scroll":
            delta = int(getattr(step, "value", 400) or 400)
            res = await self.cdp_client.scroll(delta)
            res["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
            return res

        # 6. Default Observe
        return {
            "status": "ok",
            "lane": "browser",
            "changed": True,
            "latency_ms": round((time.perf_counter() - t0) * 1000, 2)
        }
