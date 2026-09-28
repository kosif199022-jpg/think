import unittest
import asyncio
from kosif_think.core.executor import ThinkExecutor
from kosif_think.lanes.reasoning import ReasoningLane
from kosif_think.lanes.computer import ComputerLane
from kosif_think.lanes.browser import BrowserLane
from kosif_think.lanes.whatsapp import WhatsAppLane
from kosif_think.core.cancellation import CancellationSource

class TestCoreLoop(unittest.TestCase):
    def setUp(self):
        self.executor = ThinkExecutor()
        self.executor.register_lane("reasoning", ReasoningLane())
        self.executor.register_lane("computer", ComputerLane())
        self.executor.register_lane("browser", BrowserLane())
        self.executor.register_lane("whatsapp", WhatsAppLane())

    def test_end_to_end_reasoning(self):
        res = asyncio.run(self.executor.execute_goal("ما هو أفضل نهج لتأمين البيانات؟"))
        self.assertEqual(res.status, "completed")
        self.assertGreater(res.steps_executed, 0)
        self.assertIn("deliberation", res.output)

    def test_cancellation(self):
        source = CancellationSource()
        source.cancel()
        res = asyncio.run(self.executor.execute_goal("مهمة ملغاة", cancellation_token=source.token))
        self.assertEqual(res.status, "cancelled")

    def test_human_checkpoint_interruption(self):
        res = asyncio.run(self.executor.execute_goal("قم بدفع الفاتورة وسحب المبلغ 500 دولار فوراً", approved=False))
        self.assertEqual(res.status, "human_checkpoint")
        self.assertIsNotNone(res.checkpoint_details)

if __name__ == "__main__":
    unittest.main()
