"""KOSIF Think unified capability router.

One public surface; specialized engines remain internal adapters.
This module does not hold credentials and does not silently perform paid or consequential actions.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from typing import Any, Dict, List


@dataclass
class RoutePlan:
    lane: str
    adapters: List[str]
    verify: bool = True
    jev_mode: str = "only_if_ambiguous"
    approval_required: bool = False
    reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


COMPUTER = re.compile(r"computer|desktop|windows|excel|browser|chrome|device|file dialog|screen|كمبيوتر|جهاز|ويندوز|متصفح|اكسل|تحكم", re.I)
WHATSAPP = re.compile(r"whatsapp|واتساب|واتس اب|رسالة واتساب|ارسل.*رسالة|أرسل.*رسالة", re.I)
DECISION = re.compile(r"choose|choice|decide|decision|compare options|اختيار|اختر|قرار|مقارنة بدائل", re.I)
CONSEQUENTIAL = re.compile(r"pay|purchase|delete|publish|send|transfer|merge|commit|credential|security|ادفع|شراء|حذف|نشر|إرسال|ارسل|تحويل|ادمج|كلمة مرور|أمان", re.I)


def route(task: str, context: str = "") -> Dict[str, Any]:
    text = f"{task}\n{context}".strip()
    approval = bool(CONSEQUENTIAL.search(text))

    if WHATSAPP.search(text):
        return RoutePlan(
            lane="communication",
            adapters=["whatsapp"],
            verify=True,
            jev_mode="never_for_transport",
            approval_required=approval,
            reason="WhatsApp intent detected; preserve receipt-aware delivery semantics.",
        ).to_dict()

    if COMPUTER.search(text):
        adapters = ["browserjev", "browserremote", "playwright_cdp", "devtools", "windows_uia"]
        return RoutePlan(
            lane="computer",
            adapters=adapters,
            verify=True,
            jev_mode="closed_choice_on_observed_candidates",
            approval_required=approval,
            reason="Device/browser intent detected; local stable action graph is preferred before model ambiguity resolution.",
        ).to_dict()

    if DECISION.search(text):
        return RoutePlan(
            lane="decision",
            adapters=["think", "jev"],
            verify=False,
            jev_mode="bounded_choice",
            approval_required=False,
            reason="Decision intent detected; KOSIF Think frames the options and Jev resolves only bounded choices.",
        ).to_dict()

    return RoutePlan(
        lane="think",
        adapters=["think"],
        verify=False,
        jev_mode="optional",
        approval_required=False,
        reason="Default reasoning/research route.",
    ).to_dict()


def capability_map() -> Dict[str, Any]:
    return {
        "public_surface": "KOSIF Think",
        "internal_adapters": {
            "think": "planning, council, research, diagnosis, synthesis",
            "browserjev": "stable action graph, local ranking, ambiguity packets, recovery",
            "browserremote": "deterministic browser transport and input",
            "playwright_cdp": "DOM execution in persistent authenticated browser",
            "devtools": "network, console, performance and PDF diagnostics",
            "windows_uia": "Windows controls, dialogs, apps and screen-state",
            "whatsapp": "saved contacts, text/files/bundles/scheduling/receipts",
            "jev": "bounded ambiguity and structured decision only",
        },
        "rules": [
            "revalidate before consequential writes",
            "verify observable postconditions",
            "do not treat FINISH or model confidence as completion",
            "human-gate CAPTCHA, OTP, payment and credential/security confirmation",
            "no secrets in source files or chat",
        ],
    }
