import asyncio
import unittest

from kosif_think.core.executor import ThinkExecutor


class NoChangeBrowserLane:
    async def dispatch_step(self, step, cancellation_token=None):
        return {
            "status": "ok",
            "lane": "browser",
            "changed": False,
            "url": "https://example.invalid/no-change",
        }


class TestExecutorTruthfulness(unittest.TestCase):
    def test_missing_lane_handler_must_not_report_completed(self):
        executor = ThinkExecutor()
        result = asyncio.run(executor.execute_goal("ابحث عن KOSIF verification sentinel"))
        self.assertEqual(result.status, "failed")
        self.assertIn("handler", (result.error or "").lower())

    def test_failed_verification_must_not_report_completed(self):
        executor = ThinkExecutor()
        executor.register_lane("browser", NoChangeBrowserLane())
        result = asyncio.run(executor.execute_goal("ابحث عن KOSIF verification sentinel"))
        self.assertEqual(result.status, "failed")
        self.assertIn("verification", (result.error or "").lower())


if __name__ == "__main__":
    unittest.main()
