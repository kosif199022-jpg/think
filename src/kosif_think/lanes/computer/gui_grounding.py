"""
Multimodal GUI Element Grounding & Interactive Affordance Locator for KOSIF Think.
Inspired by OS-World, UI-TARS, and SeeClick.
Maps natural language user intents ("click submit", "enter username", "close popup")
to precise screen bounding boxes and target click coordinates (x, y).
Zero external dependencies. Pure Python.
"""

from typing import Dict, Any, List, Tuple, Optional
import time
import re

class UIElement:
    """Represents an interactive or visual GUI element on screen."""

    def __init__(
        self,
        element_id: str,
        role: str,
        text: str,
        bbox: Tuple[int, int, int, int],  # x1, y1, x2, y2
        is_enabled: bool = True,
        is_interactive: bool = True
    ):
        self.element_id = element_id
        self.role = role.lower()  # button, input, link, checkbox, window, icon
        self.text = text.strip()
        self.bbox = bbox
        self.is_enabled = is_enabled
        self.is_interactive = is_interactive

    @property
    def center(self) -> Tuple[int, int]:
        """Calculates center coordinates (cx, cy) for mouse click execution."""
        x1, y1, x2, y2 = self.bbox
        return ((x1 + x2) // 2, (y1 + y2) // 2)

    @property
    def width(self) -> int:
        return max(0, self.bbox[2] - self.bbox[0])

    @property
    def height(self) -> int:
        return max(0, self.bbox[3] - self.bbox[1])

    def to_dict(self) -> Dict[str, Any]:
        cx, cy = self.center
        return {
            "element_id": self.element_id,
            "role": self.role,
            "text": self.text,
            "bbox": list(self.bbox),
            "center": [cx, cy],
            "width": self.width,
            "height": self.height,
            "is_interactive": self.is_interactive
        }


class GUIGroundingEngine:
    """Grounds user intents onto GUI elements and calculates click targets."""

    def __init__(self, screen_width: int = 1920, screen_height: int = 1080):
        self.screen_width = screen_width
        self.screen_height = screen_height

    def extract_intent_keywords(self, instruction: str) -> Tuple[str, List[str]]:
        """Extracts desired action verb and target keywords from instruction."""
        clean = instruction.lower().strip()
        action = "click"
        if any(w in clean for w in ["type", "enter", "write", "input"]):
            action = "type"
        elif any(w in clean for w in ["scroll", "swipe"]):
            action = "scroll"
        elif any(w in clean for w in ["double click", "double-click"]):
            action = "double_click"

        # Remove common verbs to leave target descriptors
        clean_desc = re.sub(r"\b(?:click|press|tap|type|enter|on|the|a|an|into|button|field|icon)\b", " ", clean)
        keywords = [w for w in clean_desc.split() if len(w) > 1]
        return action, keywords

    def ground_element(
        self,
        instruction: str,
        elements: Optional[List[UIElement]] = None
    ) -> Dict[str, Any]:
        """Finds the best matching GUI element for the instruction and computes click target."""
        t0 = time.perf_counter()
        action, keywords = self.extract_intent_keywords(instruction)

        # Generate mock elements if none provided
        if not elements:
            elements = [
                UIElement("elem_search_input", "input", "Search or enter address", (300, 80, 1200, 120)),
                UIElement("elem_submit_btn", "button", "Submit", (1220, 80, 1340, 120)),
                UIElement("elem_login_btn", "button", "Log In", (1700, 80, 1820, 120)),
                UIElement("elem_cancel_btn", "button", "Cancel", (1000, 600, 1120, 640)),
                UIElement("elem_confirm_btn", "button", "Confirm Payment", (1140, 600, 1320, 640))
            ]

        best_elem: Optional[UIElement] = None
        best_score = -1.0

        for elem in elements:
            score = 0.0
            elem_text_lower = elem.text.lower()
            elem_role_lower = elem.role.lower()

            # Text match
            for kw in keywords:
                if kw in elem_text_lower:
                    score += 0.5
                if kw in elem.element_id.lower():
                    score += 0.3

            # Role match
            if action == "type" and elem_role_lower in ["input", "textbox", "textarea"]:
                score += 0.4
            elif action == "click" and elem_role_lower in ["button", "link", "icon"]:
                score += 0.3

            # Interactive bonus
            if elem.is_interactive:
                score += 0.1

            # Affordance check: ensure within screen bounds
            cx, cy = elem.center
            if 0 <= cx <= self.screen_width and 0 <= cy <= self.screen_height:
                score += 0.1

            if score > best_score:
                best_score = score
                best_elem = elem

        duration_ms = round((time.perf_counter() - t0) * 1000, 2)

        if best_elem and best_score > 0.2:
            cx, cy = best_elem.center
            return {
                "status": "grounded",
                "instruction": instruction,
                "action": action,
                "confidence": min(round(best_score, 2), 1.0),
                "target_coordinates": {"x": cx, "y": cy},
                "element": best_elem.to_dict(),
                "duration_ms": duration_ms
            }
        else:
            return {
                "status": "not_found",
                "instruction": instruction,
                "confidence": 0.0,
                "target_coordinates": None,
                "duration_ms": duration_ms
            }
