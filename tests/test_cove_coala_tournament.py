"""
Unit tests for CoVe (Chain-of-Verification), CoALA Cognitive Memory, and Tournament Verifier.
"""

import unittest
import asyncio
from kosif_think.lanes.reasoning.cove import ChainOfVerification
from kosif_think.lanes.reasoning.coala_memory import CoALAMemorySystem
from kosif_think.lanes.reasoning.tournament_verifier import TournamentVerifier, CandidateSolution
from kosif_think.lanes.reasoning.engine import ReasoningLane
from kosif_think.core.planner import Step

class TestCoveCoalaTournament(unittest.TestCase):

    def test_cove_verification(self):
        cove = ChainOfVerification()
        res = cove.verify_and_synthesize("Transfer funds securely and verify confirmation")
        self.assertEqual(res["mode"], "chain_of_verification")
        self.assertTrue(res["all_verified"])
        self.assertGreaterEqual(res["verification_questions_count"], 4)
        self.assertIn("verified_response", res)
        self.assertIn("Safety Gate", [v["question"] for v in res["verifications"]][3])

    def test_coala_memory_system(self):
        mem = CoALAMemorySystem()
        
        # Working Memory
        mem.set_working_focus("Refactor payment processing module", ["payments", "stripe"])
        self.assertEqual(mem.working_memory["current_goal"], "Refactor payment processing module")
        self.assertIn("payments", mem.working_memory["focus_entities"])
        
        # Episodic Memory
        mem.record_episode("Checkout test", ["click_buy", "wait_for_pin"], "Payment confirmed", True)
        self.assertEqual(len(mem.episodic_memory), 1)
        
        # Semantic Memory
        mem.learn_semantic_fact("policy.timeout", "All network calls must time out within 15 seconds")
        self.assertIn("policy.timeout", mem.semantic_memory)
        
        # Associative retrieval
        ctx = mem.retrieve_relevant_context("browser payment safety")
        self.assertIn("invariants.safety", ctx["relevant_semantics"])
        self.assertIn("browser.search", ctx["matched_procedures"])

    def test_tournament_verifier(self):
        verifier = TournamentVerifier()
        res = verifier.run_tournament("Optimize database queries under heavy load")
        self.assertIn("winner_id", res)
        self.assertIn("winner_title", res)
        self.assertGreaterEqual(res["winner_score"], 0.8)
        self.assertEqual(len(res["matches"]), 3)  # 2 semifinals + 1 final
        self.assertIn(res["winner_id"], ["C1_Linear", "C2_Verified", "C3_Optimistic", "C4_Council"])

    def test_reasoning_lane_integration(self):
        lane = ReasoningLane()
        
        # CoVe via lane dispatch
        step_cove = Step(step_id=1, lane="reasoning", intent="cove", value="Verify cryptographic signature")
        res_cove = asyncio.run(lane.dispatch_step(step_cove))
        self.assertEqual(res_cove["status"], "ok")
        self.assertEqual(res_cove["mode"], "chain_of_verification")
        
        # CoALA via lane dispatch
        step_coala = Step(step_id=2, lane="reasoning", intent="coala", value="browser automation memory")
        res_coala = asyncio.run(lane.dispatch_step(step_coala))
        self.assertEqual(res_coala["status"], "ok")
        self.assertEqual(res_coala["mode"], "coala_memory")
        self.assertIn("memory_context", res_coala)
        
        # Tournament via lane dispatch
        step_tour = Step(step_id=3, lane="reasoning", intent="tournament", value="Autonomous self-healing plan")
        res_tour = asyncio.run(lane.dispatch_step(step_tour))
        self.assertEqual(res_tour["status"], "ok")
        self.assertIn("winner_id", res_tour)

if __name__ == "__main__":
    unittest.main()
