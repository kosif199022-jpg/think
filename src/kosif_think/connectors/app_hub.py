"""
Multi-App & Webhook Hub for KOSIF Think.
Bridges communication with ChatGPT Custom Actions (OpenAPI 3.0),
Telegram, Discord, Slack, and automation platforms (n8n, Zapier).
"""

import json
import urllib.request
from typing import Dict, Any, List, Optional
from ..config import DEFAULT_SERVER_HOST, DEFAULT_SERVER_PORT

class AppHub:
    """Manages outbound dispatch and inbound webhooks for external messaging apps and automation."""

    def get_openapi_spec(self, host: str = DEFAULT_SERVER_HOST, port: int = DEFAULT_SERVER_PORT) -> Dict[str, Any]:
        """Generates OpenAPI 3.0 specification for ChatGPT Custom GPT Actions."""
        return {
            "openapi": "3.0.0",
            "info": {
                "title": "KOSIF Think AI Action Bridge",
                "version": "1.0.0",
                "description": "Enables ChatGPT to execute autonomous browsing, computer control, and deep reasoning via KOSIF Think."
            },
            "servers": [
                {"url": f"http://{host}:{port}"}
            ],
            "paths": {
                "/api/think/execute": {
                    "post": {
                        "operationId": "executeGoal",
                        "summary": "Executes an autonomous goal across 6 KOSIF Think lanes",
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "goal": {"type": "string", "description": "The natural language instruction."},
                                            "approved": {"type": "boolean", "description": "Explicit approval for high-risk operations."}
                                        },
                                        "required": ["goal"]
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {
                                "description": "Successful execution response",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "ok": {"type": "boolean"},
                                                "status": {"type": "string"},
                                                "task_id": {"type": "string"},
                                                "output": {"type": "object"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "/api/think/plan": {
                    "post": {
                        "operationId": "planGoal",
                        "summary": "Decomposes a goal into a contract without execution",
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "goal": {"type": "string"}
                                        },
                                        "required": ["goal"]
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {"description": "Plan breakdown"}
                        }
                    }
                }
            }
        }

    def dispatch_webhook(self, webhook_url: str, payload: Dict[str, Any], timeout: float = 5.0) -> Dict[str, Any]:
        """Dispatches an outbound notification to Telegram, Discord, Slack, or n8n."""
        try:
            raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            req = urllib.request.Request(
                webhook_url,
                data=raw,
                headers={"Content-Type": "application/json", "User-Agent": "KOSIF-Think-AppHub/1.0"}
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return {"status": "ok", "code": resp.getcode(), "dispatched": True}
        except Exception as e:
            return {"status": "error", "error": str(e), "dispatched": False}

    def format_discord_message(self, title: str, description: str, fields: List[Dict[str, str]]) -> Dict[str, Any]:
        """Formats payload for Discord webhook."""
        return {
            "embeds": [
                {
                    "title": f"⚡ {title}",
                    "description": description,
                    "color": 3911672,  # #38BDF8 blue
                    "fields": [{"name": f["name"], "value": f["value"], "inline": True} for f in fields]
                }
            ]
        }

    def format_slack_message(self, text: str) -> Dict[str, Any]:
        """Formats payload for Slack webhook."""
        return {"text": f"🧠 *KOSIF Think*: {text}"}
