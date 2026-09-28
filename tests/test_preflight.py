import unittest
from kosif_think.core.preflight import PreflightGate
from kosif_think.core.cancellation import CancellationSource

class TestPreflight(unittest.TestCase):
    def setUp(self):
        self.preflight = PreflightGate()

    def test_valid_request(self):
        req = self.preflight.run_preflight("ابحث عن سعر الذهب")
        self.assertTrue(req.is_valid)
        self.assertEqual(req.clean_goal, "ابحث عن سعر الذهب")
        self.assertTrue(len(req.task_id) > 0)

    def test_empty_request(self):
        req = self.preflight.run_preflight("   ")
        self.assertFalse(req.is_valid)

    def test_cancelled_preflight(self):
        source = CancellationSource()
        source.cancel()
        req = self.preflight.run_preflight("some goal", cancellation_token=source.token)
        self.assertFalse(req.is_valid)
        self.assertIn("Cancelled", req.error_message)

if __name__ == "__main__":
    unittest.main()
