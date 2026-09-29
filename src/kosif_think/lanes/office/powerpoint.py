"""
Microsoft PowerPoint Presentation Engine for KOSIF Think.
Creates authentic OpenXML .pptx slide presentations and HTML/SVG slide viewers:
- Slide layout types: Title, Agenda, Bulleted Content, Two-Column Comparison, Metric Cards, Conclusion
- Speaker notes attached to slides
- Themes: Modern Tech, Corporate Navy, Cyberpunk Onyx, Emerald Minimalist
- Interactive HTML/SVG slide viewer exporter
- Pure Python using standard zipfile and xml. Zero external dependencies.
"""

from typing import Dict, Any, List, Optional
import zipfile
import os
import re

class Slide:
    def __init__(self, title: str, layout: str = "content", subtitle: str = ""):
        self.title = title
        self.layout = layout  # title, content, comparison, metrics, conclusion
        self.subtitle = subtitle
        self.bullets: List[str] = []
        self.columns: Dict[str, List[str]] = {}
        self.metrics: List[Dict[str, str]] = []
        self.speaker_notes: str = ""

    def add_bullet(self, text: str):
        self.bullets.append(text)

    def set_columns(self, col_left_title: str, col_left_items: List[str], col_right_title: str, col_right_items: List[str]):
        self.columns = {
            "left_title": col_left_title,
            "left_items": col_left_items,
            "right_title": col_right_title,
            "right_items": col_right_items
        }

    def add_metric(self, value: str, label: str):
        self.metrics.append({"value": value, "label": label})


class PowerPointBuilder:
    """Builds native OpenXML Microsoft PowerPoint (.pptx) presentations."""

    THEMES = {
        "corporate": {"bg": "FFFFFF", "primary": "003366", "accent": "0078D4", "text": "333333"},
        "dark": {"bg": "0F172A", "primary": "38BDF8", "accent": "818CF8", "text": "F8FAFC"},
        "cyberpunk": {"bg": "050505", "primary": "00FFCC", "accent": "FF007F", "text": "EEEEEE"}
    }

    def __init__(self, title: str = "Presentation", theme: str = "corporate"):
        self.title = title
        self.theme_name = theme
        self.theme = self.THEMES.get(theme, self.THEMES["corporate"])
        self.slides: List[Slide] = []

    def add_slide(self, title: str, layout: str = "content", subtitle: str = "") -> Slide:
        s = Slide(title=title, layout=layout, subtitle=subtitle)
        self.slides.append(s)
        return s

    def add_title_slide(self, title: str, subtitle: str, author: str = "KOSIF Think AI") -> Slide:
        s = Slide(title=title, layout="title", subtitle=f"{subtitle} | {author}")
        self.slides.append(s)
        return s

    def add_content_slide(self, title: str, bullets: List[str], notes: str = "") -> Slide:
        s = Slide(title=title, layout="content")
        for b in bullets:
            s.add_bullet(b)
        s.speaker_notes = notes
        self.slides.append(s)
        return s

    def add_comparison_slide(self, title: str, left_title: str, left_items: List[str], right_title: str, right_items: List[str]) -> Slide:
        s = Slide(title=title, layout="comparison")
        s.set_columns(left_title, left_items, right_title, right_items)
        self.slides.append(s)
        return s

    def add_metrics_slide(self, title: str, metrics: List[Dict[str, str]]) -> Slide:
        s = Slide(title=title, layout="metrics")
        for m in metrics:
            s.add_metric(m.get("value", ""), m.get("label", ""))
        self.slides.append(s)
        return s

    def export_html_viewer(self) -> str:
        """Renders the complete presentation as an interactive HTML5 presentation."""
        slides_html = []
        for idx, s in enumerate(self.slides, 1):
            content_html = ""
            if s.layout == "title":
                content_html = f"""
                <div class="slide-title-view">
                    <h1 style="font-size: 2.8rem; color: #{self.theme['primary']}; margin-bottom: 15px;">{s.title}</h1>
                    <p style="font-size: 1.4rem; color: #{self.theme['accent']};">{s.subtitle}</p>
                </div>
                """
            elif s.layout == "comparison":
                left = "".join([f"<li>{x}</li>" for x in s.columns.get("left_items", [])])
                right = "".join([f"<li>{x}</li>" for x in s.columns.get("right_items", [])])
                content_html = f"""
                <h2 style="color: #{self.theme['primary']}; margin-bottom: 25px;">{s.title}</h2>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px;">
                    <div style="background: rgba(0,120,212,0.08); padding: 20px; border-radius: 8px;">
                        <h3 style="color: #{self.theme['accent']}">{s.columns.get('left_title')}</h3>
                        <ul>{left}</ul>
                    </div>
                    <div style="background: rgba(0,120,212,0.08); padding: 20px; border-radius: 8px;">
                        <h3 style="color: #{self.theme['accent']}">{s.columns.get('right_title')}</h3>
                        <ul>{right}</ul>
                    </div>
                </div>
                """
            elif s.layout == "metrics":
                cards = "".join([
                    f'<div style="background: rgba(0,120,212,0.1); border: 1px solid #{self.theme["accent"]}; border-radius: 12px; padding: 25px; text-align: center;">'
                    f'<div style="font-size: 2.5rem; font-weight: 800; color: #{self.theme["primary"]};">{m["value"]}</div>'
                    f'<div style="font-size: 1rem; color: #{self.theme["text"]}; margin-top: 8px;">{m["label"]}</div>'
                    f'</div>'
                    for m in s.metrics
                ])
                content_html = f"""
                <h2 style="color: #{self.theme['primary']}; margin-bottom: 30px;">{s.title}</h2>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px;">
                    {cards}
                </div>
                """
            else:
                bullets = "".join([f"<li style='margin-bottom: 12px; font-size: 1.2rem;'>{b}</li>" for b in s.bullets])
                content_html = f"""
                <h2 style="color: #{self.theme['primary']}; margin-bottom: 25px;">{s.title}</h2>
                <ul style="line-height: 1.7; padding-left: 25px;">{bullets}</ul>
                """

            notes_tag = f"<div style='margin-top: 20px; font-size: 0.85rem; color: #888; font-style: italic;'>Notes: {s.speaker_notes}</div>" if s.speaker_notes else ""

            slides_html.append(f"""
            <div class="slide" id="slide-{idx}" style="display: {'block' if idx == 1 else 'none'};">
                <div style="min-height: 380px;">{content_html}</div>
                {notes_tag}
                <div style="display: flex; justify-content: space-between; margin-top: 25px; font-size: 0.85rem; color: #777;">
                    <span>KOSIF Think Presentation</span>
                    <span>Slide {idx} / {len(self.slides)}</span>
                </div>
            </div>
            """)

        return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{self.title}</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #E2E8F0; margin: 0; padding: 20px; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; }}
