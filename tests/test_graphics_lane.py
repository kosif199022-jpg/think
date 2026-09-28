import unittest
import asyncio
from kosif_think.lanes.graphics.svg_builder import SVGBuilder
from kosif_think.lanes.graphics.diagrams import DiagramSynthesizer
from kosif_think.lanes.graphics.generative_canvas import GenerativeCanvas
from kosif_think.lanes.graphics.visual_analyzer import VisualLayoutAnalyzer
from kosif_think.lanes.graphics.engine import GraphicsLane
from kosif_think.core.planner import Step

class TestGraphicsLane(unittest.TestCase):
    def setUp(self):
        self.svg = SVGBuilder(width=400, height=300)
        self.diagrams = DiagramSynthesizer()
        self.canvas = GenerativeCanvas()
        self.analyzer = VisualLayoutAnalyzer()
        self.lane = GraphicsLane()

    def test_svg_rendering(self):
        self.svg.add_card(10, 10, 380, 200, "Core Service", "Execution Hub")
        markup = self.svg.render()
        self.assertTrue(markup.startswith("<svg"))
        self.assertTrue(markup.endswith("</svg>"))
        self.assertIn("Core Service", markup)

    def test_diagram_synthesis(self):
        nodes = [
            {"id": "A", "label": "Client", "next": "B"},
            {"id": "B", "label": "Server"}
        ]
        mermaid = self.diagrams.generate_flowchart("Test Flow", nodes)
        self.assertIn("flowchart TD", mermaid)
        self.assertIn("Client", mermaid)

    def test_canvas_dashboard(self):
        html = self.canvas.build_dashboard_widget("Telemetry", [{"label": "CPU", "value": "12%"}], [10, 12, 15])
        self.assertIn("<canvas", html)
        self.assertIn("Telemetry", html)

    def test_layout_analyzer(self):
        elements = [
            {"rect": {"x": 0, "y": 0, "w": 100, "h": 50}},
            {"rect": {"x": 200, "y": 0, "w": 100, "h": 50}}
        ]
        res = self.analyzer.analyze_layout(elements)
        self.assertTrue(res["is_clean_layout"])
        self.assertEqual(res["detected_overlaps"], 0)

    def test_graphics_lane_dispatch(self):
        step = Step(step_id=1, lane="graphics", intent="svg", description="Widget Test")
        res = asyncio.run(self.lane.dispatch_step(step))
        self.assertEqual(res["status"], "ok")
        self.assertEqual(res["lane"], "graphics")
        self.assertIn("<svg", res["svg"])

if __name__ == "__main__":
    unittest.main()
