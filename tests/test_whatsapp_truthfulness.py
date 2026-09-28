import asyncio
import unittest

from kosif_think.core.planner import Step, Target
from kosif_think.lanes.whatsapp import WhatsAppBridge, WhatsAppLane


class TestWhatsAppTruthfulness(unittest.TestCase):
    def test_bridge_does_not_invent_pairing_state(self):
        bridge = WhatsAppBridge()
        status = bridge.check_connection()
        self.assertEqual(status["status"], "requires_host_check")
        self.assertIsNone(status["paired"])
        self.assertEqual(status["tool"], "get_whatsapp_status")

    def test_send_requires_real_host_mcp_execution(self):
        lane = WhatsAppLane()
        step = Step(
            step_id=1,
            lane="whatsapp",
            intent="send_message",
            target=Target(kind="phone_number", ref="+966500000000"),
            value="hello",
            expected_postconditions=[{"type": "message_dispatched"}],
        )
        result = asyncio.run(lane.dispatch_step(step))
        self.assertFalse(result["dispatched"])
        self.assertTrue(result["requires_host_execution"])
        self.assertEqual(result["tool"], "send_whatsapp_message")
        self.assertEqual(result["args"]["to"], "+966500000000")
        self.assertEqual(result["args"]["message"], "hello")


if __name__ == "__main__":
    unittest.main()
