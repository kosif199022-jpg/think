"""
Unit tests for the Affective & Psychological Cognitive Architecture in KOSIF Think:
Validates all 11 cognitive-emotional personas:
1. Self-Critic (الناقد لنفسه)
2. Ambitious (الطموح)
3. Frustrated (المحبط)
4. Optimist (المتفائل)
5. Astonished (المندهش)
6. Skeptic (الشكاك)
7. Betrayal-Wary / Paranoid (المخون)
8. Hasty / Fast-Intuitive (المتسرع)
9. Slow / Meticulous-Deliberate (البطيء)
10. Villain / Adversarial Red Team (الشرير)
11. Brutally Frank / Candid (الصريح)
plus the Metacognitive Executive Ego.
"""

import unittest
import asyncio
from kosif_think.lanes.reasoning.affective_engine import (
    AffectiveCognitiveEngine,
    EmotionalPersonaType,
    EmotionalPerspectiveOutput,
    AffectiveSynthesis,
    PsychologicalReference
)
from kosif_think.lanes.reasoning.engine import ReasoningLane
from kosif_think.core.planner import Step


class TestAffectiveCognitiveArchitecture(unittest.TestCase):

    def setUp(self):
        self.engine = AffectiveCognitiveEngine()
        self.reasoning_lane = ReasoningLane()

    def test_all_11_personas_defined_and_grounded(self):
        """Ensures all 11 personas exist in enum and have authoritative psychological grounding."""
        expected_personas = [
            EmotionalPersonaType.SELF_CRITIC,
            EmotionalPersonaType.AMBITIOUS,
            EmotionalPersonaType.FRUSTRATED,
            EmotionalPersonaType.OPTIMIST,
            EmotionalPersonaType.ASTONISHED,
            EmotionalPersonaType.SKEPTIC,
            EmotionalPersonaType.BETRAYAL_WARY,
            EmotionalPersonaType.HASTY,
            EmotionalPersonaType.SLOW_METICULOUS,
            EmotionalPersonaType.VILLAIN,
            EmotionalPersonaType.BRUTALLY_FRANK,
        ]
        self.assertEqual(len(expected_personas), 11)

        for p in expected_personas:
            self.assertIn(p, self.engine.PSYCHOLOGICAL_FOUNDATIONS)
            ref = self.engine.PSYCHOLOGICAL_FOUNDATIONS[p]
            self.assertIsInstance(ref, PsychologicalReference)
            self.assertTrue(len(ref.author) > 3)
            self.assertTrue(len(ref.work) > 3)
            self.assertTrue(len(ref.core_concept) > 5)
            self.assertTrue(len(ref.operational_mechanism) > 10)
            d = ref.to_dict()
            self.assertIn("author", d)
            self.assertIn("work", d)
            self.assertIn("concept", d)
            self.assertIn("mechanism", d)

    def test_cognitive_distortion_detection(self):
        """Validates detection of Aaron Beck's CBT distortions in reasoning text."""
        # Catastrophizing
        d1 = self.engine.detect_cognitive_distortions("This system is impossible and a total disaster doomed to fail")
        self.assertTrue(any(x["distortion"] == "Catastrophizing" for x in d1))

        # Overgeneralization
        d2 = self.engine.detect_cognitive_distortions("كل الطرق مسدودة والبرمجيات دائماً تفشل")
        self.assertTrue(any(x["distortion"] == "Overgeneralization" for x in d2))

        # All-or-nothing
        d3 = self.engine.detect_cognitive_distortions("It is either perfect or useless completely")
        self.assertTrue(any(x["distortion"] == "Dichotomous Thinking (All-or-Nothing)" for x in d3))

        # Confirmation bias / tunnel vision
        d4 = self.engine.detect_cognitive_distortions("لا يوجد بديل سوى هذا الحل")
        self.assertTrue(any(x["distortion"] == "Confirmation Bias / Tunnel Vision" for x in d4))

        # Emotional reasoning
        d5 = self.engine.detect_cognitive_distortions("أشعر أنه سيفشل حتماً")
        self.assertTrue(any(x["distortion"] == "Emotional Reasoning" for x in d5))

    def test_bayesian_surprise_quantification(self):
        """Tests information-theoretic surprise for The Astonished persona."""
        low_surprise = self.engine.compute_bayesian_surprise(prior_belief=0.5, observed_outcome=0.52)
        high_surprise = self.engine.compute_bayesian_surprise(prior_belief=0.05, observed_outcome=0.95)
        self.assertLess(low_surprise, high_surprise)
        self.assertGreaterEqual(low_surprise, 0.0)
        self.assertLessEqual(high_surprise, 1.0)

    def test_frustrated_circuit_breaker_on_friction(self):
        """Tests that high execution friction triggers The Frustrated circuit-breaker."""
        failing_history = [
            {"intent": "fetch", "status": "failed"},
            {"intent": "fetch", "status": "failed"},
            {"intent": "fetch", "status": "error"},
            {"intent": "fetch", "status": "error"},
        ]
        friction = self.engine.evaluate_deadend_friction(failing_history)
        self.assertGreater(friction, 0.5)

        synthesis = self.engine.deliberate(
            goal="stuck in recursive deadlock",
            execution_context={"history": failing_history}
        )
        self.assertEqual(synthesis.dominant_emotion, EmotionalPersonaType.FRUSTRATED)
        self.assertTrue(len(synthesis.pruned_deadends) > 0)

    def test_deliberate_all_11_personas(self):
        """Tests full synthesis across all 11 emotional-cognitive personas."""
        goal = "Build an autonomous self-healing distributed trading engine with cloud browser automation"
        synthesis = self.engine.deliberate(goal)

        self.assertIsInstance(synthesis, AffectiveSynthesis)
        self.assertEqual(len(synthesis.perspectives), 11)
        self.assertEqual(len(synthesis.emotional_vector), 11)

        # Equilibrium score should be between 0.0 and 1.0
        self.assertGreaterEqual(synthesis.cognitive_equilibrium_score, 0.0)
        self.assertLessEqual(synthesis.cognitive_equilibrium_score, 1.0)

        # Executive plan should harmonize all 11 perspectives
        self.assertEqual(len(synthesis.executive_action_plan), 11)
        self.assertTrue(any("المتسرع" in s for s in synthesis.executive_action_plan))
        self.assertTrue(any("الصريح" in s for s in synthesis.executive_action_plan))
        self.assertTrue(any("الشكاك" in s for s in synthesis.executive_action_plan))
        self.assertTrue(any("الشرير" in s for s in synthesis.executive_action_plan))
        self.assertTrue(any("المخون" in s for s in synthesis.executive_action_plan))
        self.assertTrue(any("الناقد لنفسه" in s for s in synthesis.executive_action_plan))
        self.assertTrue(any("البطيء" in s for s in synthesis.executive_action_plan))
        self.assertTrue(any("المحبط" in s for s in synthesis.executive_action_plan))
        self.assertTrue(any("الطموح" in s for s in synthesis.executive_action_plan))
        self.assertTrue(any("المتفائل" in s for s in synthesis.executive_action_plan))
        self.assertTrue(any("المندهش" in s for s in synthesis.executive_action_plan))

        # Check dictionary serialization
        data = synthesis.to_dict()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["lane"], "reasoning")
        self.assertEqual(data["mode"], "affective_cognition")
        self.assertEqual(len(data["perspectives"]), 11)
        self.assertIn("fast_intuitive_hypothesis", data)
        self.assertIn("unvarnished_realities", data)
        self.assertIn("formal_invariants_verified", data)

    def test_single_persona_deliberation(self):
        """Tests deliberate_persona for focused individual perspectives."""
        # Villain
        p_villain = self.engine.deliberate_persona(
            EmotionalPersonaType.VILLAIN,
            "Run script eval(user_input) on AWS cluster"
        )
        self.assertEqual(p_villain.persona, EmotionalPersonaType.VILLAIN)
        self.assertIn("الشرير", p_villain.arabic_title)
        self.assertTrue(len(p_villain.risk_flags) > 0)

        # Brutally Frank
        p_candor = self.engine.deliberate_persona(
            EmotionalPersonaType.BRUTALLY_FRANK,
            "Deploy global real-time zero-latency multi-region DB in 5 minutes"
        )
        self.assertEqual(p_candor.persona, EmotionalPersonaType.BRUTALLY_FRANK)
        self.assertIn("الصريح", p_candor.arabic_title)
        self.assertIn("Radical Candor", p_candor.psychological_basis.work)

        # Skeptic
        p_skeptic = self.engine.deliberate_persona(
            EmotionalPersonaType.SKEPTIC,
            "This algorithm is guaranteed to always solve P=NP without proof"
        )
        self.assertEqual(p_skeptic.persona, EmotionalPersonaType.SKEPTIC)
        self.assertIn("الشكاك", p_skeptic.arabic_title)
        self.assertIn("Descartes", p_skeptic.psychological_basis.author)

        # Hasty vs Slow
        p_hasty = self.engine.deliberate_persona(EmotionalPersonaType.HASTY, "Fix login button CSS")
        p_slow = self.engine.deliberate_persona(EmotionalPersonaType.SLOW_METICULOUS, "Fix login button CSS")
        self.assertIn("المتسرع", p_hasty.arabic_title)
        self.assertIn("البطيء", p_slow.arabic_title)

    def test_reasoning_lane_integration(self):
        """Tests that ReasoningLane dispatches affective cognition seamlessly."""
        # Full affective synthesis
        step = Step(
            step_id=1,
            lane="reasoning",
            intent="affective",
            value="Synthesize quantum-resistant cryptographic lattice"
        )
        res = asyncio.run(self.reasoning_lane.dispatch_step(step))
        self.assertEqual(res["status"], "ok")
        self.assertEqual(res["lane"], "reasoning")
        self.assertEqual(res["mode"], "affective_cognition")
        self.assertEqual(len(res["perspectives"]), 11)

        # Individual persona dispatch via context
        step_skeptic = Step(
            step_id=2,
            lane="reasoning",
            intent="affective_persona",
            value="Asserting system has 100% uptime with no downtime possible",
            context={"persona": "skeptic"}
        )
        res_sk = asyncio.run(self.reasoning_lane.dispatch_step(step_skeptic))
        self.assertEqual(res_sk["status"], "ok")
        self.assertEqual(res_sk["mode"], "affective_persona")
        self.assertEqual(res_sk["persona"], "skeptic")
        self.assertIn("الشكاك", res_sk["arabic_title"])


if __name__ == "__main__":
    unittest.main()
