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
    args: Dict[str, Any] = field(default_factory=dict)

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
        is_office = bool(re.search(r'(?:ورد|وورد|بوربوينت|باوربوينت|بوربونت|اكسل|إكسل|word|docx|ppt|pptx|powerpoint|excel|xlsx|spreadsheet|financial_model)', goal, re.I))
        is_research = bool(re.search(r'(?:بحث علمي|ورقة بحثية|دراسة|مراجع|أوراق علمية|arxiv|pubmed|latex|bibtex|literature review|scientific)', goal, re.I))
        is_telephony = bool(re.search(r'(?:اتصال|مكالمة|هاتف|اتصل|dial|call|phone|sip|voip|twiml|meeting|اجتماع|zoom|google meet)', goal, re.I)) and not bool(re.search(r'(?:whatsapp|واتس)', goal, re.I))
        is_mobile = bool(re.search(r'(?:جوال|أندرويد|اندرويد|android|adb|هاتف ذكي|تطبيق جوال|تطبيق الهاتف)', goal, re.I)) and not bool(re.search(r'(?:آيفون|ايفون|iphone|ios)', goal, re.I))
        is_ios = bool(re.search(r'(?:آيفون|ايفون|iphone|ios|سيري|siri|اختصارات|shortcut|shortcuts)', goal, re.I))
        is_whatsapp = bool(re.search(r'(?:whatsapp|واتساب|واتس|رسالة|ارسل لـ|شات)', goal, re.I))
        is_voice = bool(re.search(r'\b(صوت|تحدث|نطق|انطق|تكلم|audio|voice|speech|tts|stt|whisper)\b', goal, re.I)) and not is_ios and not is_telephony
        is_coding = bool(re.search(r'\b(كود|برمجة|دالة|اختبار|فحص الكود|صلح|أصلح|fix|test|debug|ast|patch|refactor|python|code|repo_map)\b', goal, re.I))
        is_graphics = bool(re.search(r'\b(رسم|جرافيك|مخطط|دياجرام|diagram|mermaid|svg|canvas|واجهة|تصميم|flowchart|dashboard)\b', goal, re.I))
        is_computer = bool(re.search(r'\b(افتح برنامج|شغل تطبيق|ملف|مفكرة|notepad|calc|سطح المكتب|وندوز)\b', goal, re.I))
        is_browser = bool(re.search(r'\b(تصفح|موقع|رابط|ابحث عن|google|chrome|url|http|كابتشا|صفحة|يوتيوب|متصفح سحابي|سحابي)\b', goal, re.I))

        # 0. iOS Lane Plan
        if is_ios:
            if any(k in goal.lower() for k in ["تحدث", "قل", "انطق", "speak", "say"]):
                intent = "speak"
                desc = "نطق نص صوتي عبر Siri على الآيفون"
            elif any(k in goal.lower() for k in ["إشعار", "اشعار", "تنبيه", "notify", "notification"]):
                intent = "notify"
                desc = "إرسال إشعار فوري إلى جهاز الآيفون"
            elif any(k in goal.lower() for k in ["اختصار", "shortcut"]):
                intent = "shortcut"
                desc = "تشغيل اختصار آبل محدد على الآيفون"
            elif any(k in goal.lower() for k in ["انقر", "اضغط", "لمس", "tap", "touch"]):
                intent = "tap"
                desc = "محاكاة لمس ونقر على شاشة الآيفون"
            elif any(k in goal.lower() for k in ["هوم", "home"]):
                intent = "home"
                desc = "الضغط على زر الشاشة الرئيسية في الآيفون"
            else:
                intent = "open_app"
                app_m = re.search(r'(?:تطبيق|برنامج|open|app)\s+([a-zA-Z0-9_\-\u0621-\u064A]+)', goal)
                app_name = app_m.group(1) if app_m else "Safari"
                desc = f"فتح تطبيق {app_name} على جهاز الآيفون"

            steps.append(Step(
                step_id=1,
                lane="ios",
                intent=intent,
                target=Target(kind="ios_device", ref=goal),
                value=goal,
                expected_postconditions=[{"type": "ios_command_acknowledged"}],
                risk_level="low",
                description=desc
            ))

        # 0.5 Voice Lane Plan
        elif is_voice:
            steps.append(Step(
                step_id=1,
                lane="voice",
                intent="speak",
                target=Target(kind="voice_synthesizer", ref="tts"),
                value=goal,
                expected_postconditions=[{"type": "voice_spoken"}],
                risk_level="low",
                description="توليد ونطق المخرجات الصوتية عبر Voice Lane"
            ))

        # 0.6 Mobile Smartphone Lane Plan (Android / Cross-Platform)
        elif is_mobile:
            if any(k in goal.lower() for k in ["انقر", "اضغط", "لمس", "tap"]):
                intent = "tap"
                desc = "النقر على شاشة الجوال"
            elif any(k in goal.lower() for k in ["سحب", "تمرير", "swipe", "scroll"]):
                intent = "swipe"
                desc = "تمرير وسحب شاشة الجوال"
            elif any(k in goal.lower() for k in ["رسالة", "sms"]):
                intent = "sms"
                desc = "إرسال رسالة SMS عبر الجوال"
            elif any(k in goal.lower() for k in ["اتصل", "مكالمة", "dial"]):
                intent = "dial"
                desc = "إجراء مكالمة هاتفية عبر الجوال"
            else:
                intent = "launch_app"
                desc = f"التحكم وتشغيل التطبيق على الجوال: {goal}"

            steps.append(Step(
                step_id=1,
                lane="mobile",
                intent=intent,
                target=Target(kind="mobile_device", ref=goal),
                value=goal,
                expected_postconditions=[{"type": "mobile_action_completed"}],
                risk_level="low",
                description=desc
            ))

        # 0.7 Telephony & Call Lane Plan
        elif is_telephony:
            if any(k in goal.lower() for k in ["اجتماع", "meeting", "zoom", "meet", "teams"]):
                intent = "meeting"
                desc = "إنشاء رابط اجتماع افتراضي عبر Telephony Lane"
            elif any(k in goal.lower() for k in ["astra", "تفاعل صوتي", "محادثة"]):
                intent = "astra_session"
                desc = "بدء جلسة حوارية صوتية فورية فائقة الذكاء (Astra)"
            else:
                intent = "dial"
                desc = f"إجراء اتصال هاتفي عبر شبكة الاتصال: {goal}"

            steps.append(Step(
                step_id=1,
                lane="telephony",
                intent=intent,
                target=Target(kind="telephony_dialer", ref=goal),
                value=goal,
                expected_postconditions=[{"type": "telephony_call_dispatched"}],
                risk_level="medium",
                description=desc
            ))

        # 0.8 Scientific Research Lane Plan
        elif is_research:
            if any(k in goal.lower() for k in ["latex", "لاتكس"]):
                intent = "latex"
                desc = "توليد وتنسيق ورقة بحثية علمية بصيغة LaTeX"
            elif any(k in goal.lower() for k in ["دراسة", "مراجعة", "review", "survey"]):
                intent = "review"
                desc = "توليد مراجعة أدبيات شاملة ومصفوفة مقارنة علمية"
            elif any(k in goal.lower() for k in ["مراجع", "bibtex", "cite"]):
                intent = "bibtex"
                desc = "استخراج وتنسيق الاستشهادات الأكاديمية وصيغة BibTeX"
            elif any(k in goal.lower() for k in ["إحصاء", "احصاء", "دلالة", "p-value", "t-test"]):
                intent = "stats"
                desc = "التحقق من الدلالة الإحصائية والرصانة المنهجية للتجربة"
            else:
                intent = "search"
                desc = f"البحث الأكاديمي الموسع في ArXiv والأوراق المحكمة: {goal}"

            steps.append(Step(
                step_id=1,
                lane="research",
                intent=intent,
                target=Target(kind="academic_corpus", ref=goal),
                value=goal,
                expected_postconditions=[{"type": "research_synthesized"}],
                risk_level="low",
                description=desc
            ))

        # 0.9 Office Productivity Suite Plan (Word, PowerPoint, Excel)
        elif is_office:
            if any(k in goal.lower() for k in ["بوربوينت", "باوربوينت", "بوربونت", "ppt", "pptx", "presentation", "slides"]):
                intent = "ppt"
                desc = "إنشاء وتنسيق عرض تقديمي متكامل بصيغة PowerPoint (.pptx)"
            elif any(k in goal.lower() for k in ["اكسل", "إكسل", "excel", "xlsx", "csv", "spreadsheet", "financial_model", "معادلة"]):
                intent = "excel"
                desc = "بناء نموذج مالي ومصنف بيانات بصيغة Excel (.xlsx)"
            else:
                intent = "word"
                desc = "تأليف وتنسيق مستند رسمي متكامل بصيغة Microsoft Word (.docx)"

            steps.append(Step(
                step_id=1,
                lane="office",
                intent=intent,
                target=Target(kind="office_suite", ref=goal),
                value=goal,
                expected_postconditions=[{"type": "office_document_generated"}],
                risk_level="low",
                description=desc
            ))

        # 1. Coding Lane Plan
        elif is_coding and not is_whatsapp:
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
