"""
KOSIF Think Single-Surface Server: Provides a unified HTTP, JSON, and OpenAI-compatible API.
Includes endpoints for ChatGPT integration, Apple Shortcuts iPhone automation, and multi-app webhooks.
"""

import json
import logging
import asyncio
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
from typing import Dict, Any, Optional

from ..config import DEFAULT_SERVER_HOST, DEFAULT_SERVER_PORT, get_auth_token
from ..core.executor import ThinkExecutor
from ..lanes.reasoning import ReasoningLane
from ..lanes.coding import CodingLane
from ..lanes.graphics import GraphicsLane
from ..lanes.computer import ComputerLane
from ..lanes.browser import BrowserLane
from ..lanes.whatsapp import WhatsAppLane
from ..lanes.ios import IOSLane
from ..connectors.openai_bridge import OpenAIBridge
from ..connectors.app_hub import AppHub
from ..core.cancellation import CancellationSource

logger = logging.getLogger("kosif_think.server")

# Global singleton executor with all 7 lanes registered
executor = ThinkExecutor()
executor.register_lane("reasoning", ReasoningLane())
executor.register_lane("coding", CodingLane())
executor.register_lane("graphics", GraphicsLane())
executor.register_lane("computer", ComputerLane())
executor.register_lane("browser", BrowserLane())
executor.register_lane("whatsapp", WhatsAppLane())
executor.register_lane("ios", IOSLane())

# Connectors
openai_bridge = OpenAIBridge(executor)
app_hub = AppHub()

class ThinkHTTPRequestHandler(BaseHTTPRequestHandler):
    """Handles REST and OpenAI-compatible API requests for KOSIF Think."""

    def _send_json(self, status_code: int, data: Dict[str, Any]):
        raw = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-KOSIF-TOKEN")
        self.end_headers()
        self.wfile.write(raw)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-KOSIF-TOKEN")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path in ("/", "/health", "/api/health"):
            self._send_json(200, {
                "ok": True,
                "service": "KOSIF Think Super-Intelligence Platform",
                "version": "1.1.0",
                "lanes": ["reasoning", "coding", "graphics", "computer", "browser", "whatsapp", "ios"],
                "chatgpt_bridge": True,
                "iphone_control": True,
                "active": True
            })

        # OpenAI Models endpoint
        elif path in ("/v1/models", "/api/v1/models"):
            self._send_json(200, openai_bridge.list_models())

        # OpenAPI 3.0 specification for ChatGPT Custom Actions
        elif path in ("/openapi.json", "/api/openapi.json"):
            self._send_json(200, app_hub.get_openapi_spec())

        elif path == "/api/think/status":
            recent_events = executor.audit.get_recent_events(limit=20)
            self._send_json(200, {
                "ok": True,
                "lane_metrics": executor.router._lane_health,
                "recent_events": recent_events
            })

        elif path == "/api/think/events":
            qs = parse_qs(parsed.query)
            limit = int(qs.get("limit", [50])[0])
            task_id = qs.get("task_id", [None])[0]
            events = executor.audit.get_recent_events(limit=limit, task_id=task_id)
            self._send_json(200, {"ok": True, "count": len(events), "events": events})

        # iOS Shortcut Polling endpoint
        elif path == "/api/ios/poll":
            qs = parse_qs(parsed.query)
            dev_id = qs.get("device_id", [None])[0]
            ios_lane: IOSLane = executor._lane_handlers["ios"]
            actions = ios_lane.shortcuts.poll_pending_actions(dev_id)
            self._send_json(200, {"ok": True, "actions": actions})

        else:
            self._send_json(404, {"ok": False, "error": "Endpoint not found"})

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", 0))
        body_bytes = self.rfile.read(length) if length > 0 else b"{}"

        try:
            payload = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}
        except Exception:
            self._send_json(400, {"ok": False, "error": "Invalid JSON payload"})
            return

        # Helper to get or create event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        # 1. OpenAI Chat Completions (Direct ChatGPT integration)
        if path in ("/v1/chat/completions", "/api/v1/chat/completions"):
            res = loop.run_until_complete(openai_bridge.handle_chat_completion(payload))
            self._send_json(200, res)

        # 2. Native Think Execution
        elif path == "/api/think/execute":
            goal = payload.get("goal") or payload.get("prompt") or ""
            context = payload.get("context") or {}
            approved = bool(payload.get("approved", False))

            result = loop.run_until_complete(
                executor.execute_goal(raw_prompt=goal, context=context, approved=approved)
            )

            self._send_json(200, {
                "ok": result.status in ("completed", "human_checkpoint"),
                "task_id": result.task_id,
                "status": result.status,
                "steps_executed": result.steps_executed,
                "duration_ms": result.duration_ms,
                "output": result.output,
                "checkpoint": result.checkpoint_details,
                "error": result.error
            })

        # 3. Direct iPhone Action Trigger
        elif path == "/api/ios/action":
            action_type = payload.get("action", "open_app")
            params = payload.get("params", {})
            ios_lane: IOSLane = executor._lane_handlers["ios"]
            res = ios_lane.shortcuts.enqueue_action(action_type, params)
            self._send_json(200, {"ok": True, "result": res})

        # 4. iPhone Action Acknowledgment
        elif path == "/api/ios/ack":
            cmd_id = payload.get("cmd_id", "")
            result_data = payload.get("result", {})
            ios_lane: IOSLane = executor._lane_handlers["ios"]
            res = ios_lane.shortcuts.report_action_result(cmd_id, result_data)
            self._send_json(200, res)

        elif path == "/api/think/plan":
            goal = payload.get("goal") or payload.get("prompt") or ""
            req = executor.preflight.run_preflight(goal)
            plan = executor.planner.create_plan(req)
            self._send_json(200, {
                "ok": True,
                "task_id": plan.task_id,
                "goal": plan.goal,
                "steps_count": len(plan.steps),
                "estimated_risk": plan.estimated_risk,
                "steps": [
                    {
                        "step_id": s.step_id,
                        "lane": s.lane,
                        "intent": s.intent,
                        "description": s.description,
                        "risk_level": s.risk_level
                    } for s in plan.steps
                ]
            })

        else:
            self._send_json(404, {"ok": False, "error": "Endpoint not found"})


def run_server(host: str = DEFAULT_SERVER_HOST, port: int = DEFAULT_SERVER_PORT):
    """Starts the single-surface HTTP server."""
    server_address = (host, port)
    httpd = ThreadingHTTPServer(server_address, ThinkHTTPRequestHandler)
    print(f"🚀 KOSIF Think Unified Server listening on http://{host}:{port}")
    print(f"🔗 OpenAI / ChatGPT API endpoint: http://{host}:{port}/v1/chat/completions")
    print(f"📱 iPhone Shortcuts Webhook:     http://{host}:{port}/api/ios/poll")
    print(f"📄 ChatGPT OpenAPI Specification: http://{host}:{port}/openapi.json")
    httpd.serve_forever()
