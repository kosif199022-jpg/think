import unittest
from kosif_think.lanes.reasoning.dspy_optimizer import DSPyOptimizer, DSPySignature
from kosif_think.lanes.reasoning.multi_agent_graph import MultiAgentGraph
from kosif_think.lanes.reasoning.repo_intelligence import RepoIntelligence

class TestDSPyAndMultiAgent(unittest.TestCase):
    def setUp(self):
        self.dspy = DSPyOptimizer()
        self.graph = MultiAgentGraph()
        self.repo_intel = RepoIntelligence()

    def test_dspy_compilation(self):
        sig = DSPySignature("CodeSynthesis", ["spec"], ["implementation"])
        res = self.dspy.compile(sig, {"spec": "Write a binary search function"})
        self.assertEqual(res["mode"], "dspy_compiled")
        self.assertGreater(res["metric_score"], 0.8)
        self.assertIn("implementation", res["optimized_output"])

    def test_multi_agent_graph_execution(self):
        res = self.graph.run_graph("Refactor authentication module", max_iterations=3)
        self.assertEqual(res["mode"], "multi_agent_graph")
        self.assertTrue(res["iterations"] > 0)
        self.assertTrue(len(res["turns"]) > 0)

    def test_repo_intelligence_patterns(self):
        pattern = self.repo_intel.ingest_architectural_pattern("dspy")
        self.assertIn("Declarative", pattern["architecture"]["paradigm"])

if __name__ == "__main__":
    unittest.main()
