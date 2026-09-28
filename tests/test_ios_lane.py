import unittest
import asyncio
from kosif_think.lanes.ios.shortcuts_bridge import ShortcutsBridge
from kosif_think.lanes.ios.wda_client import WDAClient
from kosif_think.lanes.ios.engine import IOSLane
from kosif_think.core.planner import TaskPlanner, Step
from kosif_think.core.preflight import PreflightGate

class TestIOSLane(unittest.TestCase):
    def setUp(self):
        self.bridge = ShortcutsBridge()
        self.wda = WDAClient()
        self.lane = IOSLane()
        self.planner = TaskPlanner()
        self.preflight = PreflightGate()

    def test_open_app_enqueue(self):
        res = self.bridge.open_app("Notes")
        self.assertEqual(res["status"], "enqueued")
        self.assertEqual(res["action"], "open_url_scheme")

        # Verify polling
        pending = self.bridge.poll_pending_actions()
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0]["params"]["url"], "mobilenotes://")

    def test_siri_speak_text(self):
        res = self.bridge.speak_text("تم إنجاز المهمة بنجاح")
        self.assertEqual(res["status"], "enqueued")
        self.assertEqual(res["action"], "speak_text")

    def test_wda_simulated_tap(self):
        res = self.wda.tap(150, 300)
        self.assertEqual(res["action"], "tap")
        self.assertEqual(res["x"], 150)

    def test_ios_lane_dispatch(self):
        step = Step(step_id=1, lane="ios", intent="open_app", value="Safari")
        res = asyncio.run(self.lane.dispatch_step(step))
        self.assertEqual(res["lane"], "ios")
        self.assertEqual(res["target_app"], "Safari")

    def test_planner_detects_iphone_goal(self):
        req = self.preflight.run_preflight("افتح تطبيق الملاحظات على الآيفون")
        plan = self.planner.create_plan(req)
        self.assertEqual(plan.steps[0].lane, "ios")
        self.assertEqual(plan.steps[0].intent, "open_app")

if __name__ == "__main__":
    unittest.main()
