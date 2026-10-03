"""WhatsApp bridge contract for the unified KOSIF Think runtime.

This local runtime never invents pairing, acceptance, delivery, or read state. Real
WhatsApp work is executed by the authenticated `kosif-whatsapp` MCP connection
listed in the plugin manifest. This module only prepares the host-mediated tool
request until concrete transport evidence is returned by that MCP.
"""

from typing import Dict, Any

from ...whatsapp_adapter import plan as plan_whatsapp


class WhatsAppBridge:
    """Truthful adapter to the host-managed KOSIF WhatsApp MCP transport."""

    def check_connection(self) -> Dict[str, Any]:
        """Request a real connection check; never assume the account is paired."""
        return {
            "status": "requires_host_check",
            "paired": None,
            "requires_host_execution": True,
            "tool": "get_whatsapp_status",
            "args": {},
            "dispatched": False,
            "changed": False,
        }

    def dispatch_text_message(self, recipient: str, message: str) -> Dict[str, Any]:
        """Prepare a real MCP send request without fabricating transport success."""
        tool_plan = plan_whatsapp("message", to=recipient, message=message)
        if not tool_plan.get("ok"):
            return {
                "status": "failed",
                "requires_host_execution": False,
                "dispatched": False,
                "changed": False,
                "error": tool_plan.get("error", "unable_to_plan_whatsapp_send"),
            }

        return {
            "status": "requires_host_execution",
            "requires_host_execution": True,
            "tool": tool_plan["tool"],
            "args": tool_plan.get("args", {}),
            "receipt_verification": tool_plan.get("receipt_verification", True),
            "secret_policy": tool_plan.get("secret_policy", "connection_context_only"),
            "dispatched": False,
            "transport_accepted": False,
            "changed": False,
        }
