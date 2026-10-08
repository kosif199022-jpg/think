"""Regression checks for free browser-based Three.js KOSIF graphics scenes."""
import asyncio
import unittest

from kosif_think.core.planner import Step, TaskPlanner
from kosif_think.core.preflight import SanitizedRequest
from kosif_think.lanes.graphics.engine import GraphicsLane
from kosif_think.lanes.graphics.threejs_scene import build_space_scene


class TestFreeBrowserThreeJS(unittest.TestCase):
    def test_space_preview_is_client_side_webgl_not_mp4(self):
        page = build_space_scene("Space Motion", duration_seconds=5)
        self.assertIn("three@0.180.0", page)
        self.assertIn("new THREE.WebGLRenderer", page)
        self.assertIn('"duration": 5.0', page)
        self.assertIn("0.0 / 5.0", page.replace('"+cfg.duration.toFixed(1)+"', "5.0"))
        self.assertIn('id="replay"', page)

    def test_user_supplied_title_is_escaped(self):
        page = build_space_scene('<img src=x onerror=alert(1)>')
        self.assertIn("&lt;img", page)
        self.assertNotIn('<img src=x', page)

    def test_rejects_invalid_duration_and_dimensions(self):
        for seconds in (-1, 0, 31, float("nan")):
            with self.subTest(seconds=seconds):
                with self.assertRaises(ValueError):
                    build_space_scene(duration_seconds=seconds)
        with self.assertRaises(ValueError):
            build_space_scene(width=8)

    def test_graphics_lane_exposes_real_preview_capabilities(self):
        step = Step(step_id=1, lane="graphics", intent="threejs",
                    value={"duration_seconds": 5, "title": "KOSIF Space"})
        result = asyncio.run(GraphicsLane().dispatch_step(step))
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["format"], "html5_threejs")
        self.assertTrue(result["requires_webgl"])
        self.assertFalse(result["rendered_mp4"])

    def test_planner_routes_threejs_prompts_to_graphics(self):
        phrase = "اعمل فيديو 3D عن الفضاء"
        req = SanitizedRequest(task_id="space", raw_prompt=phrase, clean_goal=phrase)
        plan = TaskPlanner().create_plan(req)
        self.assertEqual(plan.steps[0].lane, "graphics")
        self.assertEqual(plan.steps[0].intent, "threejs")


if __name__ == "__main__":
    unittest.main()