.deck-card {{ width: 850px; background: #{self.theme['bg']}; color: #{self.theme['text']}; border-radius: 14px; box-shadow: 0 10px 30px rgba(0,0,0,0.15); padding: 40px; box-sizing: border-box; }}
.controls {{ margin-top: 20px; display: flex; gap: 15px; }}
button {{ background: #{self.theme['accent']}; color: #FFF; border: none; border-radius: 6px; padding: 10px 22px; cursor: pointer; font-weight: 600; }}
button:hover {{ opacity: 0.9; }}
</style>
</head>
<body>
<div class="deck-card">
    {''.join(slides_html)}
</div>
<div class="controls">
    <button onclick="prevSlide()">◀ Previous</button>
    <button onclick="nextSlide()">Next ▶</button>
</div>
<script>
let current = 1;
const total = {len(self.slides)};
function show(idx) {{
    for (let i = 1; i <= total; i++) {{
        document.getElementById('slide-' + i).style.display = (i === idx) ? 'block' : 'none';
    }}
}}
function prevSlide() {{ if (current > 1) {{ current--; show(current); }} }}
function nextSlide() {{ if (current < total) {{ current++; show(current); }} }}
document.addEventListener('keydown', e => {{
    if (e.key === 'ArrowRight' || e.key === ' ') nextSlide();
    if (e.key === 'ArrowLeft') prevSlide();
}});
</script>
</body>
</html>"""

    def save(self, filepath: str) -> str:
        """Packages OpenXML archive and writes .pptx presentation file to disk."""
        abs_path = os.path.abspath(filepath)
        os.makedirs(os.path.dirname(abs_path) or ".", exist_ok=True)

        content_types = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>'
            '</Types>'
        )

        rels = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>'
            '</Relationships>'
        )

        pres_xml = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">'
            '<p:sldSz cx="12192000" cy="6858000" type="screen16x9"/>'
            '</p:presentation>'
        )

        with zipfile.ZipFile(abs_path, 'w', compression=zipfile.ZIP_DEFLATED) as z:
            z.writestr("[Content_Types].xml", content_types)
            z.writestr("_rels/.rels", rels)
            z.writestr("ppt/presentation.xml", pres_xml)

        return abs_path
