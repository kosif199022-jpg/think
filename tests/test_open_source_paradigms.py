"""
Comprehensive Unit Tests for Open-Source Frontier AI Paradigms in KOSIF Think.
Validates:
- RepoIntelligence (multi-repo catalog, pattern extraction, cross-repo strategy)
- RLVRReasoner (DeepSeek-R1 verifiable reward search, mathematical invariants)
- CodeAgentInterpreter (Smolagents safe AST code action execution)
- BrowserUseEngine (Set-of-Marks visual indexing, DOM flattener, Cubic Bezier stealth curves)
- AppAgentOrchestrator (Tencent AppAgent / Mobile-Agent subgoal planner & screen memory)
- PerspectiveResearchEngine (Stanford Co-STORM & PaperQA multi-perspective research)
- SWEAgentOrchestrator (SWE-agent / Aider PageRank symbol ranker, fuzzy diff patcher, reproduction tests)
- Lane Integrations across Reasoning, Coding, Mobile, Research, and Browser
"""

import unittest
import asyncio
from kosif_think.lanes.reasoning.repo_intelligence import RepoIntelligence
from kosif_think.lanes.reasoning.rlvr_reasoner import RLVRReasoner, TrajectoryCandidate
from kosif_think.lanes.reasoning.code_agent import CodeAgentInterpreter
from kosif_think.lanes.browser.browser_use_engine import BrowserUseEngine
from kosif_think.lanes.mobile.app_agent import AppAgentOrchestrator
from kosif_think.lanes.research.storm_engine import PerspectiveResearchEngine
from kosif_think.lanes.coding.swe_orchestrator import SWEAgentOrchestrator
from kosif_think.lanes.reasoning.engine import ReasoningLane
from kosif_think.lanes.coding.engine import CodingLane
from kosif_think.lanes.mobile.engine import MobileLane
from kosif_think.lanes.research.engine import ResearchLane
from kosif_think.lanes.browser.engine import BrowserLane
from kosif_think.core.planner import Step

