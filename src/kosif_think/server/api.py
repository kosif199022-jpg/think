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
from ..lanes.voice import VoiceLane
from ..lanes.mobile import MobileLane
from ..lanes.telephony import TelephonyLane
from ..lanes.research import ResearchLane
from ..lanes.office import OfficeLane
from ..lanes.browser.cloud_view import render_cloud_browser_html
from ..connectors.openai_bridge import OpenAIBridge
from ..connectors.app_hub import AppHub
from ..connectors.open_source_engine import OpenSourceEngine
from ..core.cancellation import CancellationSource

logger = logging.getLogger("kosif_think.server")

# Global singleton executor with all 12 lanes registered
executor = ThinkExecutor()
executor.register_lane("reasoning", ReasoningLane())
executor.register_lane("coding", CodingLane())
executor.register_lane("graphics", GraphicsLane())
executor.register_lane("computer", ComputerLane())
executor.register_lane("browser", BrowserLane())
executor.register_lane("whatsapp", WhatsAppLane())
executor.register_lane("ios", IOSLane())
executor.register_lane("voice", VoiceLane())
executor.register_lane("mobile", MobileLane())
executor.register_lane("telephony", TelephonyLane())
executor.register_lane("research", ResearchLane())
executor.register_lane("office", OfficeLane())

