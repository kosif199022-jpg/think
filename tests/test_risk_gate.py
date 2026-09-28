import unittest
from kosif_think.core.planner import Step, Target
from kosif_think.core.risk_gate import RiskGate, RiskLevel, CheckpointRequired

class TestRiskGate(unittest.TestCase):
    def setUp(self):
        self.risk_gate = RiskGate()

    def test_low_risk(self):
        step = Step(step_id=1, lane="browser", intent="navigate", description="Open news page")
        risk = self.risk_gate.evaluate_step(step)
        self.assertEqual(risk, RiskLevel.LOW)

    def test_critical_risk_financial(self):
        step = Step(step_id=1, lane="browser", intent="click", description="Confirm and pay invoice")
        risk = self.risk_gate.evaluate_step(step)
        self.assertEqual(risk, RiskLevel.CRITICAL)

    def test_checkpoint_interruption_for_captcha(self):
        step = Step(step_id=1, lane="browser", intent="click", description="Submit search")
        with self.assertRaises(CheckpointRequired) as ctx:
            self.risk_gate.check_checkpoint_preconditions(
                step=step,
                page_url="https://www.google.com/sorry/index?continue=...",
                page_title="Sorry...",
                approved=False
            )
        self.assertEqual(ctx.exception.checkpoint_type, "captcha_anti_bot")

    def test_critical_requires_approval(self):
        step = Step(step_id=1, lane="browser", intent="click", description="Checkout payment")
        with self.assertRaises(CheckpointRequired) as ctx:
            self.risk_gate.check_checkpoint_preconditions(step=step, approved=False)
        self.assertEqual(ctx.exception.checkpoint_type, "critical_action_approval")

if __name__ == "__main__":
    unittest.main()
