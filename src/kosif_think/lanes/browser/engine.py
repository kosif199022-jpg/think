"""
Browser Lane Engine: Coordinates the semantic action graph, Jev decision routing,
Playwright CDP execution, and anti-bot human checkpoints.
"""

from typing import Dict, Any, Optional
import time
from .action_graph import ActionGraph, INDEX_JS
from .jev_router import JevDecisionRouter
from .playwright_cdp import PlaywrightCDPClient
from .cloud_session import CloudSessionManager
from .jev_controller import JevCloudController
from .jev_scraper import JevWebScraper
from .browser_use_engine import BrowserUseEngine
from ...core.cancellation import CancellationToken

class BrowserLane:
    """Unified handler for the browser execution lane with Jev Cloud Control."""

    def __init__(self):
        self.action_graph = ActionGraph()
        self.jev_router = JevDecisionRouter()
        self.cdp_client = PlaywrightCDPClient()
        self.cloud_manager = CloudSessionManager()
        self.jev_cloud = JevCloudController(session_manager=self.cloud_manager)
        self.scraper = JevWebScraper()
        self.browser_use = BrowserUseEngine()

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

        # 6. Jev Cloud Browser: Navigate
        elif intent in ("cloud_navigate", "cloud_open"):
            target_url = str(getattr(step, "value", "") or getattr(getattr(step, "target", None), "ref", "")) or "https://www.google.com"
            res = self.jev_cloud.navigate(session_id="default", url=target_url)
            res["lane"] = "browser"
            res["changed"] = True
            return res

        # 7. Jev Cloud Browser: Click
        elif intent in ("cloud_click", "jev_click"):
            target_id = str(getattr(step, "value", "") or getattr(getattr(step, "target", None), "ref", "a_btn_1"))
            res = self.jev_cloud.click_jev(session_id="default", action_id=target_id)
            res["lane"] = "browser"
            return res

        # 8. Jev Cloud Browser: Type with Human Cadence
        elif intent in ("cloud_type", "jev_type"):
            target_id = getattr(getattr(step, "target", None), "ref", "a_input_1") or "a_input_1"
            text_val = str(getattr(step, "value", ""))
            res = self.jev_cloud.type_human(session_id="default", action_id=target_id, text=text_val)
            res["lane"] = "browser"
            return res

        # 9. Jev Cloud Browser: Viewport Scroll
        elif intent in ("cloud_scroll", "jev_scroll"):
            amount = int(getattr(step, "value", 400) or 400)
            res = self.jev_cloud.scroll_jev(session_id="default", amount=amount)
            res["lane"] = "browser"
            return res

        # 10. Jev Cloud Browser: Autonomous Multi-Step Goal
        elif intent in ("jev_goal", "cloud_auto", "auto_browser"):
            goal_str = str(getattr(step, "value", "") or getattr(step, "description", ""))
            res = self.jev_cloud.run_autonomous_goal(session_id="default", goal=goal_str)
            res["lane"] = "browser"
            res["status"] = "ok"
            res["changed"] = True
            return res

        # 11. Jev Cloud Browser: Scrape Structured Data
        elif intent in ("cloud_scrape", "scrape_page"):
            raw_html = str(getattr(step, "value", ""))
            meta = self.scraper.extract_metadata(raw_html)
            tables = self.scraper.extract_tables(raw_html)
            md = self.scraper.html_to_markdown(raw_html)
            return {
                "status": "ok",
                "lane": "browser",
                "mode": "jev_scraper",
                "metadata": meta,
                "tables": tables,
                "markdown": md,
                "changed": True,
                "latency_ms": round((time.perf_counter() - t0) * 1000, 2)
            }

        # 12. Browser-Use Vision & Set-of-Marks Mode
        elif intent in ("browser_use", "flatten_dom", "som_index", "stealth_mouse"):
            val_str = str(getattr(step, "value", "") or "")
            args = getattr(step, "args", {}) or {}
            if "mouse" in intent or args.get("mode") == "stealth_mouse":
                start_pt = tuple(args.get("start", (100, 100)))
                end_pt = tuple(args.get("end", (500, 400)))
                pts = self.browser_use.generate_stealth_mouse_curve(start_pt, end_pt)
                res = {"status": "ok", "lane": "browser", "mode": "stealth_mouse", "points_count": len(pts), "trajectory": pts}
            else:
                html = val_str or "<html><body><button id='btn'>Submit</button><input name='q' placeholder='Search'/></body></html>"
                elements = self.browser_use.flatten_dom(html)
                res = {
                    "status": "ok",
                    "lane": "browser",
                    "mode": "flatten_dom",
                    "element_count": len(elements),
                    "interactive_elements": elements,
                    "action_space": self.browser_use.get_current_action_space()
                }
            res["changed"] = True
            res["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
            return res

        # 12. Default Observe
        return {
            "status": "ok",
            "lane": "browser",
            "changed": True,
            "latency_ms": round((time.perf_counter() - t0) * 1000, 2)
        }
