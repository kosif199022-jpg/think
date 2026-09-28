import unittest
from kosif_think.lanes.reasoning.graph_of_thoughts import GraphOfThoughts

class TestGraphOfThoughts(unittest.TestCase):
    def setUp(self):
        self.got = GraphOfThoughts()

    def test_solve_graph(self):
        res = self.got.solve_graph("Design an ultra-low latency trading matching engine")
        self.assertEqual(res["mode"], "graph_of_thoughts")
        self.assertGreater(res["vertex_count"], 3)
        self.assertTrue(len(res["topological_order"]) >= 4)
        self.assertIn("synthesis", res["final_consensus"].lower())

if __name__ == "__main__":
    unittest.main()
