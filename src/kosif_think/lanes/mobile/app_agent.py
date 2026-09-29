"""
AppAgent & Mobile-Agent Autonomous Mobile Engine for KOSIF Think.
Inspired by Tencent AppAgent, X-PLUG Mobile-Agent, and UI-TARS:
- Set-of-Marks mobile visual element grounding from UIAutomator
- Sub-goal planning and multi-screen trajectory synthesis
- Screen state memory graph (ScreenStateNode) for tracking navigation history
- Auto-recovery from system dialogs, permissions, and app popups
"""

from typing import Dict, Any, List, Optional, Tuple
import time
import re
from .android import AndroidController

class ScreenStateNode:
    def __init__(self, screen_id: str, app_package: str, elements: List[Dict[str, Any]]):
        self.screen_id = screen_id
        self.app_package = app_package
        self.elements = elements
        self.visited_count = 1
        self.transitions: Dict[str, str] = {}  # action -> next_screen_id


class AppAgentOrchestrator:
    """Orchestrates multi-step autonomous smartphone exploration and execution."""

    def __init__(self, android_controller: Optional[AndroidController] = None):
        self.android = android_controller or AndroidController()
        self.screen_memory: Dict[str, ScreenStateNode] = {}
        self.action_history: List[Dict[str, Any]] = []

    def plan_subgoals_for_app(self, goal: str, app_name: str) -> List[Dict[str, Any]]:
        """Decomposes high-level smartphone user goal into sequential UI actions."""
        subgoals = []

        # Step 1: Ensure target app is launched and in foreground
        subgoals.append({
            "step": 1,
            "intent": "launch_app",
            "target": app_name,
            "description": f"Launch {app_name} on mobile device"
        })

        # Step 2: Handle permissions/popups if emerging
        subgoals.append({
            "step": 2,
            "intent": "dismiss_popups",
            "target": "allow|accept|continue",
            "description": "Auto-dismiss any modal permission or update dialogs"
        })

        # Step 3: Domain action
        if any(k in goal.lower() or k in app_name.lower() for k in ["message", "send", "report", "chat", "رسالة", "واتس", "whatsapp"]):
            subgoals.append({
                "step": 3,
                "intent": "locate_and_type",
                "target": "search_contact",
                "value": "Recipient Name",
                "description": "Locate chat contact and open dialogue"
            })
            subgoals.append({
                "step": 4,
                "intent": "input_text",
                "target": "message_input",
                "value": goal,
                "description": "Type message and tap Send button"
            })
        elif any(k in goal.lower() or k in app_name.lower() for k in ["call", "اتصل", "مكالمة", "phone", "dial"]):
            subgoals.append({
                "step": 3,
                "intent": "dial_call",
                "target": "dialer",
                "value": re.sub(r'[^0-9\+]', '', goal),
                "description": "Dial phone number directly"
            })
        else:
            subgoals.append({
                "step": 3,
                "intent": "locate_and_click",
                "target": goal,
                "description": f"Ground and tap element matching '{goal}'"
            })

        return subgoals

    def record_screen_state(self, screen_id: str, app_package: str, elements: List[Dict[str, Any]]) -> ScreenStateNode:
        """Records a screen state node in the memory graph."""
        if screen_id in self.screen_memory:
            node = self.screen_memory[screen_id]
            node.visited_count += 1
            node.elements = elements
            return node
        node = ScreenStateNode(screen_id, app_package, elements)
        self.screen_memory[screen_id] = node
        return node

    def record_screen_transition(self, current_screen: str, action: str, next_screen: str, elements: List[Dict[str, Any]]):
        """Builds app state transition graph in memory."""
        node = self.screen_memory.setdefault(current_screen, ScreenStateNode(current_screen, "active_app", elements))
        node.transitions[action] = next_screen
        self.screen_memory.setdefault(next_screen, ScreenStateNode(next_screen, "active_app", elements))

    def auto_dismiss_dialogs(self) -> Dict[str, Any]:
        """Detects and automatically dismisses standard Android system popups."""
        keywords = ["allow", "while using the app", "agree", "ok", "got it", "dismiss", "close", "موافق", "سماح"]
        dismissed = False
        for kw in keywords:
            ground = self.android.dump_and_find_element(kw)
            if ground.get("found") and not ground.get("simulated"):
                self.android.tap(ground["center_x"], ground["center_y"])
                dismissed = True
                break

        return {"dismissed": dismissed, "status": "ok"}
