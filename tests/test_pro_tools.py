import asyncio
import io
import json
import threading
import unittest
import urllib.error
import urllib.request
from contextlib import redirect_stdout
from http.server import HTTPServer

from kosif_think.cli import main as cli_main
from kosif_think.connectors.models import ScriptedClient
from kosif_think.pro import DESCRIPTIONS, TOOLS, deliberate, run_tool


class TestDeterministicTools(unittest.TestCase):

    def test_registry_complete(self):
        self.assertEqual(set(TOOLS), set(DESCRIPTIONS))
        with self.assertRaises(KeyError):
            run_tool("nope", {})

    def test_decision_feasibility_dominance_sensitivity(self):
        res = run_tool("decision", {
            "criteria": {"cost": {"direction": "min", "weight": 0.4}, "quality": {"direction": "max", "weight": 0.4},
                         "speed": {"direction": "max", "weight": 0.2}},
            "constraints": {"cost": {"max": 5000}, "quality": {"min": 6}},
            "options": [{"id": "A", "scores": {"cost": 4000, "quality": 7, "speed": 5}},
                        {"id": "B", "scores": {"cost": 4500, "quality": 6, "speed": 4}},
                        {"id": "C", "scores": {"cost": 6000, "quality": 9, "speed": 9}},
                        {"id": "D", "scores": {"cost": 3000, "quality": 8}}]})
        self.assertEqual(res["winner"], "A")
        self.assertEqual(res["dominated"], {"B": "A"})
        self.assertEqual(res["rejected"], [{"id": "C", "failed": ["cost"]}])
        self.assertEqual(res["pending"], [{"id": "D", "missing": ["speed"]}])
        self.assertIn("weight_sensitivity", res)

    def test_probability_conjunction_and_base_rate(self):
        res = run_tool("probability", {
            "events": {"A": "0.3", "B": "0.6", "A&B": "0.4", "not A": "0.7"},
            "bayes": [{"name": "test", "prior": "0.01", "sensitivity": "0.9", "false_positive_rate": "0.09",
                       "stated_posterior": "0.9"}]})
        self.assertFalse(res["ok"])
        self.assertTrue(any("conjunction fallacy" in i for i in res["issues"]))
        self.assertTrue(any("base-rate neglect" in i for i in res["issues"]))
        self.assertEqual(res["bayes"][0]["posterior"], "0.091743")

    def test_calibration_arabic_and_english(self):
        res = run_tool("calibration", {"claims": [
            {"text": "He must be French", "evidence": [{"type": "observation", "source": "sign"}]},
            {"text": "ربما يكون الخادم متوقفاً", "evidence": [{"type": "inference"}]}]})
        self.assertIn("overclaim", res["claims"][0]["verdict"])
        self.assertEqual(res["claims"][1]["level"], "possible")
        self.assertEqual(res["claims"][1]["verdict"], "ok")

    def test_evidence_quarantines_contradicted_answer(self):
        res = run_tool("evidence", {
            "evidence": [{"id": "e1", "source": "gpt", "type": "arithmetic", "expression": "120 - 120*15% - 10"},
                         {"id": "e2", "source": "claude", "type": "arithmetic", "expression": "(120 - 18) - 10"},
                         {"id": "e3", "source": "calc", "type": "sum", "parts": ["18", "102"], "total": "120"}],
            "answers": [{"id": "a1", "value": "97"}, {"id": "a2", "value": "92"}]})
        self.assertEqual(res["converged_value"], "92")
        self.assertEqual([q["id"] for q in res["quarantined_answers"]], ["a1"])

    def test_evidence_rejects_code_in_expressions(self):
        res = run_tool("evidence", {"evidence": [{"type": "arithmetic", "expression": "__import__('os').getcwd()"}]})
        self.assertFalse(res["evidence"][0]["valid"])

    def test_council_select_and_aggregate_veto(self):
        sel = run_tool("council-select", {"task": "publish the payment page with stored credentials", "mode": "standard"})
        self.assertIn("skeptic", [p["id"] for p in sel["personas"]])
        veto = next(p for p in sel["personas"] if p["veto"] and p["id"] != "skeptic")
        agg = run_tool("council-aggregate", {"artifacts": [
            {"id": "skeptic", "stance": "support", "confidence": 0.9, "evidence": ["a", "b", "c"]},
            {"id": veto["id"], "stance": "oppose", "confidence": 0.6, "objection": "stop", "severity": "blocking"}]})
        self.assertEqual(agg["verdict"], "escalate")

    def test_independence_discounts_same_model(self):
        res = run_tool("council-independence", {"artifacts": [
            {"agentId": "a", "source": "anthropic", "model": "m"}, {"agentId": "b", "source": "anthropic", "model": "m"}]})
        self.assertEqual(res["effective_independent_votes"], 1.25)
        self.assertFalse(res["meets_gate"])

    def test_source_atlas_exact_duplicates_one_vote(self):
        res = run_tool("source-atlas", {"as_of": "2026-10-01", "records": [
            {"name": "a", "text": "same body"}, {"name": "b", "text": "same body"}, {"name": "c", "text": ""}]})
        self.assertEqual(res["exact_duplicate_groups"], [["a", "b"]])
        self.assertEqual(res["effective_retrieval_weight"], 1.0)
        self.assertEqual(res["quarantined"]["empty"], ["c"])
        with self.assertRaises(ValueError):
            run_tool("source-atlas", {"records": []})

    def test_secrets_never_echo_values(self):
        token = "ghp_" + "A" * 30
        res = run_tool("secrets", {"text": f"push with {token}", "redact": True})
        self.assertTrue(res["blocked"])
        self.assertNotIn(token, json.dumps(res["findings"]))
        self.assertNotIn(token, res["redacted_text"])

    def test_capability_needs_evidence(self):
        self.assertEqual(run_tool("capability", {"name": "x", "implementation": "verified"})["status"], "implemented")
        ok = run_tool("capability", {"name": "x", "implementation": "implemented", "evidence": [
            {"type": "deterministic-test", "passed": True}, {"type": "benchmark", "passed": True}]})
        self.assertTrue(ok["verified"])

    def test_dag(self):
        self.assertFalse(run_tool("dag", {"nodes": ["a", "b"], "edges": [["a", "b"], ["b", "a"]]})["acyclic"])

    def test_ledger_controls(self):
        res = run_tool("ledger", {
            "currency_minor_units": 2, "vat_rate": "0.15", "chart": ["1101", "1201", "2201", "4101"],
            "revenue_accounts": ["4101"], "bank_accounts": ["1101"],
            "period": {"start": "2026-09-01", "end": "2026-09-30", "status": "open"},
            "entries": [
                {"id": "JE1", "date": "2026-09-03", "event_key": "INV-104",
                 "lines": [{"account": "1201", "debit": "1150.00"}, {"account": "4101", "credit": "1000.00"},
                           {"account": "2201", "credit": "150.00"}], "tax": {"base": "1000.00", "amount": "150.00"}},
                {"id": "JE2", "date": "2026-09-04", "event_key": "INV-104",
                 "lines": [{"account": "1101", "debit": "100.00"}, {"account": "4101", "credit": "90.00"}]}],
            "invoices": [{"id": "INV-104", "party": "NOUR", "total": "1150.00"}],
            "bank": [{"id": "B1", "party": "NOUR", "amount": "1150.00", "ref": "INV-104"}]})
        self.assertFalse(res["ok"])
        problems = " ".join(res["issues"])
        self.assertIn("unbalanced", problems)
        self.assertIn("already booked in JE1", problems)
        self.assertIn("bank receipt credited directly to revenue", problems)
        self.assertEqual(res["matches"][0]["status"], "full")


