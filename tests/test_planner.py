import unittest
from kosif_think.core.preflight import PreflightGate
from kosif_think.core.planner import TaskPlanner

class TestPlanner(unittest.TestCase):
    def setUp(self):
        self.preflight = PreflightGate()
        self.planner = TaskPlanner()

    def test_browser_goal_planning(self):
        req = self.preflight.run_preflight("ابحث عن هواتف سامسونج")
        plan = self.planner.create_plan(req)
        self.assertEqual(len(plan.steps), 1)
        self.assertEqual(plan.steps[0].lane, "browser")
        self.assertEqual(plan.steps[0].intent, "search_and_assess")

    def test_whatsapp_goal_planning(self):
        req = self.preflight.run_preflight("ارسل رسالة واتساب إلى 0555555555 نص: السلام عليكم")
        plan = self.planner.create_plan(req)
        self.assertEqual(plan.steps[0].lane, "whatsapp")
        self.assertEqual(plan.steps[0].intent, "send_message")

    def test_computer_goal_planning(self):
        req = self.preflight.run_preflight("افتح برنامج notepad")
        plan = self.planner.create_plan(req)
        self.assertEqual(plan.steps[0].lane, "computer")
        self.assertEqual(plan.steps[0].intent, "launch_app")

if __name__ == "__main__":
    unittest.main()
