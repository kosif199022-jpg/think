import asyncio
import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from types import SimpleNamespace
from unittest import mock

from kosif_think.connectors.llm_router import LLMRouter
from kosif_think.connectors.models import (AnthropicClient, ModelError, OllamaClient, OpenAICompatibleClient,
                                           ScriptedClient, resolve_default_client)
from kosif_think.lanes.reasoning import ChainOfVerification, SelfConsistencyEngine, TreeOfThoughts
from kosif_think.lanes.reasoning.engine import ReasoningLane
from kosif_think.lanes.reasoning.strategies import (chain_of_verification, extract_answer, least_to_most,
                                                    multi_agent_debate, normalize_answer, reflexion,
                                                    self_consistency, self_refine, tree_of_thoughts)
from kosif_think.lanes.voice.tts import VoiceSynthesizer


class FakeMessages:
    def __init__(self, stop_reason="end_turn"):
        self.kwargs = None
        self.stop_reason = stop_reason

    def create(self, **kwargs):
        self.kwargs = kwargs
        return SimpleNamespace(
            stop_reason=self.stop_reason, model=kwargs["model"],
            content=[SimpleNamespace(type="thinking", thinking=""), SimpleNamespace(type="text", text="42")],
            usage=SimpleNamespace(input_tokens=11, output_tokens=3))


class TestModelClients(unittest.TestCase):

    def test_anthropic_client_request_shape_and_usage(self):
        messages = FakeMessages()
        client = AnthropicClient(client=SimpleNamespace(messages=messages), effort="high")
        out = client.complete("What is 6*7?", system="Be brief.", max_tokens=500, temperature=0.9)
        self.assertEqual(out.text, "42")
        self.assertEqual((out.input_tokens, out.output_tokens), (11, 3))
        self.assertEqual(messages.kwargs["model"], "claude-opus-5")
        self.assertEqual(messages.kwargs["thinking"], {"type": "adaptive"})
        self.assertEqual(messages.kwargs["output_config"], {"effort": "high"})
        self.assertEqual(messages.kwargs["system"], "Be brief.")
        self.assertNotIn("temperature", messages.kwargs)

    def test_anthropic_refusal_raises(self):
        client = AnthropicClient(client=SimpleNamespace(messages=FakeMessages(stop_reason="refusal")))
        with self.assertRaises(ModelError):
            client.complete("x")

    def test_http_clients_against_local_server(self):
        seen = []

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                seen.append((self.path, body, self.headers.get("Authorization")))
                if self.path == "/api/chat":
                    reply = {"model": body["model"], "message": {"content": "ollama says hi"},
                             "prompt_eval_count": 5, "eval_count": 4, "done_reason": "stop"}
                else:
                    reply = {"model": body["model"], "choices": [{"message": {"content": "compat says hi"},
                                                                  "finish_reason": "stop"}],
                             "usage": {"prompt_tokens": 7, "completion_tokens": 2}}
                data = json.dumps(reply).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def log_message(self, *args):
                pass

        server = HTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        base = f"http://127.0.0.1:{server.server_port}"
        try:
            o = OllamaClient(model="llama3.1:8b", base_url=base).complete("hi", system="sys")
            self.assertEqual((o.text, o.input_tokens, o.output_tokens), ("ollama says hi", 5, 4))
            c = OpenAICompatibleClient(model="m", base_url=base + "/v1", api_key="k").complete("hi")
            self.assertEqual((c.text, c.input_tokens, c.output_tokens), ("compat says hi", 7, 2))
        finally:
            server.shutdown()
        self.assertEqual(seen[0][0], "/api/chat")
        self.assertEqual(seen[0][1]["messages"][0], {"role": "system", "content": "sys"})
        self.assertEqual(seen[1][0], "/v1/chat/completions")
        self.assertEqual(seen[1][2], "Bearer k")

    def test_unreachable_server_raises_model_error(self):
        with self.assertRaises(ModelError):
            OllamaClient(base_url="http://127.0.0.1:9", timeout=2).complete("hi")

    def test_resolve_default_client(self):
        self.assertIsNone(resolve_default_client({}))
        self.assertIsInstance(resolve_default_client({"OLLAMA_HOST": "http://h:1"}), OllamaClient)
        compat = resolve_default_client({"KOSIF_OPENAI_BASE_URL": "http://h/v1", "KOSIF_OPENAI_MODEL": "m"})
        self.assertIsInstance(compat, OpenAICompatibleClient)
        with self.assertRaises(ModelError):
            resolve_default_client({"KOSIF_MODEL_PROVIDER": "openai_compatible"})
        with self.assertRaises(ModelError):
            resolve_default_client({"KOSIF_MODEL_PROVIDER": "nope"})


