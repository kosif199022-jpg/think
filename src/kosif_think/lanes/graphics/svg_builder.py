"""
SVG Vector Graphics Builder for KOSIF Think.
Constructs responsive, high-resolution SVG diagrams, UI mockups, and charts programmatically.
"""

from typing import List, Dict, Any, Optional

class SVGBuilder:
    """Constructs valid SVG markup with CSS styling and component layout."""

    def __init__(self, width: int = 800, height: int = 600, bg_color: str = "#0f172a"):
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.elements: List[str] = []

    def add_rect(self, x: int, y: int, w: int, h: int, fill: str, stroke: str = "none", rx: int = 8) -> "SVGBuilder":
        self.elements.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
        )
        return self

    def add_text(self, x: int, y: int, text: str, font_size: int = 16, fill: str = "#f8fafc", weight: str = "normal", anchor: str = "start") -> "SVGBuilder":
        self.elements.append(
            f'<text x="{x}" y="{y}" fill="{fill}" font-size="{font_size}" font-weight="{weight}" text-anchor="{anchor}" font-family="system-ui, -apple-system, sans-serif">{text}</text>'
        )
        return self

    def add_line(self, x1: int, y1: int, x2: int, y2: int, stroke: str = "#64748b", width: int = 2, dashed: bool = False) -> "SVGBuilder":
        dash = ' stroke-dasharray="4,4"' if dashed else ''
        self.elements.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{width}"{dash}/>')
        return self

    def add_card(self, x: int, y: int, w: int, h: int, title: str, subtitle: str, badge: str = "Active", color: str = "#3b82f6") -> "SVGBuilder":
        """Adds a modern frosted glass UI card."""
        self.add_rect(x, y, w, h, fill="#1e293b", stroke="#334155", rx=12)
        # Accent bar
        self.add_rect(x, y, 6, h, fill=color, rx=3)
        self.add_text(x + 20, y + 32, title, font_size=18, weight="bold")
        self.add_text(x + 20, y + 60, subtitle, font_size=13, fill="#94a3b8")
        # Badge
        self.add_rect(x + w - 85, y + 16, 70, 24, fill=f"{color}22", stroke=color, rx=12)
        self.add_text(x + w - 50, y + 33, badge, font_size=11, fill=color, weight="bold", anchor="middle")
        return self

    def render(self) -> str:
        """Assembles and returns full SVG XML string."""
        content = "\n  ".join(self.elements)
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.width} {self.height}" width="{self.width}" height="{self.height}">\n'
            f'  <rect width="100%" height="100%" fill="{self.bg_color}"/>\n'
            f'  {content}\n'
            f'</svg>'
        )
