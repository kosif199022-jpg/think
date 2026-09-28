import unittest
import asyncio
from kosif_think.core.executor import ThinkExecutor
from kosif_think.lanes.reasoning import ReasoningLane
from kosif_think.lanes.ios import IOSLane
from kosif_think.connectors.openai_bridge import OpenAIBridge
from kosif_think.connectors.app_hub import AppHub

class TestOpenAIBridge(unittest.TestCase):
    def setUp(self):
        self.executor = ThinkExecutor()
        self.executor.register_lane("reasoning", ReasoningLane())
        self.executor.register_lane("ios", IOSLane())
        self.bridge = OpenAIBridge(self.executor)
        self.hub = AppHub()

    def test_list_models(self):
        models = self.bridge.list_models()
        self.assertEqual(models["object"], "list")
        ids = [m["id"] for m in models["data"]]
        self.assertIn("kosif-think-v1", ids)

    def test_chat_completion_format(self):
        req = {
            "model": "kosif-think-v1",
            "messages": [
                {"role": "user", "content": "ما هي أفضل ممارسات الأمن السيبراني؟"}
            ]
        }
        res = asyncio.run(self.bridge.handle_chat_completion(req))
        self.assertEqual(res["object"], "chat.completion")
        self.assertTrue(len(res["choices"]) > 0)
        self.assertEqual(res["choices"][0]["message"]["role"], "assistant")
        self.assertIn("usage", res)

    def test_chatgpt_controls_iphone(self):
        req = {
            "model": "kosif-think-v1",
            "messages": [
                {"role": "user", "content": "افتح تطبيق الكاميرا على الآيفون"}
            ]
        }
        res = asyncio.run(self.bridge.handle_chat_completion(req))
        self.assertEqual(res["kosif_metadata"]["status"], "completed")

    def test_openapi_spec(self):
        spec = self.hub.get_openapi_spec()
        self.assertEqual(spec["openapi"], "3.0.0")
        self.assertIn("/api/think/execute", spec["paths"])

if __name__ == "__main__":
    unittest.main()
