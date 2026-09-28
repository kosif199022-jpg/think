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
    lane: str  # reasoning, coding, graphics, computer, browser, whatsapp
    intent: str  # navigate, click, type, summarize, launch_app, send_message, verify, code, diagram, tot, etc.
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
        """Generates a structured execution plan from a sanitized request across all 6 lanes."""
        goal = req.clean_goal
        steps: List[Step] = []

        # Analyze intent patterns
        is_whatsapp = bool(re.search(r'\b(whatsapp|واتساب|واتس|رسالة|ارسل لـ|شات)\b', goal, re.I))
        is_coding = bool(re.search(r'\b(كود|برمجة|دالة|اختبار|فحص الكود|صلح|أصلح|fix|test|debug|ast|patch|refactor|python|code|repo_map)\b', goal, re.I))
        is_graphics = bool(re.search(r'\b(رسم|جرافيك|مخطط|دياجرام|diagram|mermaid|svg|canvas|واجهة|تصميم|flowchart|dashboard)\b', goal, re.I))
        is_computer = bool(re.search(r'\b(افتح برنامج|شغل تطبيق|ملف|مفكرة|notepad|calc|word|excel|سطح المكتب|وندوز)\b', goal, re.I))
        is_browser = bool(re.search(r'\b(تصفح|موقع|رابط|ابحث عن|google|chrome|url|http|كابتشا|صفحة|يوتيوب)\b', goal, re.I))

        # 1. Coding Lane Plan
        if is_coding and not is_whatsapp:
            if any(k in goal.lower() for k in ["test", "اختبار", "شغل الاختبارات"]):
                intent = "test"
                desc = "تشغيل حزمة الاختبارات وفحص حالة الأكواد"
            elif any(k in goal.lower() for k in ["debug", "صلح", "أصلح", "fix", "repair"]):
                intent = "debug"
                desc = "دورة الإصلاح الذاتي وتشخيص وتصحيح الأخطاء"
            elif any(k in goal.lower() for k in ["repo_map", "خريطة", "map"]):
                intent = "repo_map"
                desc = "بناء خريطة الرموز والعلاقات في المستودع"
            else:
                intent = "analyze"
                desc = "التحليل الاستنتاجي للشفرة البرمجية وبناء شجرة AST"

            steps.append(Step(
                step_id=1,
                lane="coding",
                intent=intent,
                target=Target(kind="codebase", ref="."),
                value=goal,
                expected_postconditions=[{"type": "code_processed"}],
                risk_level="low",
                description=desc
            ))

        # 2. Graphics Lane Plan
        elif is_graphics and not is_whatsapp:
            if "svg" in goal.lower():
                intent = "svg"
                desc = "توليد رسم شعاعي SVG عالي الدقة"
            elif any(k in goal.lower() for k in ["canvas", "dashboard", "لوحة"]):
                intent = "canvas"
                desc = "توليد واجهة HTML5/Canvas تفاعلية حية"
            else:
                intent = "diagram"
                desc = "توليد مخطط هيكلي معماري بصري (Mermaid)"

            steps.append(Step(
                step_id=1,
                lane="graphics",
                intent=intent,
                target=Target(kind="visual_canvas", ref="output"),
                value=goal,
                expected_postconditions=[{"type": "graphic_rendered"}],
                risk_level="low",
                description=desc
            ))

        # 3. WhatsApp Lane Plan
        elif is_whatsapp:
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

        # 4. Desktop Computer Lane Plan
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

        # 5. Browser Lane Plan
        elif is_browser:
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

        # 6. Advanced Reasoning / Council Lane Plan
        else:
            if "tot" in goal.lower() or "شجرة" in goal.lower():
                intent = "tot"
                desc = f"استكشاف شجرة الأفكار (Tree of Thoughts) للهدف: {goal[:40]}"
            elif "got" in goal.lower() or "شبكة" in goal.lower():
                intent = "got"
                desc = f"بناء شبكة الأفكار المتداخلة (Graph of Thoughts) للهدف: {goal[:40]}"
            elif "reflexion" in goal.lower() or "تأمل" in goal.lower():
                intent = "reflexion"
                desc = f"التفكير التأملي الاسترجاعي (Reflexion) للهدف: {goal[:40]}"
            elif "mcts" in goal.lower():
                intent = "mcts"
                desc = f"محاكاة مونت كارلو للأشجار (MCTS) للهدف: {goal[:40]}"
            else:
                intent = "council_evaluate"
                desc = f"تحليل المسألة عبر مجلس الذكاء والتفكير المعمق: {goal[:40]}"

            steps.append(Step(
                step_id=1,
                lane="reasoning",
                intent=intent,
                target=Target(kind="semantic", ref="problem_space"),
                value=goal,
                expected_postconditions=[{"type": "reasoning_complete"}],
                risk_level="low",
                description=desc
            ))

        return Plan(
            task_id=req.task_id,
            goal=goal,
            steps=steps,
            estimated_risk="low" if not is_whatsapp else "medium"
        )
