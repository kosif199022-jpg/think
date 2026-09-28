"""KOSIF Think WhatsApp adapter contract.

The transport remains the authenticated KOSIF WhatsApp MCP/bridge. This module defines
how the unified KOSIF Think surface should route requests without embedding credentials.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional


SEND_ACTIONS = {
    "message": "send_whatsapp_message",
    "file": "send_whatsapp_file",
    "bundle": "send_whatsapp_bundle",
    "schedule_message": "schedule_whatsapp_message",
    "schedule_bundle": "schedule_whatsapp_bundle",
}

READ_ACTIONS = {
    "status": "get_whatsapp_status",
    "delivery": "get_whatsapp_delivery_report",
    "job": "get_whatsapp_job",
    "contacts": "list_saved_whatsapp_contacts",
    "resolve": "resolve_whatsapp_recipient",
    "diagnose": "diagnose_whatsapp_bridge",
}

CONTACT_ACTIONS = {
    "save": "save_whatsapp_contact",
    "delete": "delete_saved_whatsapp_contact",
}


def plan(
    operation: str,
    *,
    to: Optional[str] = None,
    message: Optional[str] = None,
    attachments: Optional[List[Dict[str, Any]]] = None,
    when: Optional[str] = None,
) -> Dict[str, Any]:
    """Return a host-mediated WhatsApp tool plan; never expose bridge secrets."""
    op = operation.lower().strip()
    if op in SEND_ACTIONS:
        args: Dict[str, Any] = {}
        if to is not None:
            args["to"] = to
        if message is not None:
            args["message"] = message
        if attachments:
            args["attachments"] = attachments
        if when is not None:
            args["when"] = when
        return {
            "ok": True,
            "lane": "whatsapp",
            "tool": SEND_ACTIONS[op],
            "args": args,
            "receipt_verification": True,
            "preflight_status_required": False,
            "secret_policy": "connection_context_only",
        }
    if op in READ_ACTIONS:
        return {"ok": True, "lane": "whatsapp", "tool": READ_ACTIONS[op], "args": {"to": to} if to else {}}
    if op in CONTACT_ACTIONS:
        return {"ok": True, "lane": "whatsapp", "tool": CONTACT_ACTIONS[op], "args": {"to": to} if to else {}}
    return {"ok": False, "error": "unknown_whatsapp_operation", "operation": operation}


def delivery_semantics() -> Dict[str, str]:
    return {
        "accepted": "transport accepted the send",
        "delivered": "provider delivery receipt confirmed",
        "read": "read receipt confirmed",
        "failed": "transport or item failure",
        "partial": "bundle only partially succeeded",
    }
