import unittest
from kosif_think.core.verifier import ObservableVerifier

class TestVerifier(unittest.TestCase):
    def setUp(self):
        self.verifier = ObservableVerifier()

    def test_url_matching_success(self):
        conds = [{"type": "url_matches", "expected": "google.com"}]
        observed = {"url": "https://www.google.com/search?q=test", "changed": True}
        res = self.verifier.verify_step_postconditions(conds, observed)
        self.assertTrue(res.verified)

    def test_url_matching_failure(self):
        conds = [{"type": "url_matches", "expected": "bing.com"}]
        observed = {"url": "https://www.google.com/sorry/index", "changed": True}
        res = self.verifier.verify_step_postconditions(conds, observed)
        self.assertFalse(res.verified)
        self.assertIn("Expected URL to contain", res.failure_reason)

    def test_text_contains(self):
        conds = [{"type": "text_contains", "text": "Results"}]
        observed = {"text": "Search Results for gold", "changed": True}
        res = self.verifier.verify_step_postconditions(conds, observed)
        self.assertTrue(res.verified)

if __name__ == "__main__":
    unittest.main()
