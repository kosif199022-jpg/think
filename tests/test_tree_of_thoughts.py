import unittest
from kosif_think.lanes.reasoning.tree_of_thoughts import TreeOfThoughts

class TestTreeOfThoughts(unittest.TestCase):
    def setUp(self):
        self.tot = TreeOfThoughts(branching_factor=2, max_depth=2)

    def test_search_optimal_path(self):
        res = self.tot.search("Design a fault-tolerant distributed cache")
        self.assertEqual(res["mode"], "tree_of_thoughts")
        self.assertGreater(res["best_score"], 0.0)
        self.assertGreater(res["total_thoughts_explored"], 1)
        self.assertTrue(len(res["optimal_reasoning_path"]) >= 2)

if __name__ == "__main__":
    unittest.main()