# Connectors
openai_bridge = OpenAIBridge(executor)
app_hub = AppHub()
open_models_engine = OpenSourceEngine()

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

    def _send_html(self, status_code: int, html_str: str):
        raw = html_str.encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Access-Control-Allow-Origin", "*")
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
                "version": "1.2.0",
                "lanes": ["reasoning", "coding", "graphics", "computer", "browser", "whatsapp", "ios", "voice"],
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

        # Cloud Browser Sessions
        elif path == "/api/browser/sessions":
            b_lane: BrowserLane = executor._lane_handlers["browser"]
            self._send_json(200, {"ok": True, "sessions": b_lane.cloud_manager.list_sessions()})

        # Cloud Browser View (HTML5 Remote Viewer)
        elif path.startswith("/api/browser/session/") and path.endswith("/view"):
            b_lane: BrowserLane = executor._lane_handlers["browser"]
            session = b_lane.cloud_manager.get_or_create_default()
            html_markup = render_cloud_browser_html(session.to_dict())
            self._send_html(200, html_markup)

        # Cloud Browser State
        elif path.startswith("/api/browser/session/") and path.endswith("/state"):
            b_lane: BrowserLane = executor._lane_handlers["browser"]
            self._send_json(200, b_lane.jev_cloud.get_cloud_state("default"))

        # Open-Source Models Catalog
        elif path in ("/api/open-models/catalog", "/api/v1/open_models"):
            self._send_json(200, {"ok": True, "models": open_models_engine.list_models()})

        # Mobile Device Information
        elif path == "/api/mobile/info":
            m_lane: MobileLane = executor._lane_handlers["mobile"]
            self._send_json(200, {"ok": True, "info": m_lane.android.get_device_info()})

        # Telephony History
        elif path == "/api/telephony/history":
            t_lane: TelephonyLane = executor._lane_handlers["telephony"]
            self._send_json(200, {"ok": True, "calls": t_lane.call_manager.call_history})

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

        # Cloud Browser Action Dispatch
        elif path.startswith("/api/browser/session/") and path.endswith("/action"):
            b_lane: BrowserLane = executor._lane_handlers["browser"]
            act = payload.get("action", "navigate")
            if act == "navigate":
                res = b_lane.jev_cloud.navigate("default", payload.get("url", "https://www.google.com"))
            elif act == "click":
                res = b_lane.jev_cloud.click_jev("default", payload.get("action_id", "a_btn_1"))
            elif act == "type":
                res = b_lane.jev_cloud.type_human("default", payload.get("action_id", "a_input_1"), payload.get("text", ""))
            elif act == "scroll":
                res = b_lane.jev_cloud.scroll_jev("default", payload.get("amount", 400), payload.get("direction", "down"))
            elif act in ("auto_goal", "jev_goal"):
                res = b_lane.jev_cloud.run_autonomous_goal("default", payload.get("goal", ""))
            else:
                res = {"error": f"Unknown action: {act}"}
            self._send_json(200, res)

        # Cloud Browser Scrape
        elif path.startswith("/api/browser/session/") and path.endswith("/scrape"):
            b_lane: BrowserLane = executor._lane_handlers["browser"]
            html_str = payload.get("html", "")
            meta = b_lane.scraper.extract_metadata(html_str)
            tables = b_lane.scraper.extract_tables(html_str)
            md = b_lane.scraper.html_to_markdown(html_str)
            self._send_json(200, {"ok": True, "metadata": meta, "tables": tables, "markdown": md})

        # Deep Thinking Long-CoT Endpoint
        elif path in ("/api/think/deep", "/api/v1/deep_think"):
            r_lane: ReasoningLane = executor._lane_handlers["reasoning"]
            prob = payload.get("problem") or payload.get("goal") or ""
            effort = payload.get("effort", "high")
            res = r_lane.deep_think.deliberate(prob, compute_budget_effort=effort)
            self._send_json(200, res)

        # Cognitive Thought Map Endpoint
        elif path in ("/api/think/thought-map", "/api/v1/thought_map"):
            goal = payload.get("goal") or payload.get("problem") or "Autonomous Super-Intelligence Architecture"
            from ..lanes.reasoning.thought_map import CognitiveThoughtMap
            tmap = CognitiveThoughtMap()
            tmap.build_from_goal(goal)
            self._send_json(200, {
                "ok": True,
                "map_id": tmap.map_id,
                "data": tmap.to_dict(),
                "mermaid": tmap.to_mermaid_mindmap(),
                "ascii_tree": tmap.to_ascii_tree(),
                "critical_path": tmap.find_critical_path()
            })

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

        # Open-Source Models Inference
        elif path in ("/api/open-models/run", "/api/v1/open_models/run"):
            prompt = payload.get("prompt", "")
            model_id = payload.get("model", "deepseek-r1")
            system_inst = payload.get("system_instruction")
            res = open_models_engine.run_inference(prompt, model_id=model_id, system_instruction=system_inst)
            self._send_json(200, res)

        # Mobile Control Action
        elif path == "/api/mobile/action":
            m_lane: MobileLane = executor._lane_handlers["mobile"]
            from ..core.planner import Step
            intent = payload.get("intent", "observe")
            val = payload.get("value")
            step = Step(step_id=1, lane="mobile", intent=intent, value=val, args=payload)
            res = asyncio.run(m_lane.dispatch_step(step))
            self._send_json(200, res)

        # Telephony & Call Action
        elif path == "/api/telephony/action":
            t_lane: TelephonyLane = executor._lane_handlers["telephony"]
            from ..core.planner import Step
            intent = payload.get("intent", "dial")
            val = payload.get("value")
            step = Step(step_id=1, lane="telephony", intent=intent, value=val, args=payload)
            res = asyncio.run(t_lane.dispatch_step(step))
            self._send_json(200, res)

        # Research & Academic Search / Review
        elif path == "/api/research/action":
            r_lane: ResearchLane = executor._lane_handlers["research"]
            from ..core.planner import Step
            intent = payload.get("intent", "search")
            val = payload.get("value")
            step = Step(step_id=1, lane="research", intent=intent, value=val, args=payload)
            res = asyncio.run(r_lane.dispatch_step(step))
            self._send_json(200, res)

        # Office Suite Action (Word / PowerPoint / Excel)
        elif path == "/api/office/action":
            o_lane: OfficeLane = executor._lane_handlers["office"]
            from ..core.planner import Step
            intent = payload.get("intent", "word")
            val = payload.get("value")
            step = Step(step_id=1, lane="office", intent=intent, value=val, args=payload)
            res = asyncio.run(o_lane.dispatch_step(step))
            self._send_json(200, res)

        # RLVR Verifiable Reward Search (DeepSeek-R1 / Open-R1)
        elif path in ("/api/rlvr/search", "/api/v1/rlvr"):
            r_lane: ReasoningLane = executor._lane_handlers["reasoning"]
            from ..core.planner import Step
            prob = payload.get("problem") or payload.get("goal") or ""
            step = Step(step_id=1, lane="reasoning", intent="rlvr", value=prob)
            res = asyncio.run(r_lane.dispatch_step(step))
            self._send_json(200, res)

        # Smolagents CodeAgent Execution
        elif path in ("/api/code-agent/run", "/api/v1/code_agent"):
            r_lane: ReasoningLane = executor._lane_handlers["reasoning"]
            from ..core.planner import Step
            code = payload.get("code") or payload.get("script") or ""
            step = Step(step_id=1, lane="reasoning", intent="code_agent", value=code)
            res = asyncio.run(r_lane.dispatch_step(step))
            self._send_json(200, res)

        # Cross-Repo Super-Agent Strategy
        elif path in ("/api/repo-intel/strategy", "/api/v1/strategy"):
            r_lane: ReasoningLane = executor._lane_handlers["reasoning"]
            from ..core.planner import Step
            goal = payload.get("goal") or payload.get("query") or ""
            step = Step(step_id=1, lane="reasoning", intent="repo_strategy", value=goal)
            res = asyncio.run(r_lane.dispatch_step(step))
            self._send_json(200, res)

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
