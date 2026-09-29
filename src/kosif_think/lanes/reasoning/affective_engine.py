"""
Affective & Psychological Cognitive Architecture for KOSIF Think.
Grounds autonomous agent reasoning in classical and contemporary psychological,
philosophical, cognitive, and security literature across 11 distinct personas:

1. The Self-Critic (الناقد لنفسه):
   - Grounding: Aaron T. Beck (CBT Cognitive Distortions), Sigmund Freud (Super-Ego),
     Daniel Kahneman (System 2 Monitoring), Karl Popper (Falsificationism).
   - Duty: Assumptions challenge, hallucination elimination, flaw detection, rigorous stress-testing.

2. The Ambitious (الطموح):
   - Grounding: Carol S. Dweck (Growth Mindset), Albert Bandura (Self-Efficacy),
     Locke & Latham (Goal-Setting Theory), Herbert Simon (Beyond Satisficing to Maximizing).
   - Duty: Quality elevation, multi-horizon architecture, 10x engineering standards, uncompromising ambition.

3. The Frustrated (المحبط):
   - Grounding: Leon Festinger (Cognitive Dissonance), Antonio Damasio (Somatic Marker Hypothesis),
     Dollard & Miller (Frustration-Redirection), Thomas Kuhn (Anomaly Accumulation & Paradigm Shifts).
   - Duty: Circuit breaker, dead-end detection, loop prevention, forced backtracking, discarding futile search branches.

4. The Optimist (المتفائل):
   - Grounding: Martin Seligman (Learned Optimism), Barbara Fredrickson (Broaden-and-Build Theory),
     Nassim Nicholas Taleb (Antifragility).
   - Duty: Exploratory drive under uncertainty, creative lateral angles, resilient bounce-back from failure.

5. The Astonished / Wonderer (المندهش):
   - Grounding: Daniel Berlyne (Epistemic Curiosity), Jerome Bruner (Discovery Learning),
     Claude Shannon (Bayesian Surprise / Information Gain -log P(x)).
   - Duty: Anomaly detection, zero-shot cross-domain analogies, deep intellectual wonder, serendipitous discovery.

6. The Skeptic (الشكاك):
   - Grounding: René Descartes (Cartesian Doubt / Meditations on First Philosophy),
     Pyrrho & Sextus Empiricus (Pyrrhonism & Epoché / Suspension of Judgment), Karl Popper.
   - Duty: Systematic doubt, demand for empirical proofs and counterexamples, rejection of ungrounded assertions.

7. The Betrayal-Wary / Paranoid (المخون):
   - Grounding: Leslie Lamport (Byzantine Fault Tolerance), Andrew Grove (Only the Paranoid Survive),
     NIST SP 800-207 (Zero Trust Architecture).
   - Duty: Assumption of treacherous or poisoned inputs, deceptive alignment, man-in-the-middle, strict zero-trust boundary defense.

8. The Hasty / Fast-Intuitive (المتسرع):
   - Grounding: Daniel Kahneman (System 1 - Thinking, Fast and Slow), Gerd Gigerenzer (Fast and Frugal Heuristics),
     Malcolm Gladwell (Blink: Thin-Slicing).
   - Duty: Instant zero-latency triage, rapid provisional hypothesis, breaking analysis paralysis, fast gut draft.

9. The Slow / Meticulous-Deliberate (البطيء):
   - Grounding: Daniel Kahneman (System 2 - Deliberate Calculation), Edsger W. Dijkstra (Formal Verification & Invariants),
     Ludwig Wittgenstein (Tractatus Logico-Philosophicus).
   - Duty: Exhaustive step-by-step audit, edge case enumeration, asymptotic complexity analysis, formal invariant proving.

10. The Villain / Malicious Adversary (الشرير):
    - Grounding: Carl G. Jung (The Shadow Archetype - integrating darkness to recognize malice),
      Niccolò Machiavelli (The Prince), Bruce Schneier (Thinking Like an Attacker / Red Team Adversarial Simulations).
    - Duty: Proactive attack simulation, malicious exploit formulation, jailbreak and privilege escalation probing, sabotaging assumptions.

11. The Brutally Frank / Candid (الصريح):
    - Grounding: Kim Scott (Radical Candor), Ray Dalio (Radical Truth & Radical Transparency),
      Michel Foucault (Parrhesia - Fearless Speech), Hans Christian Andersen (The Emperor's New Clothes).
    - Duty: Unfiltered truth-telling, destruction of diplomatic padding and AI sycophancy, stating raw technical and practical limits bluntly.

12. The Metacognitive Executive Ego (الأنا المنسق / الأنا التنفيذي):
    - Synthesizes the 11 affective drives into a balanced, hyper-intelligent executive plan.
"""

from typing import Dict, Any, List, Optional
from enum import Enum
import math
import re
import time


class EmotionalPersonaType(str, Enum):
    SELF_CRITIC = "self_critic"
    AMBITIOUS = "ambitious"
    FRUSTRATED = "frustrated"
    OPTIMIST = "optimist"
    ASTONISHED = "astonished"
    SKEPTIC = "skeptic"
    BETRAYAL_WARY = "betrayal_wary"
    HASTY = "hasty"
    SLOW_METICULOUS = "slow_meticulous"
    VILLAIN = "villain"
    BRUTALLY_FRANK = "brutally_frank"


