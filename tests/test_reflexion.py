import unittest
from kosif_think.lanes.reasoning.reflexion import ReflexionEngine

class TestReflexion(unittest.TestCase):
    def setUp(self):
        self.reflexion = ReflexionEngine()

    def test_reflection_on_failure_and_success(self):
        # 1. Failure reflection
        rec1 = self.reflexion.reflect_on_trial(
            trial_number=1,
            action_taken="click_button_by_text",
            observed_outcome="Element obscured by cookie modal",
            success=False,
            goal="Submit login form"
        )
        self.assertFalse(rec1.success)
        self.assertIn("Avoid repeating", rec1.lesson_learned)

        # 2. Advice retrieval
        advice = self.reflexion.get_context_advice("click_button_by_text")
        self.assertEqual(len(advice), 1)
        self.assertIn("Past Failure Insight", advice[0])

        # 3. Success reflection
        rec2 = self.reflexion.reflect_on_trial(
            trial_number=2,
            action_taken="dismiss_overlay_then_click",
            observed_outcome="Form submitted successfully",
            success=True,
            goal="Submit login form"
        )
        self.assertTrue(rec2.success)

if __name__ == "__main__":
    unittest.main()