class TestOpenSourceParadigms(unittest.TestCase):

    def setUp(self):
        self.repo_intel = RepoIntelligence()
        self.rlvr = RLVRReasoner()
        self.code_agent = CodeAgentInterpreter()
        self.browser_use = BrowserUseEngine()
        self.app_agent = AppAgentOrchestrator()
        self.storm = PerspectiveResearchEngine()
        self.swe = SWEAgentOrchestrator()

    # 1. RepoIntelligence Tests
    def test_repo_catalog_and_search(self):
        repos = self.repo_intel.search_github_repos("mobile browser code research")
        self.assertGreaterEqual(len(repos), 3)
        repo_names = [r["name"].lower() for r in repos]
        self.assertTrue(any("agent" in n or "deepseek" in n or "browser" in n for n in repo_names))

    def test_repo_pattern_ingestion(self):
        pattern = self.repo_intel.ingest_architectural_pattern("browser-use/browser-use")
        self.assertEqual(pattern["repo"], "browser-use/browser-use")
        self.assertIn("Set-of-Marks", pattern["architecture"]["paradigm"])
        self.assertGreater(len(pattern["architecture"]["core_invariants"]), 0)

    def test_cross_repo_strategy_synthesis(self):
        strat = self.repo_intel.synthesize_super_agent_strategy(
            "تطوير منظومة ذكية للتحكم بالمتصفح والهاتف وتحليل الأبحاث ومستندات الأوفيس"
        )
        self.assertEqual(strat["expected_execution_quality"], "Super-Intelligent Zero-Hallucination")
        self.assertGreaterEqual(strat["total_open_source_paradigms"], 4)
        self.assertIn("architecture_blueprint", strat)
        self.assertIn("execution_steps", strat)
        # Verify lane assignments
        lanes = [s["lane"] for s in strat["execution_steps"]]
        self.assertIn("browser", lanes)
        self.assertIn("mobile", lanes)
        self.assertIn("office", lanes)

    # 2. RLVR Reasoner Tests
    def test_rlvr_verifiable_reward(self):
        cand = TrajectoryCandidate(
            trajectory_id=1,
            hypothesis="Direct algebraic deduction",
            steps=[
                "Step 1: Simplify 12 + 8 = 20.",
                "Step 2: Note previous contradiction was resolved.",
                "Step 3: Conclude final equality 20 * 2 = 40."
            ],
            expected_outcome="Value 40 formally proved"
        )
        reward = self.rlvr.evaluate_verifiable_reward(cand)
        self.assertGreaterEqual(reward, 0.7)
        self.assertTrue(cand.is_sound)
        self.assertIn("format_compliance", cand.invariants_passed)
        self.assertIn("contradiction_resolution", cand.invariants_passed)
        self.assertIn("symbolic_arithmetic_valid", cand.invariants_passed)

    def test_rlvr_search_optimal_trajectory(self):
        res = self.rlvr.search_optimal_trajectory("Maximize distributed consensus throughput", rollouts=4)
        self.assertEqual(res["rollouts_evaluated"], 4)
        self.assertIn("verification_reward", res)
        self.assertIn("optimal_hypothesis", res)
        self.assertIn("synthesized_solution", res)
        self.assertGreaterEqual(len(res["reasoning_steps"]), 2)

    # 3. Smolagents CodeAgent Tests
    def test_code_agent_safety_inspection(self):
        safe_code = "total = sum([x**2 for x in range(10)])\nprint(total)"
        unsafe_code = "import subprocess\nsubprocess.run('calc.exe')"
        eval_code = "result = eval('2 + 2')"

        self.assertTrue(self.code_agent.inspect_safety(safe_code)["safe"])
        self.assertFalse(self.code_agent.inspect_safety(unsafe_code)["safe"])
        self.assertFalse(self.code_agent.inspect_safety(eval_code)["safe"])

    def test_code_agent_execution(self):
        script = (
            "accumulator = 0\n"
            "for i in range(1, 6):\n"
            "    accumulator += i\n"
            "print(f'Sum is {accumulator}')\n"
            "result = accumulator\n"
        )
        res = self.code_agent.execute_script(script)
        self.assertEqual(res["status"], "ok")
        self.assertTrue(res["success"])
        self.assertEqual(res["result"], 15)
        self.assertIn("Sum is 15", res["output"])

    # 4. BrowserUseEngine Tests
    def test_browser_use_flatten_dom(self):
        html = """
        <html>
            <body>
                <header><h1>Welcome</h1></header>
                <button id="login-btn" class="btn">Log In</button>
                <input type="text" name="username" placeholder="Username" />
                <a href="/help">Need Help?</a>
            </body>
        </html>
        """
        elements = self.browser_use.flatten_dom(html)
        self.assertGreaterEqual(len(elements), 3)
        tags = [e["tag"] for e in elements]
        self.assertIn("button", tags)
        self.assertIn("input", tags)
        self.assertIn("a", tags)
        # Check badge formatting
        self.assertTrue(elements[0]["badge"].startswith("["))
        # Check action space
        space = self.browser_use.get_current_action_space()
        self.assertIn("click(badge_id)", space["supported_actions"])

    def test_browser_use_stealth_mouse_curve(self):
        start = (50, 100)
        end = (600, 450)
        trajectory = self.browser_use.generate_stealth_mouse_curve(start, end, steps=15)
        self.assertEqual(len(trajectory), 15)
        self.assertEqual(trajectory[0], start)
        self.assertEqual(trajectory[-1], end)

    # 5. AppAgent Mobile Tests
    def test_app_agent_subgoal_planning(self):
        subgoals = self.app_agent.plan_subgoals_for_app("Send status report to manager", "com.whatsapp")
        self.assertGreaterEqual(len(subgoals), 4)
        intents = [sg["intent"] for sg in subgoals]
        self.assertIn("launch_app", intents)
        self.assertIn("locate_and_type", intents)
        self.assertIn("input_text", intents)

    def test_app_agent_screen_transitions(self):
        # Register a state
        node = self.app_agent.record_screen_state("home_screen", "com.android.launcher", [{"role": "icon", "text": "WhatsApp"}])
        self.assertEqual(node.screen_id, "home_screen")
        self.assertEqual(node.visited_count, 1)

    # 6. PerspectiveResearchEngine (STORM) Tests
    def test_storm_perspectives_expansion(self):
        perspectives = self.storm.expand_perspectives("Reinforcement Learning from Human Feedback")
        self.assertEqual(len(perspectives), 4)
        roles = [p["perspective"] for p in perspectives]
        self.assertIn("Theoretical Foundations", roles)
        self.assertIn("Empirical Systems Engineer", roles)
        self.assertIn("Safety & Robustness Auditor", roles)

    def test_storm_question_tree(self):
        qtree = self.storm.generate_question_tree("Neural Symbolic Synthesis")
        self.assertEqual(qtree["root_topic"], "Neural Symbolic Synthesis")
        self.assertGreater(len(qtree["core_inquiries"]), 0)

    # 7. SWEAgentOrchestrator Tests
    def test_symbol_pagerank(self):
        graph = {
            "ASTParser": ["Tokenizer", "SyntaxNode"],
            "AtomicPatcher": ["ASTParser", "SyntaxNode"],
            "AutonomousDebugger": ["AtomicPatcher", "TestSandbox", "ASTParser"],
            "Tokenizer": [],
            "SyntaxNode": [],
            "TestSandbox": []
        }
        ranks = self.swe.compute_symbol_pagerank(graph, iterations=15)
        self.assertGreater(len(ranks), 0)
        # Tokenizer and SyntaxNode have high incoming references
        self.assertIn("SyntaxNode", ranks)
        self.assertAlmostEqual(sum(ranks.values()), 1.0, places=2)

    def test_apply_fuzzy_patch(self):
        original = "def calculate(a, b):\n    # Old implementation\n    return a - b\n"
        target = "    # Old implementation\n    return a - b"
        replacement = "    # Fixed implementation\n    return a + b"

        res = self.swe.apply_fuzzy_patch(original, target, replacement)
        self.assertTrue(res["applied"])
        self.assertIn("return a + b", res["content"])

    def test_synthesize_reproduction_test(self):
        test_src = self.swe.synthesize_reproduction_test("solve_matrix_inversion fails on zero determinant")
        self.assertIn("import unittest", test_src)
        self.assertIn("class TestReproduction(unittest.TestCase):", test_src)
        self.assertTrue(self.swe.validate_syntax(test_src)["valid"])

    # 8. Dispatch Integration Tests Across Lanes
    def test_lane_dispatches(self):
        async def run_dispatches():
            # Reasoning RLVR
            r_lane = ReasoningLane()
            rlvr_res = await r_lane.dispatch_step(Step(step_id=1, lane="reasoning", intent="rlvr", value="Deduce optimal invariant"))
            self.assertEqual(rlvr_res["mode"], "rlvr_reasoning")

            # Reasoning CodeAgent
            code_res = await r_lane.dispatch_step(Step(step_id=2, lane="reasoning", intent="code_agent", value="total = 40 + 2\nresult = total"))
            self.assertEqual(code_res["status"], "ok")
            self.assertEqual(code_res["result"], 42)

            # Coding SWE
            c_lane = CodingLane()
            swe_res = await c_lane.dispatch_step(Step(step_id=3, lane="coding", intent="swe", value="ZeroDivisionError in matrix normalize"))
            self.assertEqual(swe_res["mode"], "swe_reproduction")

            # Mobile Subgoals
            m_lane = MobileLane()
            mob_res = await m_lane.dispatch_step(Step(step_id=4, lane="mobile", intent="subgoals", value="com.whatsapp"))
            self.assertEqual(mob_res["action"], "app_agent_subgoals")

            # Research Perspectives
            res_lane = ResearchLane()
            storm_res = await res_lane.dispatch_step(Step(step_id=5, lane="research", intent="perspectives", value="Quantum Algorithms"))
            self.assertEqual(storm_res["mode"], "multi_perspective")

            # Browser DOM Flattening
            b_lane = BrowserLane()
            dom_res = await b_lane.dispatch_step(Step(step_id=6, lane="browser", intent="browser_use", value="<button>Click</button>"))
            self.assertEqual(dom_res["mode"], "flatten_dom")

        asyncio.run(run_dispatches())

if __name__ == "__main__":
    unittest.main()
