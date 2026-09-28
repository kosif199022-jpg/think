"""
Playwright & CDP Adapter: Connects to the persistent KOSIF Chrome/CDP session.
"""

import json
import urllib.request
import asyncio
from typing import Dict, Any, List, Optional
from ...config import DEFAULT_CHROME_RUN_URL, DEFAULT_CHROME_HEALTH_URL

class PlaywrightCDPClient:
    """Manages communication with the running persistent Chrome instance."""

    def __init__(self, run_url: str = DEFAULT_CHROME_RUN_URL, health_url: str = DEFAULT_CHROME_HEALTH_URL):
        self.run_url = run_url
        self.health_url = health_url

    def is_connected(self) -> bool:
        try:
            req = urllib.request.Request(self.health_url)
            with urllib.request.urlopen(req, timeout=2) as r:
                return bool(json.load(r).get("ok"))
        except Exception:
            return False

    def post_actions_sync(self, actions: List[Dict[str, Any]], timeout: float = 12.0) -> Dict[str, Any]:
        """Sends atomic actions to the Chrome runner endpoint."""
        raw = json.dumps({"actions": actions}, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(self.run_url, data=raw, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.load(r)

    async def post_actions(self, actions: List[Dict[str, Any]], timeout: float = 12.0) -> Dict[str, Any]:
        return await asyncio.to_thread(self.post_actions_sync, actions, timeout)

    async def navigate(self, url: str) -> Dict[str, Any]:
        if not url.startswith(("http://", "https://", "about:", "file://")):
            url = "https://" + url
        res = await self.post_actions([{"op": "goto", "url": url}, {"op": "info"}])
        info = (res.get("results") or [{}, {}])[-1]
        return {"status": "ok", "url": info.get("url", url), "title": info.get("title", ""), "changed": True}

    async def click(self, selector: str) -> Dict[str, Any]:
        res = await self.post_actions([{"op": "click", "selector": selector}])
        return {"status": "ok", "action": "click", "selector": selector, "changed": bool(res.get("ok"))}

    async def fill_and_enter(self, selector: str, value: str) -> Dict[str, Any]:
        res = await self.post_actions([
            {"op": "fill", "selector": selector, "value": value},
            {"op": "press", "selector": selector, "key": "Enter"}
        ])
        return {"status": "ok", "action": "type", "selector": selector, "value": value, "changed": bool(res.get("ok"))}

    async def scroll(self, delta: int = 400) -> Dict[str, Any]:
        res = await self.post_actions([{"op": "scroll", "delta": delta}])
        return {"status": "ok", "action": "scroll", "delta": delta, "changed": bool(res.get("ok"))}