class TestRouter(unittest.TestCase):

    def test_simulated_when_no_client(self):
        router = LLMRouter()
        rec = router.dispatch_completion("hello")
        self.assertTrue(rec["simulated"])
        self.assertIn("SIMULATED", rec["response"])

    def test_real_client_usage_and_failover(self):
        class Broken(ScriptedClient):
            def _complete(self, *a):
                raise ModelError("down")

        router = LLMRouter(primary_provider="anthropic",
                           clients={"anthropic": Broken(["x"]), "ollama": ScriptedClient(["real answer"])})
        rec = router.dispatch_completion("hello there")
        self.assertFalse(rec["simulated"])
        self.assertEqual((rec["provider"], rec["response"]), ("ollama", "real answer"))
        self.assertEqual(router.CATALOG["anthropic"].consecutive_failures, 1)
        # Health is per router instance, not shared through the class.
        self.assertEqual(LLMRouter().CATALOG["anthropic"].consecutive_failures, 0)

    def test_all_clients_fail(self):
        class Broken(ScriptedClient):
            def _complete(self, *a):
                raise ModelError("down")

        with self.assertRaises(RuntimeError):
            LLMRouter(clients={"scripted": Broken(["x"])}).dispatch_completion("hi")


class TestStrategies(unittest.TestCase):

    def test_answer_extraction(self):
        self.assertEqual(extract_answer("work\nAnswer: 1,200."), "1,200.")
        self.assertEqual(normalize_answer("1,200."), "1200")
        self.assertEqual(normalize_answer(" **Paris** "), "paris")
        self.assertEqual(extract_answer("no marker\nlast line"), "last line")

    def test_self_consistency_majority(self):
        client = ScriptedClient(["a\nAnswer: 18", "b\nAnswer: 18.0", "c\nAnswer: 26", "d\nAnswer: 18", "e\nAnswer: 20"])
        res = self_consistency(client, "q", samples=5)
        self.assertEqual(normalize_answer(res["answer"]), "18")
        self.assertEqual(res["votes"]["18"], 3)
        self.assertEqual(res["consensus_ratio"], 0.6)
        self.assertFalse(res["unanimous"])
        self.assertEqual(res["usage"]["model_calls"], 5)
        self.assertTrue(all(c["temperature"] == 0.8 for c in client.calls))

    def test_cove_is_factored_and_revises(self):
        def reply(prompt, system):
            if prompt.startswith("Here is a question"):
                return "1. Where was X born?\n2. When did X die?"
            if prompt.startswith("Answer concisely"):
                return "Lyon" if "born" in prompt else "1900"
            if "Independent verification" in prompt:
                return "X was born in Lyon.\nChanged: yes"
            return "X was born in Paris and died in 1900."

        client = ScriptedClient(reply)
        res = chain_of_verification(client, "Tell me about X")
        self.assertEqual(res["verification_questions_count"], 2)
        self.assertTrue(res["draft_changed"])
        self.assertEqual(res["verified_response"], "X was born in Lyon.")
        verify_prompts = [c["prompt"] for c in client.calls if c["prompt"].startswith("Answer concisely")]
        self.assertTrue(verify_prompts and all("Paris" not in p for p in verify_prompts))

    def test_self_refine_stops_on_no_issues(self):
        client = ScriptedClient(["v1", "too short", "v2", "NO ISSUES"])
        res = self_refine(client, "write", max_iterations=5)
        self.assertEqual(res["answer"], "v2")
        self.assertTrue(res["converged"])
        self.assertEqual(res["usage"]["model_calls"], 4)

    def test_reflexion_uses_reflections_and_external_evaluator(self):
        client = ScriptedClient(["def f(): return 1", "Forgot to double the input.", "def f(x): return 2*x"])
        res = reflexion(client, "write f", evaluator=lambda code: ("2*x" in code, "f(2) != 4"), max_trials=3)
        self.assertTrue(res["passed"])
        self.assertEqual(len(res["trials"]), 2)
        self.assertIn("Forgot to double", client.calls[2]["prompt"])

    def test_tree_of_thoughts_bfs_prefers_sure(self):
        def reply(prompt, system):
            if prompt.startswith("Problem") and "Propose" in prompt:
                return "1. good step\n2. bad step"
            last = prompt.split("Partial solution:")[1].strip().splitlines()[-1]
            return "sure" if "good" in last else "impossible"

        res = tree_of_thoughts(ScriptedClient(reply), "p", breadth=2, depth=2, beam=1)
        self.assertEqual(res["optimal_reasoning_path"], ["good step", "good step"])
        self.assertEqual(res["total_thoughts_explored"], 4)

    def test_debate_agents_see_each_other(self):
        a = ScriptedClient(["Answer: 5", "Answer: 7"])
        b = ScriptedClient(["Answer: 7", "Answer: 7"])
        res = multi_agent_debate([a, b], "q", rounds=2)
        self.assertEqual(res["answer"], "7")
        self.assertIn("Agent 2:\nAnswer: 7", a.calls[1]["prompt"])
        self.assertEqual(res["usage"]["model_calls"], 4)

    def test_least_to_most_carries_context(self):
        client = ScriptedClient(["1. sub one\n2. whole problem", "ans one", "final"])
        res = least_to_most(client, "p")
        self.assertEqual(res["answer"], "final")
        self.assertIn("A: ans one", client.calls[2]["prompt"])


