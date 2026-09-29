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
    context: Dict[str, Any] = field(default_factory=dict)

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
        is_office = bool(re.search(r'(?:ظˆط±ط¯|ظˆظˆط±ط¯|ط¨ظˆط±ط¨ظˆظٹظ†طھ|ط¨ط§ظˆط±ط¨ظˆظٹظ†طھ|ط¨ظˆط±ط¨ظˆظ†طھ|ط§ظƒط³ظ„|ط¥ظƒط³ظ„|word|docx|ppt|pptx|powerpoint|excel|xlsx|spreadsheet|financial_model)', goal, re.I))
        is_research = bool(re.search(r'(?:ط¨ط­ط« ط¹ظ„ظ…ظٹ|ظˆط±ظ‚ط© ط¨ط­ط«ظٹط©|ط¯ط±ط§ط³ط©|ظ…ط±ط§ط¬ط¹|ط£ظˆط±ط§ظ‚ ط¹ظ„ظ…ظٹط©|arxiv|pubmed|latex|bibtex|literature review|scientific)', goal, re.I))
        is_telephony = bool(re.search(r'(?:ط§طھطµط§ظ„|ظ…ظƒط§ظ„ظ…ط©|ظ‡ط§طھظپ|ط§طھطµظ„|dial|call|phone|sip|voip|twiml|meeting|ط§ط¬طھظ…ط§ط¹|zoom|google meet)', goal, re.I)) and not bool(re.search(r'(?:whatsapp|ظˆط§طھط³)', goal, re.I))
        is_mobile = bool(re.search(r'(?:ط¬ظˆط§ظ„|ط£ظ†ط¯ط±ظˆظٹط¯|ط§ظ†ط¯ط±ظˆظٹط¯|android|adb|ظ‡ط§طھظپ ط°ظƒظٹ|طھط·ط¨ظٹظ‚ ط¬ظˆط§ظ„|طھط·ط¨ظٹظ‚ ط§ظ„ظ‡ط§طھظپ)', goal, re.I)) and not bool(re.search(r'(?:ط¢ظٹظپظˆظ†|ط§ظٹظپظˆظ†|iphone|ios)', goal, re.I))
        is_ios = bool(re.search(r'(?:ط¢ظٹظپظˆظ†|ط§ظٹظپظˆظ†|iphone|ios|ط³ظٹط±ظٹ|siri|ط§ط®طھطµط§ط±ط§طھ|shortcut|shortcuts)', goal, re.I))
        is_whatsapp = bool(re.search(r'(?:whatsapp|ظˆط§طھط³ط§ط¨|ظˆط§طھط³|ط±ط³ط§ظ„ط©|ط§ط±ط³ظ„ ظ„ظ€|ط´ط§طھ)', goal, re.I))
        is_voice = bool(re.search(r'\b(طµظˆطھ|طھط­ط¯ط«|ظ†ط·ظ‚|ط§ظ†ط·ظ‚|طھظƒظ„ظ…|audio|voice|speech|tts|stt|whisper)\b', goal, re.I)) and not is_ios and not is_telephony
        is_coding = bool(re.search(r'\b(ظƒظˆط¯|ط¨ط±ظ…ط¬ط©|ط¯ط§ظ„ط©|ط§ط®طھط¨ط§ط±|ظپط­طµ ط§ظ„ظƒظˆط¯|طµظ„ط­|ط£طµظ„ط­|fix|test|debug|ast|patch|refactor|python|code|repo_map)\b', goal, re.I))
        is_graphics = bool(re.search(r'\b(ط±ط³ظ…|ط¬ط±ط§ظپظٹظƒ|ظ…ط®ط·ط·|ط¯ظٹط§ط¬ط±ط§ظ…|diagram|mermaid|svg|canvas|ظˆط§ط¬ظ‡ط©|طھطµظ…ظٹظ…|flowchart|dashboard)\b', goal, re.I))
        is_computer = bool(re.search(r'\b(ط§ظپطھط­ ط¨ط±ظ†ط§ظ…ط¬|ط´ط؛ظ„ طھط·ط¨ظٹظ‚|ظ…ظ„ظپ|ظ…ظپظƒط±ط©|notepad|calc|ط³ط·ط­ ط§ظ„ظ…ظƒطھط¨|ظˆظ†ط¯ظˆط²)\b', goal, re.I))
        is_browser = bool(re.search(r'\b(طھطµظپط­|ظ…ظˆظ‚ط¹|ط±ط§ط¨ط·|ط§ط¨ط­ط« ط¹ظ†|google|chrome|url|http|ظƒط§ط¨طھط´ط§|طµظپط­ط©|ظٹظˆطھظٹظˆط¨|ظ…طھطµظپط­ ط³ط­ط§ط¨ظٹ|ط³ط­ط§ط¨ظٹ)\b', goal, re.I))

        # 0. iOS Lane Plan
        if is_ios:
            if any(k in goal.lower() for k in ["طھط­ط¯ط«", "ظ‚ظ„", "ط§ظ†ط·ظ‚", "speak", "say"]):
                intent = "speak"
                desc = "ظ†ط·ظ‚ ظ†طµ طµظˆطھظٹ ط¹ط¨ط± Siri ط¹ظ„ظ‰ ط§ظ„ط¢ظٹظپظˆظ†"
            elif any(k in goal.lower() for k in ["ط¥ط´ط¹ط§ط±", "ط§ط´ط¹ط§ط±", "طھظ†ط¨ظٹظ‡", "notify", "notification"]):
                intent = "notify"
                desc = "ط¥ط±ط³ط§ظ„ ط¥ط´ط¹ط§ط± ظپظˆط±ظٹ ط¥ظ„ظ‰ ط¬ظ‡ط§ط² ط§ظ„ط¢ظٹظپظˆظ†"
            elif any(k in goal.lower() for k in ["ط§ط®طھطµط§ط±", "shortcut"]):
                intent = "shortcut"
                desc = "طھط´ط؛ظٹظ„ ط§ط®طھطµط§ط± ط¢ط¨ظ„ ظ…ط­ط¯ط¯ ط¹ظ„ظ‰ ط§ظ„ط¢ظٹظپظˆظ†"
            elif any(k in goal.lower() for k in ["ط§ظ†ظ‚ط±", "ط§ط¶ط؛ط·", "ظ„ظ…ط³", "tap", "touch"]):
                intent = "tap"
                desc = "ظ…ط­ط§ظƒط§ط© ظ„ظ…ط³ ظˆظ†ظ‚ط± ط¹ظ„ظ‰ ط´ط§ط´ط© ط§ظ„ط¢ظٹظپظˆظ†"
            elif any(k in goal.lower() for k in ["ظ‡ظˆظ…", "home"]):
                intent = "home"
                desc = "ط§ظ„ط¶ط؛ط· ط¹ظ„ظ‰ ط²ط± ط§ظ„ط´ط§ط´ط© ط§ظ„ط±ط¦ظٹط³ظٹط© ظپظٹ ط§ظ„ط¢ظٹظپظˆظ†"
            else:
                intent = "open_app"
                app_m = re.search(r'(?:طھط·ط¨ظٹظ‚|ط¨ط±ظ†ط§ظ…ط¬|open|app)\s+([a-zA-Z0-9_\-\u0621-\u064A]+)', goal)
                app_name = app_m.group(1) if app_m else "Safari"
                desc = f"ظپطھط­ طھط·ط¨ظٹظ‚ {app_name} ط¹ظ„ظ‰ ط¬ظ‡ط§ط² ط§ظ„ط¢ظٹظپظˆظ†"

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
                description="طھظˆظ„ظٹط¯ ظˆظ†ط·ظ‚ ط§ظ„ظ…ط®ط±ط¬ط§طھ ط§ظ„طµظˆطھظٹط© ط¹ط¨ط± Voice Lane"
            ))

        # 0.6 Mobile Smartphone Lane Plan (Android / Cross-Platform)
        elif is_mobile:
            if any(k in goal.lower() for k in ["ط§ظ†ظ‚ط±", "ط§ط¶ط؛ط·", "ظ„ظ…ط³", "tap"]):
                intent = "tap"
                desc = "ط§ظ„ظ†ظ‚ط± ط¹ظ„ظ‰ ط´ط§ط´ط© ط§ظ„ط¬ظˆط§ظ„"
            elif any(k in goal.lower() for k in ["ط³ط­ط¨", "طھظ…ط±ظٹط±", "swipe", "scroll"]):
                intent = "swipe"
                desc = "طھظ…ط±ظٹط± ظˆط³ط­ط¨ ط´ط§ط´ط© ط§ظ„ط¬ظˆط§ظ„"
            elif any(k in goal.lower() for k in ["ط±ط³ط§ظ„ط©", "sms"]):
                intent = "sms"
                desc = "ط¥ط±ط³ط§ظ„ ط±ط³ط§ظ„ط© SMS ط¹ط¨ط± ط§ظ„ط¬ظˆط§ظ„"
            elif any(k in goal.lower() for k in ["ط§طھطµظ„", "ظ…ظƒط§ظ„ظ…ط©", "dial"]):
                intent = "dial"
                desc = "ط¥ط¬ط±ط§ط، ظ…ظƒط§ظ„ظ…ط© ظ‡ط§طھظپظٹط© ط¹ط¨ط± ط§ظ„ط¬ظˆط§ظ„"
            else:
                intent = "launch_app"
                desc = f"ط§ظ„طھط­ظƒظ… ظˆطھط´ط؛ظٹظ„ ط§ظ„طھط·ط¨ظٹظ‚ ط¹ظ„ظ‰ ط§ظ„ط¬ظˆط§ظ„: {goal}"

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
            if any(k in goal.lower() for k in ["ط§ط¬طھظ…ط§ط¹", "meeting", "zoom", "meet", "teams"]):
                intent = "meeting"
                desc = "ط¥ظ†ط´ط§ط، ط±ط§ط¨ط· ط§ط¬طھظ…ط§ط¹ ط§ظپطھط±ط§ط¶ظٹ ط¹ط¨ط± Telephony Lane"
            elif any(k in goal.lower() for k in ["astra", "طھظپط§ط¹ظ„ طµظˆطھظٹ", "ظ…ط­ط§ط¯ط«ط©"]):
                intent = "astra_session"
                desc = "ط¨ط¯ط، ط¬ظ„ط³ط© ط­ظˆط§ط±ظٹط© طµظˆطھظٹط© ظپظˆط±ظٹط© ظپط§ط¦ظ‚ط© ط§ظ„ط°ظƒط§ط، (Astra)"
            else:
                intent = "dial"
                desc = f"ط¥ط¬ط±ط§ط، ط§طھطµط§ظ„ ظ‡ط§طھظپظٹ ط¹ط¨ط± ط´ط¨ظƒط© ط§ظ„ط§طھطµط§ظ„: {goal}"

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
            if any(k in goal.lower() for k in ["latex", "ظ„ط§طھظƒط³"]):
                intent = "latex"
                desc = "طھظˆظ„ظٹط¯ ظˆطھظ†ط³ظٹظ‚ ظˆط±ظ‚ط© ط¨ط­ط«ظٹط© ط¹ظ„ظ…ظٹط© ط¨طµظٹط؛ط© LaTeX"
            elif any(k in goal.lower() for k in ["ط¯ط±ط§ط³ط©", "ظ…ط±ط§ط¬ط¹ط©", "review", "survey"]):
                intent = "review"
                desc = "طھظˆظ„ظٹط¯ ظ…ط±ط§ط¬ط¹ط© ط£ط¯ط¨ظٹط§طھ ط´ط§ظ…ظ„ط© ظˆظ…طµظپظˆظپط© ظ…ظ‚ط§ط±ظ†ط© ط¹ظ„ظ…ظٹط©"
            elif any(k in goal.lower() for k in ["ظ…ط±ط§ط¬ط¹", "bibtex", "cite"]):
                intent = "bibtex"
                desc = "ط§ط³طھط®ط±ط§ط¬ ظˆطھظ†ط³ظٹظ‚ ط§ظ„ط§ط³طھط´ظ‡ط§ط¯ط§طھ ط§ظ„ط£ظƒط§ط¯ظٹظ…ظٹط© ظˆطµظٹط؛ط© BibTeX"
            elif any(k in goal.lower() for k in ["ط¥ط­طµط§ط،", "ط§ط­طµط§ط،", "ط¯ظ„ط§ظ„ط©", "p-value", "t-test"]):
                intent = "stats"
                desc = "ط§ظ„طھط­ظ‚ظ‚ ظ…ظ† ط§ظ„ط¯ظ„ط§ظ„ط© ط§ظ„ط¥ط­طµط§ط¦ظٹط© ظˆط§ظ„ط±طµط§ظ†ط© ط§ظ„ظ…ظ†ظ‡ط¬ظٹط© ظ„ظ„طھط¬ط±ط¨ط©"
            else:
                intent = "search"
                desc = f"ط§ظ„ط¨ط­ط« ط§ظ„ط£ظƒط§ط¯ظٹظ…ظٹ ط§ظ„ظ…ظˆط³ط¹ ظپظٹ ArXiv ظˆط§ظ„ط£ظˆط±ط§ظ‚ ط§ظ„ظ…ط­ظƒظ…ط©: {goal}"

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
            if any(k in goal.lower() for k in ["ط¨ظˆط±ط¨ظˆظٹظ†طھ", "ط¨ط§ظˆط±ط¨ظˆظٹظ†طھ", "ط¨ظˆط±ط¨ظˆظ†طھ", "ppt", "pptx", "presentation", "slides"]):
                intent = "ppt"
                desc = "ط¥ظ†ط´ط§ط، ظˆطھظ†ط³ظٹظ‚ ط¹ط±ط¶ طھظ‚ط¯ظٹظ…ظٹ ظ…طھظƒط§ظ…ظ„ ط¨طµظٹط؛ط© PowerPoint (.pptx)"
            elif any(k in goal.lower() for k in ["ط§ظƒط³ظ„", "ط¥ظƒط³ظ„", "excel", "xlsx", "csv", "spreadsheet", "financial_model", "ظ…ط¹ط§ط¯ظ„ط©"]):
                intent = "excel"
                desc = "ط¨ظ†ط§ط، ظ†ظ…ظˆط°ط¬ ظ…ط§ظ„ظٹ ظˆظ…طµظ†ظپ ط¨ظٹط§ظ†ط§طھ ط¨طµظٹط؛ط© Excel (.xlsx)"
            else:
                intent = "word"
                desc = "طھط£ظ„ظٹظپ ظˆطھظ†ط³ظٹظ‚ ظ…ط³طھظ†ط¯ ط±ط³ظ…ظٹ ظ…طھظƒط§ظ…ظ„ ط¨طµظٹط؛ط© Microsoft Word (.docx)"

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
            if any(k in goal.lower() for k in ["test", "ط§ط®طھط¨ط§ط±", "ط´ط؛ظ„ ط§ظ„ط§ط®طھط¨ط§ط±ط§طھ"]):
                intent = "test"
                desc = "طھط´ط؛ظٹظ„ ط­ط²ظ…ط© ط§ظ„ط§ط®طھط¨ط§ط±ط§طھ ظˆظپط­طµ ط­ط§ظ„ط© ط§ظ„ط£ظƒظˆط§ط¯"
            elif any(k in goal.lower() for k in ["debug", "طµظ„ط­", "ط£طµظ„ط­", "fix", "repair"]):
                intent = "debug"
                desc = "ط¯ظˆط±ط© ط§ظ„ط¥طµظ„ط§ط­ ط§ظ„ط°ط§طھظٹ ظˆطھط´ط®ظٹطµ ظˆطھطµط­ظٹط­ ط§ظ„ط£ط®ط·ط§ط،"
            elif any(k in goal.lower() for k in ["repo_map", "ط®ط±ظٹط·ط©", "map"]):
                intent = "repo_map"
                desc = "ط¨ظ†ط§ط، ط®ط±ظٹط·ط© ط§ظ„ط±ظ…ظˆط² ظˆط§ظ„ط¹ظ„ط§ظ‚ط§طھ ظپظٹ ط§ظ„ظ…ط³طھظˆط¯ط¹"
            else:
                intent = "analyze"
                desc = "ط§ظ„طھط­ظ„ظٹظ„ ط§ظ„ط§ط³طھظ†طھط§ط¬ظٹ ظ„ظ„ط´ظپط±ط© ط§ظ„ط¨ط±ظ…ط¬ظٹط© ظˆط¨ظ†ط§ط، ط´ط¬ط±ط© AST"

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
                desc = "طھظˆظ„ظٹط¯ ط±ط³ظ… ط´ط¹ط§ط¹ظٹ SVG ط¹ط§ظ„ظٹ ط§ظ„ط¯ظ‚ط©"
            elif any(k in goal.lower() for k in ["canvas", "dashboard", "ظ„ظˆط­ط©"]):
                intent = "canvas"
                desc = "طھظˆظ„ظٹط¯ ظˆط§ط¬ظ‡ط© HTML5/Canvas طھظپط§ط¹ظ„ظٹط© ط­ظٹط©"
            else:
                intent = "diagram"
                desc = "طھظˆظ„ظٹط¯ ظ…ط®ط·ط· ظ‡ظٹظƒظ„ظٹ ظ…ط¹ظ…ط§ط±ظٹ ط¨طµط±ظٹ (Mermaid)"

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
            target_match = re.search(r'(?:ط¥ظ„ظ‰|ظ„ظ€|ط±ظ‚ظ…|to)\s+([0-9\+\-\s]+|[^\s,]+)', goal)
            msg_match = re.search(r'(?:ظ†طµ|ط±ط³ط§ظ„ط©|message)\s*[:=]?\s*["\']?([^"\'\n]+)', goal)
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
                description=f"ط¥ط±ط³ط§ظ„ ط±ط³ط§ظ„ط© ظˆط§طھط³ط§ط¨ ط¥ظ„ظ‰ {recipient}"
            ))

        # 4. Desktop Computer Lane Plan
        elif is_computer:
            app_match = re.search(r'(?:ط¨ط±ظ†ط§ظ…ط¬|طھط·ط¨ظٹظ‚|launch|run|open)\s+([a-zA-Z0-9_\-\.]+)', goal, re.I)
            app_name = app_match.group(1) if app_match else "notepad.exe"
            steps.append(Step(
                step_id=1,
                lane="computer",
                intent="launch_app",
                target=Target(kind="app_name", ref=app_name),
                expected_postconditions=[{"type": "process_running", "name": app_name}],
                risk_level="low",
                description=f"طھط´ط؛ظٹظ„ طھط·ط¨ظٹظ‚ ط§ظ„ظ†ط¸ط§ظ…: {app_name}"
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
                    description=f"ط§ظ„طھظ†ظ‚ظ„ ط¥ظ„ظ‰ ط§ظ„ط±ط§ط¨ط· {target_url}"
                ))
            else:
                query_clean = re.sub(r'^(?:ط§ط¨ط­ط« ط¹ظ†|ط¨ط­ط« ط¹ظ†|search for|find|google)\s*', '', goal, flags=re.I).strip()
                steps.append(Step(
                    step_id=1,
                    lane="browser",
                    intent="search_and_assess",
                    target=Target(kind="semantic", ref=query_clean),
                    value=query_clean,
                    expected_postconditions=[{"type": "dom_state_changed"}],
                    risk_level="low",
                    description=f"ط§ظ„ط¨ط­ط« ظˆط§ظ„ط§ط³طھظƒط´ط§ظپ ط§ظ„ط°ظƒظٹ ظ„ظ„ظ‡ط¯ظپ: {query_clean}"
                ))

        # 6. Advanced Reasoning / Council Lane Plan
        else:
            if "tot" in goal.lower() or "ط´ط¬ط±ط©" in goal.lower():
                intent = "tot"
                desc = f"ط§ط³طھظƒط´ط§ظپ ط´ط¬ط±ط© ط§ظ„ط£ظپظƒط§ط± (Tree of Thoughts) ظ„ظ„ظ‡ط¯ظپ: {goal[:40]}"
            elif "got" in goal.lower() or "ط´ط¨ظƒط©" in goal.lower():
                intent = "got"
                desc = f"ط¨ظ†ط§ط، ط´ط¨ظƒط© ط§ظ„ط£ظپظƒط§ط± ط§ظ„ظ…طھط¯ط§ط®ظ„ط© (Graph of Thoughts) ظ„ظ„ظ‡ط¯ظپ: {goal[:40]}"
            elif "reflexion" in goal.lower() or "طھط£ظ…ظ„" in goal.lower():
                intent = "reflexion"
                desc = f"ط§ظ„طھظپظƒظٹط± ط§ظ„طھط£ظ…ظ„ظٹ ط§ظ„ط§ط³طھط±ط¬ط§ط¹ظٹ (Reflexion) ظ„ظ„ظ‡ط¯ظپ: {goal[:40]}"
            elif "mcts" in goal.lower():
                intent = "mcts"
                desc = f"ظ…ط­ط§ظƒط§ط© ظ…ظˆظ†طھ ظƒط§ط±ظ„ظˆ ظ„ظ„ط£ط´ط¬ط§ط± (MCTS) ظ„ظ„ظ‡ط¯ظپ: {goal[:40]}"
            else:
                intent = "council_evaluate"
                desc = f"طھط­ظ„ظٹظ„ ط§ظ„ظ…ط³ط£ظ„ط© ط¹ط¨ط± ظ…ط¬ظ„ط³ ط§ظ„ط°ظƒط§ط، ظˆط§ظ„طھظپظƒظٹط± ط§ظ„ظ…ط¹ظ…ظ‚: {goal[:40]}"

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