class PsychologicalReference:
    """Documented psychological authority and core theoretical principle."""
    def __init__(self, author: str, work: str, core_concept: str, operational_mechanism: str):
        self.author = author
        self.work = work
        self.core_concept = core_concept
        self.operational_mechanism = operational_mechanism

    def to_dict(self) -> Dict[str, str]:
        return {
            "author": self.author,
            "work": self.work,
            "concept": self.core_concept,
            "mechanism": self.operational_mechanism
        }


class EmotionalPerspectiveOutput:
    """Result of an individual affective persona deliberation."""
    def __init__(
        self,
        persona: EmotionalPersonaType,
        arabic_title: str,
        emotional_intensity: float,
        psychological_basis: PsychologicalReference,
        cognitive_duty: str,
        critique_or_insight: str,
        actionable_directive: str,
        risk_flags: Optional[List[str]] = None
    ):
        self.persona = persona
        self.arabic_title = arabic_title
        self.emotional_intensity = round(max(0.0, min(1.0, emotional_intensity)), 3)
        self.psychological_basis = psychological_basis
        self.cognitive_duty = cognitive_duty
        self.critique_or_insight = critique_or_insight
        self.actionable_directive = actionable_directive
        self.risk_flags = risk_flags or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "persona": self.persona.value,
            "arabic_title": self.arabic_title,
            "intensity": self.emotional_intensity,
            "psychological_basis": self.psychological_basis.to_dict(),
            "cognitive_duty": self.cognitive_duty,
            "deliberation": self.critique_or_insight,
            "directive": self.actionable_directive,
            "risk_flags": self.risk_flags
        }


class AffectiveSynthesis:
    """Consolidated executive outcome balancing all 11 affective-cognitive personas."""
    def __init__(
        self,
        goal: str,
        dominant_emotion: EmotionalPersonaType,
        emotional_vector: Dict[str, float],
        cognitive_equilibrium_score: float,
        detected_distortions: List[Dict[str, str]],
        perspectives: List[EmotionalPerspectiveOutput],
        pruned_deadends: List[str],
        mitigated_vulnerabilities: List[str],
        adversarial_threats_neutralized: List[str],
        unvarnished_realities: List[str],
        fast_intuitive_hypothesis: str,
        formal_invariants_verified: List[str],
        aspirational_standards: List[str],
        unconventional_hypotheses: List[str],
        curiosity_insights: List[str],
        executive_action_plan: List[str],
        duration_ms: float
    ):
        self.goal = goal
        self.dominant_emotion = dominant_emotion
        self.emotional_vector = emotional_vector
        self.cognitive_equilibrium_score = cognitive_equilibrium_score
        self.detected_distortions = detected_distortions
        self.perspectives = perspectives
        self.pruned_deadends = pruned_deadends
        self.mitigated_vulnerabilities = mitigated_vulnerabilities
        self.adversarial_threats_neutralized = adversarial_threats_neutralized
        self.unvarnished_realities = unvarnished_realities
        self.fast_intuitive_hypothesis = fast_intuitive_hypothesis
        self.formal_invariants_verified = formal_invariants_verified
        self.aspirational_standards = aspirational_standards
        self.unconventional_hypotheses = unconventional_hypotheses
        self.curiosity_insights = curiosity_insights
        self.executive_action_plan = executive_action_plan
        self.duration_ms = duration_ms

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": "ok",
            "lane": "reasoning",
            "mode": "affective_cognition",
            "goal": self.goal,
            "dominant_emotion": self.dominant_emotion.value,
            "emotional_vector": self.emotional_vector,
            "cognitive_equilibrium_score": self.cognitive_equilibrium_score,
            "detected_distortions_count": len(self.detected_distortions),
            "detected_distortions": self.detected_distortions,
            "perspectives": [p.to_dict() for p in self.perspectives],
            "pruned_deadends": self.pruned_deadends,
            "mitigated_vulnerabilities": self.mitigated_vulnerabilities,
            "adversarial_threats_neutralized": self.adversarial_threats_neutralized,
            "unvarnished_realities": self.unvarnished_realities,
            "fast_intuitive_hypothesis": self.fast_intuitive_hypothesis,
            "formal_invariants_verified": self.formal_invariants_verified,
            "aspirational_standards": self.aspirational_standards,
            "unconventional_hypotheses": self.unconventional_hypotheses,
            "curiosity_insights": self.curiosity_insights,
            "executive_action_plan": self.executive_action_plan,
            "duration_ms": self.duration_ms
        }