class TestEnginesWithClient(unittest.TestCase):

    def test_engines_delegate_when_client_given(self):
        sc = SelfConsistencyEngine(client=ScriptedClient(["Answer: 4"])).evaluate_consensus("2+2", num_samples=3)
        self.assertFalse(sc["simulated"])
        self.assertEqual(sc["majority_conclusion"], "4")
        self.assertTrue(SelfConsistencyEngine().evaluate_consensus("x")["simulated"])

        cove = ChainOfVerification(client=ScriptedClient(["draft", "1. q?", "a", "final\nChanged: no"]))
        res = cove.verify_and_synthesize("p")
        self.assertTrue(res["all_verified"])
        self.assertFalse(res["simulated"])

        tot = TreeOfThoughts(branching_factor=2, max_depth=1, client=ScriptedClient(lambda p, s: "1. a\n2. b" if "Propose" in p else "likely"))
        self.assertFalse(tot.search("p")["simulated"])

    def test_lane_model_only_modes(self):
        step = SimpleNamespace(intent="debate", value="q")
        no_model = asyncio.run(ReasoningLane(use_env_client=False).dispatch_step(step))
        self.assertEqual(no_model["status"], "error")
        lane = ReasoningLane(client=ScriptedClient(["Answer: 3"]))
        ok = asyncio.run(lane.dispatch_step(step))
        self.assertEqual((ok["status"], ok["answer"], ok["agents"]), ("ok", "3", 3))


class TestVoiceNoInterpolation(unittest.TestCase):

    def test_text_is_not_in_powershell_command(self):
        text = "hi\"; Remove-Item C:\\x; $(whoami) '"
        cmd, env = VoiceSynthesizer()._command("windows_sapi", text)
        self.assertNotIn(text, " ".join(cmd))
        self.assertEqual(env["KOSIF_TTS_TEXT"], text)
        cmd, _ = VoiceSynthesizer()._command("espeak-ng", "-v evil")
        self.assertEqual(cmd, ["espeak-ng", "--", "-v evil"])

    def test_unavailable_engine_reported(self):
        with mock.patch.object(VoiceSynthesizer, "detect_engine", return_value=None):
            self.assertEqual(VoiceSynthesizer().speak("x")["status"], "unavailable")


if __name__ == "__main__":
    unittest.main()
