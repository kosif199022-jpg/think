import unittest
import asyncio
from kosif_think.lanes.coding.ast_parser import ASTCodeParser
from kosif_think.lanes.coding.patcher import AtomicPatcher
from kosif_think.lanes.coding.debugger import AutonomousDebugger
from kosif_think.lanes.coding.engine import CodingLane
from kosif_think.core.planner import Step

SAMPLE_CODE = """
import os, sys

class DataStore:
    def __init__(self, name):
        self.name = name

    def get_data(self, key):
        if key:
            return "value"
        return None
"""

class TestCodingLane(unittest.TestCase):
    def setUp(self):
        self.parser = ASTCodeParser()
        self.patcher = AtomicPatcher()
        self.lane = CodingLane()

    def test_ast_parsing(self):
        res = self.parser.parse_source(SAMPLE_CODE, filename="sample.py")
        self.assertTrue(res["ok"])
        self.assertEqual(res["symbol_count"], 3)  # DataStore, __init__, get_data
        self.assertIn("os", res["imports"])

    def test_traceback_parsing(self):
        debugger = AutonomousDebugger()
        sample_tb = '''Traceback (most recent call last):
  File "app/main.py", line 42, in process_request
    raise ValueError("Invalid payload")
ValueError: Invalid payload'''
        diag = debugger.parse_traceback(sample_tb)
        self.assertEqual(diag["file"], "app/main.py")
        self.assertEqual(diag["line"], 42)
        self.assertEqual(diag["error_type"], "ValueError")

    def test_coding_lane_dispatch(self):
        step = Step(step_id=1, lane="coding", intent="analyze", value=SAMPLE_CODE)
        res = asyncio.run(self.lane.dispatch_step(step))
        self.assertTrue(res.get("ok"))
        self.assertEqual(res.get("lane"), "coding")

if __name__ == "__main__":
    unittest.main()