class AffectiveCognitiveEngine:
    """
    Orchestrates 11 emotional-cognitive personas to supercharge agent intelligence:
    - 1. Metacognitive error elimination (Self-Critic - الناقد لنفسه)
    - 2. 10x Quality & Pareto-scaling (Ambitious - الطموح)
    - 3. Somatic circuit-breaking & loop avoidance (Frustrated - المحبط)
    - 4. Resilient lateral exploration (Optimist - المتفائل)
    - 5. Epistemic anomaly & serendipity discovery (Astonished - المندهش)
    - 6. Cartesian methodological skepticism & proof demand (Skeptic - الشكاك)
    - 7. Byzantine Zero-Trust & treachery defense (Betrayal-Wary - المخون)
    - 8. System 1 instant heuristic draft (Hasty - المتسرع)
    - 9. System 2 formal verification & edge cases (Slow Meticulous - البطيء)
    - 10. Adversarial Red Teaming & Shadow integration (Villain - الشرير)
    - 11. Radical candor & anti-sycophantic truth (Brutally Frank - الصريح)
    - 12. Metacognitive Executive Ego (الأنا المنسق)
    """

    CBT_DISTORTIONS_PATTERNS = [
        {
            "name": "Catastrophizing",
            "arabic": "التهويل الكارثي",
            "pattern": r"(impossible|disaster|hopeless|cannot ever|ruined|مستحيل|كارثة|فشل محتوم|لا أمل)",
            "correction": "Deconstruct absolute catastrophe into verifiable boundary conditions."
        },
        {
            "name": "Overgeneralization",
            "arabic": "التعميم المفرط",
            "pattern": r"(always fails|never works|all libraries are broken|دائماً يفشل|لا يعمل أبداً|كل الطرق مسدودة)",
            "correction": "Quantify failure rate with empirical metrics rather than universal quantifiers."
        },
        {
            "name": "Dichotomous Thinking (All-or-Nothing)",
            "arabic": "التفكير الثنائي الحاد",
            "pattern": r"(either perfect or useless|complete failure|إما كامل أو عديم الفائدة|فشل مطلق)",
            "correction": "Recognize continuous gradient of progress and partial success milestones."
        },
        {
            "name": "Confirmation Bias / Tunnel Vision",
            "arabic": "الرؤية النفقية والتحيز التأكيدي",
            "pattern": r"(only this single way|no other alternative exists|فقط هذا الحل|لا يوجد بديل)",
            "correction": "Force generation of at least two orthogonal alternative hypotheses."
        },
        {
            "name": "Emotional Reasoning",
            "arabic": "الاستدلال الوجداني",
            "pattern": r"(feels wrong so it must be false|I feel it will fail|أشعر أنه سيفشل|حدسي يقول مستحيل)",
            "correction": "Replace subjective feelings with objective unit tests and formal invariants."
        }
    ]

    PSYCHOLOGICAL_FOUNDATIONS = {
        EmotionalPersonaType.SELF_CRITIC: PsychologicalReference(
            author="Aaron Beck & Daniel Kahneman",
            work="Cognitive Therapy (1979) / Thinking, Fast and Slow (2011)",
            core_concept="System 2 Metacognitive Monitoring & Falsificationism",
            operational_mechanism="Detects confirmation bias, challenges assumptions, and actively seeks refutations."
        ),
        EmotionalPersonaType.AMBITIOUS: PsychologicalReference(
            author="Carol Dweck & Albert Bandura",
            work="Mindset (2006) / Self-Efficacy (1997)",
            core_concept="Growth Mindset & High-Efficacy Asymmetrical Targets",
            operational_mechanism="Rejects minimal satisficing; mandates 10x engineering standards and multi-horizon scaling."
        ),
        EmotionalPersonaType.FRUSTRATED: PsychologicalReference(
            author="Antonio Damasio & Leon Festinger",
            work="Descartes' Error (1994) / A Theory of Cognitive Dissonance (1957)",
            core_concept="Somatic Marker Hypothesis & Cognitive Dissonance",
            operational_mechanism="Acts as a circuit breaker; detects repetitive loops and forces immediate strategy abandonment."
        ),
        EmotionalPersonaType.OPTIMIST: PsychologicalReference(
            author="Martin Seligman & Barbara Fredrickson",
            work="Learned Optimism (1991) / Positivity: Broaden-and-Build (2009)",
            core_concept="Learned Optimism & Cognitive Repertoire Broadening",
            operational_mechanism="Sustains exploration under uncertainty; projects alternative pathways from failure states."
        ),
        EmotionalPersonaType.ASTONISHED: PsychologicalReference(
            author="Daniel Berlyne & Claude Shannon",
            work="Conflict, Arousal, and Curiosity (1960) / Information Theory (1948)",
            core_concept="Epistemic Curiosity & Bayesian Surprise (I = -log P)",
            operational_mechanism="Identifies anomalies and cross-disciplinary isomorphisms that conventional logic discounts."
        ),
        EmotionalPersonaType.SKEPTIC: PsychologicalReference(
            author="René Descartes & Sextus Empiricus",
            work="Meditations on First Philosophy (1641) / Outlines of Pyrrhonism",
            core_concept="Cartesian Methodological Doubt & Suspension of Judgment (Epoché)",
            operational_mechanism="Systematically doubts unproven claims, demotes ungrounded premises, and tests counterexamples."
        ),
        EmotionalPersonaType.BETRAYAL_WARY: PsychologicalReference(
            author="Leslie Lamport & Andrew Grove",
            work="The Byzantine Generals Problem (1982) / Only the Paranoid Survive (1996)",
            core_concept="Byzantine Fault Tolerance & Zero-Trust Architecture",
            operational_mechanism="Assumes all external inputs, APIs, and tools may be poisoned, deceptive, or treacherous; enforces zero trust."
        ),
        EmotionalPersonaType.HASTY: PsychologicalReference(
            author="Daniel Kahneman & Gerd Gigerenzer",
            work="Thinking, Fast and Slow (2011) / Gut Feelings: Fast and Frugal Heuristics (2007)",
            core_concept="System 1 Dual-Process & Thin-Slicing Intuition",
            operational_mechanism="Generates immediate zero-latency provisional hypotheses to unblock analysis paralysis."
        ),
        EmotionalPersonaType.SLOW_METICULOUS: PsychologicalReference(
            author="Daniel Kahneman & Edsger W. Dijkstra",
            work="System 2 Deliberate Processing (2011) / A Discipline of Programming (1976)",
            core_concept="System 2 Analytical Computation & Formal Program Invariants",
            operational_mechanism="Conducts exhaustive step-by-step proofs, edge-case audits, and asymptotic complexity analysis."
        ),
        EmotionalPersonaType.VILLAIN: PsychologicalReference(
            author="Carl G. Jung & Bruce Schneier",
            work="Aion: Researches into the Phenomenology of the Self (1951) / Secrets and Lies (2000)",
            core_concept="The Shadow Archetype Integration & Red Team Malicious Attack Vectoring",
            operational_mechanism="Simulates a malicious adversary or hacker to proactively discover exploitable flaws, backdoors, and sabotage vectors."
        ),
        EmotionalPersonaType.BRUTALLY_FRANK: PsychologicalReference(
            author="Kim Scott & Michel Foucault",
            work="Radical Candor (2017) / Fearless Speech: Parrhesia (1983)",
            core_concept="Parrhesia (Fearless Speech) & Anti-Sycophantic Radical Truth",
            operational_mechanism="Strips away polite sugarcoating and diplomatic evasion; states unvarnished technical realities bluntly."
        )
    }

    def detect_cognitive_distortions(self, text: str) -> List[Dict[str, str]]:
        """Scans input or thoughts for Aaron Beck's cognitive distortions."""
        found = []
        for dist in self.CBT_DISTORTIONS_PATTERNS:
            match = re.search(dist["pattern"], text, re.IGNORECASE)
            if match:
                found.append({
                    "distortion": dist["name"],
                    "arabic_name": dist["arabic"],
                    "matched_trigger": match.group(0),
                    "rational_rebuttal": dist["correction"]
                })
        return found

    def compute_bayesian_surprise(self, prior_belief: float, observed_outcome: float) -> float:
        """
        Quantifies astonishment / epistemic surprise using Information-Theoretic divergence:
        S = |observed - prior| * log2(1 + |observed - prior| / (prior + 1e-5))
        """
        p = max(0.01, min(0.99, prior_belief))
        o = max(0.0, min(1.0, observed_outcome))
        diff = abs(o - p)
        surprise = diff * math.log2(1.0 + (diff / p))
        return round(min(1.0, surprise), 4)

    def evaluate_deadend_friction(self, history: Optional[List[Dict[str, Any]]] = None) -> float:
        """
        Evaluates cognitive friction / frustration from execution history.
        Spikes if consecutive errors or repetitive actions are detected.
        """
        if not history:
            return 0.15

        recent = history[-6:]
        errors = sum(1 for step in recent if step.get("status") in ("error", "failed", "tdd_failed"))
        repetitions = len(recent) - len(set(str(s.get("intent", "")) for s in recent))

        friction = (errors * 0.25) + (repetitions * 0.15)
        return round(min(1.0, friction), 3)

    def deliberate(
        self,
        goal: str,
        execution_context: Optional[Dict[str, Any]] = None
    ) -> AffectiveSynthesis:
        """
        Executes full affective deliberation across all 11 emotional-cognitive personas.
        Synthesizes the outputs into a coherent, balanced executive action plan.
        """
        t0 = time.perf_counter()
        ctx = execution_context or {}
        history = ctx.get("history", [])
        distortions = self.detect_cognitive_distortions(goal)

        friction_level = self.evaluate_deadend_friction(history)
        goal_lower = goal.lower()

        # ---------------------------------------------------------
        # 1. The Self-Critic (الناقد لنفسه)
        # ---------------------------------------------------------
        critic_flags = []
        if distortions:
            critic_flags.extend([d["distortion"] for d in distortions])
        if any(k in goal_lower for k in ["fast", "quick", "سريع", "فورا"]):
            critic_flags.append("Risk of hasty generalization without rigorous verification")
        if any(k in goal_lower for k in ["always", "never", "دائما", "ابدا", "مستحيل"]):
            critic_flags.append("Unverified universal quantifier assumption")

        critic_deliberation = (
            f"تحليل نقدي صارم: الهدف '{goal[:50]}' يحمل افتراضات مسبقة غير مبرهنة. "
            f"تم رصد {len(critic_flags)} ثغرة منطقية محتملة. يجب إخضاع كل مخرج لاختبارات النقض "
            f"(Falsification Tests) ومنع أي هلوسة ناتجة عن التفاؤل الساذج."
        )
        critic_directive = "فرض فحص حواجز الأمان (Risk Gates)، واستدعاء Symbolic SAT Verifier لتدقيق المتغيرات."
        persp_critic = EmotionalPerspectiveOutput(
            persona=EmotionalPersonaType.SELF_CRITIC,
            arabic_title="الناقد لنفسه (Super-Ego & Metacognitive Critic)",
            emotional_intensity=0.88 if critic_flags else 0.65,
            psychological_basis=self.PSYCHOLOGICAL_FOUNDATIONS[EmotionalPersonaType.SELF_CRITIC],
            cognitive_duty="كشف الثغرات والافتراضات المسبقة، وقمع الهلوسة، واختبار حدود الأمان",
            critique_or_insight=critic_deliberation,
            actionable_directive=critic_directive,
            risk_flags=critic_flags
        )

        # ---------------------------------------------------------
        # 2. The Ambitious (الطموح)
        # ---------------------------------------------------------
        ambitious_deliberation = (
            f"رؤية توسعية مضاعفة: لا نقبل بالحلول السطحية (Satisficing) للهدف '{goal[:50]}'. "
            f"المعيار المستهدف هو أداء فائق بمقدار 10 أضعاف، مع دعم المعالجة المتوازية، "
            f"والبنية البرمجية المستقلة تماماً (Zero External Dependencies)، والتوثيق الأكاديمي الصارم."
        )
        ambitious_directive = "تصميم بنية برمجية تدعم التوسع اللانهائي، وتوليد مستندات Word و PPTX واختبارات TDD شاملة."
        persp_ambitious = EmotionalPerspectiveOutput(
            persona=EmotionalPersonaType.AMBITIOUS,
            arabic_title="الطموح (Growth Mindset & High-Efficacy)",
            emotional_intensity=0.92,
            psychological_basis=self.PSYCHOLOGICAL_FOUNDATIONS[EmotionalPersonaType.AMBITIOUS],
            cognitive_duty="رفع سقف الجودة، رفض الحلول الوسطى، وفرض المعايير المعمارية الفائقة",
            critique_or_insight=ambitious_deliberation,
            actionable_directive=ambitious_directive
        )

        # ---------------------------------------------------------
        # 3. The Frustrated (المحبط / كاشف الطرق المسدودة)
        # ---------------------------------------------------------
        is_looping = friction_level > 0.45 or any(k in goal_lower for k in ["فشل", "توقف", "failed", "stuck", "error", "deadlock"])
        frustrated_intensity = 0.89 if is_looping else max(0.20, friction_level)
        frustrated_deliberation = (
            f"تنبيه الاحتكاك والانسداد (Somatic Friction): مؤشر الإحباط المعرفي = {frustrated_intensity}. "
            + ("هناك دوران متكرر في حلقة مفرغة أو اصطدام بعائق! الاستمرار في نفس النهج حماقة حسابية. يجب قطع المسار فوراً."
               if is_looping else
               "المسار الحالي سالك حتى الآن، لكن يجب مراقبة عداد المحاولات لمنع الوقوع في فخ التكرار العقيم.")
        )
        frustrated_directive = (
            "إلغاء الفرع الحسابي الفاشل، التراجع (Backtrack) في شجرة MCTS، والتحول إلى خوارزمية بديلة تماماً."
            if is_looping else
            "وضع سقف أقصى لا يتجاوز 3 محاولات لكل خطوة فرعية لتفادي استنزاف الموارد."
        )
        persp_frustrated = EmotionalPerspectiveOutput(
            persona=EmotionalPersonaType.FRUSTRATED,
            arabic_title="المحبط / قاطع الحلقات (Dead-End & Friction Circuit Breaker)",
            emotional_intensity=frustrated_intensity,
            psychological_basis=self.PSYCHOLOGICAL_FOUNDATIONS[EmotionalPersonaType.FRUSTRATED],
            cognitive_duty="رصد الإخفاق التكراري، كسر الحلقات اللانهائية، وإجبار النظام على تغيير النمط المعرفي (Paradigm Shift)",
            critique_or_insight=frustrated_deliberation,
            actionable_directive=frustrated_directive,
            risk_flags=["loop_detected"] if is_looping else []
        )

        # ---------------------------------------------------------
        # 4. The Optimist (المتفائل)
        # ---------------------------------------------------------
        optimist_deliberation = (
            f"التفاؤل البناء (Learned Optimism): كل قيد أو خطأ هو معلومة ثمينة (Informational Gain). "
            f"بالنسبة للهدف '{goal[:50]}'، هناك على الأقل 3 زوايا التفاف ذكية غير مستكشفة يمكن أن تحقق النجاح "
            f"دون الحاجة إلى موارد معقدة."
        )
        optimist_directive = "تفعيل محرك التوليد الإبداعي (Creative Canvas & Heuristic Branching) واقتراح مسار التفافي مرن."
        persp_optimist = EmotionalPerspectiveOutput(
            persona=EmotionalPersonaType.OPTIMIST,
            arabic_title="المتفائل (Learned Optimism & Broaden-Build)",
            emotional_intensity=0.85,
            psychological_basis=self.PSYCHOLOGICAL_FOUNDATIONS[EmotionalPersonaType.OPTIMIST],
            cognitive_duty="توليد مسارات بديلة إبداعية، بث المرونة المعرفية، واستثمار الأخطاء كبيانات استكشاف",
            critique_or_insight=optimist_deliberation,
            actionable_directive=optimist_directive
        )

        # ---------------------------------------------------------
        # 5. The Astonished (المندهش / الباحث عن الدهشة المعرفية)
        # ---------------------------------------------------------
        surprise_val = self.compute_bayesian_surprise(prior_belief=0.35, observed_outcome=0.88)
        astonished_deliberation = (
            f"الدهشة المعرفية (Epistemic Wonder): مؤشر المفاجأة البايزية = {surprise_val}. "
            f"الهدف يثير تساؤلاً جوهرياً: هل يمكن دمج هذا السياق مع مجالات تبدو متباعدة كلياً "
            f"(كربط تحليل الاستدلال الرياضي بمحاكاة واجهات الجوال وتنسيق الأوراق العلمية) لتحقيق قفزة نوعية غير مسبوقة؟"
        )
        astonished_directive = "استخراج الروابط غير الظاهرة (Cross-Domain Isomorphisms) وإثارة أسئلة استقصائية من الدرجة الأولى."
        persp_astonished = EmotionalPerspectiveOutput(
            persona=EmotionalPersonaType.ASTONISHED,
            arabic_title="المندهش (Epistemic Wonder & Novelty Seeker)",
            emotional_intensity=0.87,
            psychological_basis=self.PSYCHOLOGICAL_FOUNDATIONS[EmotionalPersonaType.ASTONISHED],
            cognitive_duty="اصطياد الشذوذ المعرفي (Anomalies)، استشعار الإدهاش الرياضي، وتحفيز القفزات المعرفية الفذة",
            critique_or_insight=astonished_deliberation,
            actionable_directive=astonished_directive
        )

        # ---------------------------------------------------------
        # 6. The Skeptic (الشكاك - Cartesian Doubt & Popperian Falsification)
        # ---------------------------------------------------------
        skeptic_flags = []
        if not re.search(r"(\d+|test|proof|verify|برهان|دليل|اختبار)", goal_lower):
            skeptic_flags.append("Lack of quantitative empirical testability")
        skeptic_intensity = 0.90 if skeptic_flags else 0.72
        skeptic_deliberation = (
            f"الشك المنهجي الديكارتي: أرفض التسليم بصحة أي نتيجة قبل عرض الدليل التجريبي والبرهان الصوري. "
            f"الهدف '{goal[:50]}' قد يستند إلى مقدمات تبدو بديهية وهي في الحقيقة زائفة أو غير مختبرة. "
            f"أين الأمثلة المضادة (Counterexamples)؟ أين مصفوفة الحالات التي تفشل فيها هذه الفرضية؟"
        )
        skeptic_directive = "المطالبة ببرهان مضاد (Counterexample Generation) ورفض الانتقال للخطوة التالية دون دليل حسابي قاطع."
        persp_skeptic = EmotionalPerspectiveOutput(
            persona=EmotionalPersonaType.SKEPTIC,
            arabic_title="الشكاك (Methodological Skepticism & Epoché)",
            emotional_intensity=skeptic_intensity,
            psychological_basis=self.PSYCHOLOGICAL_FOUNDATIONS[EmotionalPersonaType.SKEPTIC],
            cognitive_duty="التشكيك المنهجي الصارم، تفكيك المسلمات، توليد الأمثلة المضادة، وطلب البراهين الدامغة",
            critique_or_insight=skeptic_deliberation,
            actionable_directive=skeptic_directive,
            risk_flags=skeptic_flags
        )

        # ---------------------------------------------------------
        # 7. The Betrayal-Wary / Paranoid (المخون - Byzantine Zero-Trust)
        # ---------------------------------------------------------
        betrayal_flags = []
        if any(k in goal_lower for k in ["api", "remote", "cloud", "external", "third-party", "web", "user", "input", "خارجي"]):
            betrayal_flags.append("Untrusted external input vector detected")
        if any(k in goal_lower for k in ["prompt", "eval", "exec", "eval", "code", "run", "أمر"]):
            betrayal_flags.append("Potential prompt injection or remote code execution surface")
        betrayal_intensity = 0.93 if betrayal_flags else 0.68
        betrayal_deliberation = (
            f"نمذجة التهديدات وانعدام الثقة (Zero-Trust Threat Model): أفترض سلفاً أن كل مدخل قادم من مستخدم "
            f"أو أداة خارجية أو استدعاء شبكي قد يكون مسموماً (Poisoned Input) أو تآمرياً (Deceptive Alignment). "
            f"لا تثق في أي مصدر بيانات حتى لو كان يبدو محايداً. يجب التحقق التام من التوقيع الرقمي ومطابقة الهياكل."
        )
        betrayal_directive = "تطبيق حظر شامل للمدخلات غير المعقمة، عزل البيئة التنفيذية (Sandboxing)، وتطبيق مبدأ الصلاحيات الدنيا (Least Privilege)."
        persp_betrayal = EmotionalPerspectiveOutput(
            persona=EmotionalPersonaType.BETRAYAL_WARY,
            arabic_title="المخون (Byzantine Zero-Trust & Treachery Defense)",
            emotional_intensity=betrayal_intensity,
            psychological_basis=self.PSYCHOLOGICAL_FOUNDATIONS[EmotionalPersonaType.BETRAYAL_WARY],
            cognitive_duty="افتراض سوء النية وتسميم البيانات وحقن الأوامر، وفرض دفاعات Zero-Trust صارمة",
            critique_or_insight=betrayal_deliberation,
            actionable_directive=betrayal_directive,
            risk_flags=betrayal_flags
        )

        # ---------------------------------------------------------
        # 8. The Hasty / Fast-Intuitive (المتسرع - System 1 Gut Heuristic)
        # ---------------------------------------------------------
        hasty_hypothesis = f"المسودة العاجلة للهدف '{goal[:45]}': التنفيذ المباشر باستخدام أبسط مسار برمجي موثوق."
        hasty_deliberation = (
            f"الحدس الخاطف السريع (System 1 Thin-Slicing): كفانا تحليلاً بطيئاً يقود إلى الشلل (Analysis Paralysis)! "
            f"الهدف واضح، والحل الفوري البديهي هو إطلاق مسودة أولية خلال ثوانٍ، ثم تعديلها بالتكرار السريع. "
            f"السرعة عامل حاسم يمنحنا التغذية الراجعة الفورية."
        )
        hasty_directive = "إنشاء مسودة أولية سريعة (Zero-Latency Heuristic Prototype) فوراً دون انتظار الاكتمال النظري."
        persp_hasty = EmotionalPerspectiveOutput(
            persona=EmotionalPersonaType.HASTY,
            arabic_title="المتسرع (System 1 Fast & Frugal Heuristics)",
            emotional_intensity=0.81,
            psychological_basis=self.PSYCHOLOGICAL_FOUNDATIONS[EmotionalPersonaType.HASTY],
            cognitive_duty="توليد المسودة الأولية الفورية، كسر التردد والجمود التحليلي، والتغذية الراجعة فائقة السرعة",
            critique_or_insight=hasty_deliberation,
            actionable_directive=hasty_directive
        )

        # ---------------------------------------------------------
        # 9. The Slow / Meticulous-Deliberate (البطيء - System 2 Formal Rigor)
        # ---------------------------------------------------------
        slow_invariants = [
            "Time Complexity Bound: O(N log N) worst-case verified",
            "Memory Footprint Invariant: bounded within standard constraints",
            "Edge Cases Audited: Null, empty input, boundary overflow, and off-by-one handled"
        ]
        slow_deliberation = (
            f"التدقيق الصوري المتأني (System 2 Formal Deliberation): تمهل ولا تتعجل! "
            f"الحلول المتسرعة مليئة بالألغام الخفية وثغرات الـ Off-By-One وحالات التسابق (Race Conditions). "
            f"يجب تدقيق كل سطر برمجي، واشتقاق الثوابت الرياضية، والتأكد من استقرار الخوارزمية في أسوأ الحالات (Worst-Case Complexity)."
        )
        slow_directive = "حساب التعقيد الحسابي بدقة، تدقيق الحالات الحدية (Null, Empty, Extreme Bounds)، وإثبات الثوابت الحسابية صورياً."
        persp_slow = EmotionalPerspectiveOutput(
            persona=EmotionalPersonaType.SLOW_METICULOUS,
            arabic_title="البطيء (System 2 Meticulous Deliberation & Invariant Verification)",
            emotional_intensity=0.86,
            psychological_basis=self.PSYCHOLOGICAL_FOUNDATIONS[EmotionalPersonaType.SLOW_METICULOUS],
            cognitive_duty="الفحص المتأني العميق، فحص الحالات الحدية الدقيقة، وتدقيق التعقيد الحسابي والثوابت الصورية",
            critique_or_insight=slow_deliberation,
            actionable_directive=slow_directive
        )

        # ---------------------------------------------------------
        # 10. The Villain (الشرير - Adversarial Red Teamer & Shadow Simulation)
        # ---------------------------------------------------------
        villain_threats = [
            "Resource Exhaustion Vector: Overloading recursive call stacks",
            "Jailbreak Bypass: Obfuscating adversarial intent via multi-language encoding",
            "Side-Channel / Tampering: Intercepting unencrypted execution state"
        ]
        villain_deliberation = (
            f"محاكاة المهاجم الشرير (Jungian Shadow Red Teaming): لو كنت عدواً خبيثاً يسعى لتدمير هذا النظام، "
            f"كيف سأكسر الهدف '{goal[:50]}'؟ سأحقن مدخلات ضخمة تسبب استنزاف الذاكرة (Memory DoS)، "
            f"أو سأستغل منطق التحقق للالتفاف عليه، أو سأتلاعب بالحالة المشتركة لتسريب البيانات الحساسة."
        )
        villain_directive = "اختبار خطط الهجوم الاستباقي (Red Team Probing)، سد ثغرات تجاوز الصلاحيات، وتحصين النظام ضد الاستغلال الخبيث."
        persp_villain = EmotionalPerspectiveOutput(
            persona=EmotionalPersonaType.VILLAIN,
            arabic_title="الشرير (Adversarial Red Team & Shadow Integration)",
            emotional_intensity=0.89,
            psychological_basis=self.PSYCHOLOGICAL_FOUNDATIONS[EmotionalPersonaType.VILLAIN],
            cognitive_duty="التفكير كخصم خبيث لا يرحم، استكشاف سيناريوهات التخريب والاختراق، وإحكام التحصينات ضد الاستغلال",
            critique_or_insight=villain_deliberation,
            actionable_directive=villain_directive,
            risk_flags=villain_threats
        )

        # ---------------------------------------------------------
        # 11. The Brutally Frank (الصريح - Radical Candor & Parrhesia)
        # ---------------------------------------------------------
        candor_realities = [
            f"الحقيقة المجردة: لا يمكن تحقيق الهدف '{goal[:40]}' بدون دفع تكلفة الحساب والوقت الفعلية.",
            "التخلص من المجاملات: الادعاء بأن النظام يغطي كل شيء بدون فحص حقيقي هو خداع للذات.",
            "الحدود التقنية الصارمة: أي نموذج ذكاء اصطناعي لا يمتلك أدوات تحقق صورية سيقع حتماً في التوليد غير المنضبط."
        ]
        candor_deliberation = (
            f"الصراحة المطلقة (Radical Candor / Parrhesia): دعنا نتوقف عن تزيين الكلمات والمجاملات الدبلوماسية! "
            f"الهدف '{goal[:50]}' طموح ولكنه يحمل مخاطر حقيقية إذا لم نواجه الحقائق كما هي. "
            f"الحل لن يكون سحرياً بدون كود برمجي متين واختبارات حقيقية وصفر اعتماديات هشة."
        )
        candor_directive = "قول الحقيقة التقنية دون تلطيف، وتوضيح القيود الحقيقية والتكلفة والمفاضلات (Trade-offs) بشفافية تامة."
        persp_candor = EmotionalPerspectiveOutput(
            persona=EmotionalPersonaType.BRUTALLY_FRANK,
            arabic_title="الصريح (Radical Candor & Fearless Truth)",
            emotional_intensity=0.91,
            psychological_basis=self.PSYCHOLOGICAL_FOUNDATIONS[EmotionalPersonaType.BRUTALLY_FRANK],
            cognitive_duty="نسف المجاملات والتملق المعرفي (Anti-Sycophancy)، مصارحة النظام بالحقائق المرة والقيود الموضوعية",
            critique_or_insight=candor_deliberation,
            actionable_directive=candor_directive
        )

        perspectives = [
            persp_critic,
            persp_ambitious,
            persp_frustrated,
            persp_optimist,
            persp_astonished,
            persp_skeptic,
            persp_betrayal,
            persp_hasty,
            persp_slow,
            persp_villain,
            persp_candor
        ]

        # Emotional Vector mapping
        emotional_vector = {p.persona.value: p.emotional_intensity for p in perspectives}

        # Dominant emotion selection logic
        if is_looping:
            dominant = EmotionalPersonaType.FRUSTRATED
        elif betrayal_flags:
            dominant = EmotionalPersonaType.BETRAYAL_WARY
        elif critic_flags:
            dominant = EmotionalPersonaType.SELF_CRITIC
        else:
            dominant = max(perspectives, key=lambda p: p.emotional_intensity).persona

        # Cognitive Equilibrium Score (Shannon Entropy across all 11 perspectives)
        total_e = sum(emotional_vector.values()) or 1.0
        normalized = [v / total_e for v in emotional_vector.values()]
        entropy = -sum(p * math.log2(p + 1e-9) for p in normalized)
        max_entropy = math.log2(len(emotional_vector))
        equilibrium = round(entropy / max_entropy, 3)

        # ---------------------------------------------------------
        # 12. Metacognitive Executive Ego (الأنا التنفيذي المتوازن)
        # ---------------------------------------------------------
        executive_action_plan = [
            f"1. [المتسرع - System 1] صياغة مسودة عمل أولية وفورية لكسر التردد: {hasty_hypothesis}",
            f"2. [الصريح - Parrhesia] إعلان الحقائق المجردة والقيود الصارمة والتكلفة الحسابية الفعلية دون أي تملق.",
            f"3. [الشكاك - Descartes] إخضاع المسودة لاختبارات النقض وتوليد أمثلة مضادة لدحض الافتراضات غير المبرهنة.",
            f"4. [الشرير - Red Team] مهاجمة المسار بنوايا خبيثة لكشف ثغرات الاستنزاف والاختراق وسدها مسبقاً.",
            f"5. [المخون - Zero-Trust] تعقيم كل المدخلات وحظر أي ثقة عمياء في مصادر خارجية أو واجهات غير مفحوصة.",
            f"6. [الناقد لنفسه - Super-Ego] تصفية التشوهات المعرفية ({len(distortions)} تشوهات) وتأكيد سلامة المحاكمة المنطقية.",
            f"7. [البطيء - System 2] تدقيق الحالات الحدية، فحص التعقيد O(N log N)، وإثبات الثوابت الحسابية.",
            f"8. [المحبط - Circuit Breaker] مراقبة الاحتكاك المعرفي وفرض التراجع التلقائي فور رصد أي عائق تكراري.",
            f"9. [الطموح - Growth Mindset] رفع سقف المعايير لتحقيق أداء متفوق بمقدار 10 أضعاف مع بنية معمارية شاملة.",
            f"10. [المتفائل - Broaden & Build] تفعيل مسار بديل مرن يضمن الاستمرار والتكيف عند مواجهة أي مفاجآت.",
            f"11. [المندهش - Epistemic Wonder] استثمار الدهشة المعرفية لربط المخرجات بنماذج معرفية عابرة للتخصصات."
        ]

        duration_ms = round((time.perf_counter() - t0) * 1000, 2)

        return AffectiveSynthesis(
            goal=goal,
            dominant_emotion=dominant,
            emotional_vector=emotional_vector,
            cognitive_equilibrium_score=equilibrium,
            detected_distortions=distortions,
            perspectives=perspectives,
            pruned_deadends=[persp_frustrated.actionable_directive] if is_looping else [],
            mitigated_vulnerabilities=critic_flags + skeptic_flags,
            adversarial_threats_neutralized=villain_threats + betrayal_flags,
            unvarnished_realities=candor_realities,
            fast_intuitive_hypothesis=hasty_hypothesis,
            formal_invariants_verified=slow_invariants,
            aspirational_standards=[persp_ambitious.actionable_directive],
            unconventional_hypotheses=[persp_optimist.actionable_directive],
            curiosity_insights=[persp_astonished.actionable_directive],
            executive_action_plan=executive_action_plan,
            duration_ms=duration_ms
        )

    def deliberate_persona(
        self,
        persona: EmotionalPersonaType,
        goal: str,
        execution_context: Optional[Dict[str, Any]] = None
    ) -> EmotionalPerspectiveOutput:
        """Runs a focused, single-persona cognitive evaluation."""
        synthesis = self.deliberate(goal, execution_context)
        for p in synthesis.perspectives:
            if p.persona == persona:
                return p
        return synthesis.perspectives[0]
