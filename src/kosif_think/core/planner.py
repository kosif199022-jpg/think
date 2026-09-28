"""
Task Planner: Breaks down user intent into explicit steps with preconditions,
target definitions, execution lanes, expected observable postconditions, and risk levels.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import re
from .preflight import SanitizedRequest

@dataclass
class Target:
    kind: str = "semantic"  # semantic, element_id, selector, uia_name, phone_number, path
    name: Optional[str] = None
    ref: Optional[str] = None
    role: Optional[str] = None
    rect: Optional[Dict[str, int]] = None

@dataclass
class Step:
    step_id: int
    lane: str  # reasoning, computer, browser, whatsapp
    intent: str  # navigate, click, type, summarize, launch_app, send_message, verify
    target: Target = field(default_factory=Target)
    value: Any = None
    preconditions: List[str] = field(default_factory=list)
    expected_postconditions: List[Dict[str, Any]] = field(default_factory=list)
    risk_level: str = "auto"
    timeout_ms: int = 15000
    description: str = ""

@dataclass
class Plan:
    task_id: str
    goal: str
    steps: List[Step] = field(default_factory=list)
    estimated_risk: str = "low"
    requires_human_checkpoint: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


class TaskPlanner:
    """Intelligent rule-based and semantic decomposition engine."""

    def __init__(self):
        pass

    def create_plan(self, req: SanitizedRequest) -> Plan:
        """Generates a structured execution plan from a sanitized request."""
        goal = req.clean_goal
        steps: List[Step] = []

        # Analyze intent patterns
        is_whatsapp = bool(re.search(r'\b(whatsapp|واتساب|واتس|رسالة|ارسل لـ|شات)\b', goal, re.I))
        is_computer = bool(re.search(r'\b(افتح برنامج|شغل تطبيق|ملف|مفكرة|notepad|calc|word|excel|سطح المكتب|وندوز)\b', goal, re.I))
        is_browser = bool(re.search(r'\b(تصفح|موقع|رابط|ابحث عن|google|chrome|url|http|كابتشا|صفحة|يوتيوب)\b', goal, re.I))
        is_reasoning_only = bool(re.search(r'\b(فكر|حلل|ما رأيك|اشرح|مجلس|قارن|council|think|reason|ما هو|ما هي|كيف|لماذا)\b', goal, re.I)) and not (is_browser or is_computer or is_whatsapp)

        # 1. WhatsApp Lane Plan
        if is_whatsapp:
            target_match = re.search(r'(?:إلى|لـ|رقم|to)\s+([0-9\+\-\s]+|[^\s,]+)', goal)
            msg_match = re.search(r'(?:نص|رسالة|message)\s*[:=]?\s*["\']?([^"\'\n]+)', goal)
            recipient = target_match.group(1).strip() if target_match else "recent_chat"
            message = msg_match.group(1).strip() if msg_match else goal

            steps.append(Step(
                step_id=1,
                lane="whatsapp",
                intent="send_message",
                target=Target(kind="phone_number", ref=recipient),
                value=message,
                expected_postconditions=[{"type": "message_dispatched", "recipient": recipient}],
                risk_level="medium",
                description=f"إرسال رسالة واتساب إلى {recipient}"
            ))

        # 2. Desktop Computer Lane Plan
        elif is_computer:
            app_match = re.search(r'(?:برنامج|تطبيق|launch|run|open)\s+([a-zA-Z0-9_\-\.]+)', goal, re.I)
            app_name = app_match.group(1) if app_match else "notepad.exe"
            steps.append(Step(
                step_id=1,
                lane="computer",
                intent="launch_app",
                target=Target(kind="app_name", ref=app_name),
                expected_postconditions=[{"type": "process_running", "name": app_name}],
                risk_level="low",
                description=f"تشغيل تطبيق النظام: {app_name}"
            ))

        # 3. Browser Lane Plan
        elif is_browser or not is_reasoning_only:
            # Check for URL
            url_match = re.search(r'https?://[^\s]+', goal)
            if url_match:
                target_url = url_match.group(0)
                steps.append(Step(
                    step_id=1,
                    lane="browser",
                    intent="navigate",
                    target=Target(kind="url", ref=target_url),
                    expected_postconditions=[{"type": "url_matches", "expected": target_url}],
                    risk_level="low",
                    description=f"التنقل إلى الرابط {target_url}"
                ))
            else:
                # Search query
                query_clean = re.sub(r'^(?:ابحث عن|بحث عن|search for|find|google)\s*', '', goal, flags=re.I).strip()
                steps.append(Step(
                    step_id=1,
                    lane="browser",
                    intent="search_and_assess",
                    target=Target(kind="semantic", ref=query_clean),
                    value=query_clean,
                    expected_postconditions=[{"type": "dom_state_changed"}],
                    risk_level="low",
                    description=f"البحث والاستكشاف الذكي للهدف: {query_clean}"
                ))

        # 4. Pure Reasoning / Council Lane Plan
        else:
            steps.append(Step(
                step_id=1,
                lane="reasoning",
                intent="council_evaluate",
                target=Target(kind="semantic", ref="problem_space"),
                value=goal,
                expected_postconditions=[{"type": "reasoning_complete"}],
                risk_level="low",
                description=f"تحليل المسألة عبر مجلس الذكاء والتفكير المعمق: {goal[:50]}"
            ))

        return Plan(
            task_id=req.task_id,
            goal=goal,
            steps=steps,
            estimated_risk="low" if not is_whatsapp else "medium"
        )