class TestModelCouncil(unittest.TestCase):

    def test_deliberate_uses_lenses_and_vetoes(self):
        def reply(prompt, system):
            if system and "Skeptic" in system:
                return 'Here: {"stance": "oppose", "confidence": 0.8, "evidence": ["no source"], ' \
                       '"objection": "claims are unsourced", "severity": "material"}'
            if system:
                return '{"stance": "support", "confidence": 0.7, "evidence": ["ok"], "severity": "none"}'
            return "Revised plan: add sources first."

        client = ScriptedClient(reply)
        res = deliberate(client, "Publish the report claiming 40% growth", max_personas=3)
        self.assertEqual(res["verdict"]["verdict"], "revise")
        self.assertEqual(res["recommendation"], "Revised plan: add sources first.")
        self.assertIn("skeptic: claims are unsourced", client.calls[-1]["prompt"])
        self.assertEqual(res["usage"]["model_calls"], res["selection"]["count"] + 1)
        self.assertEqual(res["verdict"]["effective_independent_sources"], 1)

    def test_unparseable_artifact_abstains(self):
        res = deliberate(ScriptedClient(["not json"]), "Decide on lunch", max_personas=1)
        self.assertTrue(res["parse_errors"])
        self.assertTrue(all(a["stance"] == "abstain" for a in res["artifacts"]))


class TestInterfaces(unittest.TestCase):

    def _cli(self, argv, stdin_text):
        import sys
        old = sys.stdin
        sys.stdin = io.StringIO(stdin_text)
        out = io.StringIO()
        try:
            with redirect_stdout(out), self.assertRaises(SystemExit) as cm:
                cli_main(argv)
        finally:
            sys.stdin = old
        return cm.exception.code, out.getvalue()

    def test_cli_pro(self):
        code, out = self._cli(["pro", "dag"], json.dumps({"nodes": ["a"], "edges": []}))
        self.assertEqual(code, 0)
        self.assertTrue(json.loads(out)["acyclic"])
        code, _ = self._cli(["pro", "probability"], json.dumps({"events": {"A": "0.2", "not A": "0.5"}}))
        self.assertEqual(code, 1)
        code, _ = self._cli(["pro", "dag"], "not json")
        self.assertEqual(code, 2)

    def test_mcp_pro_tool(self):
        from kosif_think.server.mcp import TOOLS_DEFINITION, handle_tool_call
        names = [t["name"] for t in TOOLS_DEFINITION]
        self.assertIn("think_pro_tool", names)
        self.assertIn("think_reason", names)
        res = asyncio.run(handle_tool_call("think_pro_tool", {"tool": "secrets", "input": {"text": "nothing here"}}))
        self.assertFalse(res["blocked"])
        bad = asyncio.run(handle_tool_call("think_pro_tool", {"tool": "nope", "input": {}}))
        self.assertFalse(bad["ok"])

    def test_http_pro_endpoint(self):
        from kosif_think.server.api import ThinkHTTPRequestHandler
        server = HTTPServer(("127.0.0.1", 0), ThinkHTTPRequestHandler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        base = f"http://127.0.0.1:{server.server_port}/api/pro/"
        try:
            req = urllib.request.Request(base + "dag", data=json.dumps({"nodes": ["a"], "edges": []}).encode(),
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                self.assertTrue(json.loads(resp.read())["acyclic"])
            with self.assertRaises(urllib.error.HTTPError) as cm:
                urllib.request.urlopen(urllib.request.Request(base + "nope", data=b"{}"), timeout=5)
            self.assertEqual(cm.exception.code, 404)
        finally:
            server.shutdown()


if __name__ == "__main__":
    unittest.main()
