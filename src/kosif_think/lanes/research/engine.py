"""
Scientific Research & Academic Intelligence Lane Engine for KOSIF Think.
Dispatches paper retrieval, literature review synthesis, LaTeX paper drafting,
citation generation, and statistical rigor validation.
"""

from typing import Dict, Any, List, Optional
import time
from .academic_search import AcademicSearchEngine
from .literature_review import LiteratureReviewSynthesizer
from .latex_builder import LatexBuilder
from .citations import CitationEngine
from .stats_verifier import StatisticalVerifier
from .storm_engine import PerspectiveResearchEngine
from ...core.cancellation import CancellationToken

class ResearchLane:
    """Unified execution lane for academic and scientific research."""

    def __init__(self):
        self.search = AcademicSearchEngine()
        self.review = LiteratureReviewSynthesizer()
        self.latex = LatexBuilder()
        self.citations = CitationEngine()
        self.stats = StatisticalVerifier()
        self.storm = PerspectiveResearchEngine()

    async def dispatch_step(self, step: Any, cancellation_token: Optional[CancellationToken] = None) -> Dict[str, Any]:
        """Dispatches an action in the research lane."""
        if cancellation_token:
            cancellation_token.throw_if_cancellation_requested()

        t0 = time.perf_counter()
        intent = str(getattr(step, "intent", "search")).lower()
        target_ref = str(getattr(getattr(step, "target", None), "ref", "") or "")
        val = getattr(step, "value", None)
        args = getattr(step, "args", {}) or {}

        # 1. Academic Paper Search
        if intent in ("search", "paper_search", "arxiv"):
            q = target_ref or str(val or "Deep Reasoning in Artificial Intelligence")
            max_r = int(args.get("limit", 5))
            papers = self.search.search_arxiv(q, max_results=max_r)
            return {
                "status": "ok",
                "lane": "research",
                "action": "search",
                "query": q,
                "count": len(papers),
                "papers": papers,
                "latency_ms": round((time.perf_counter() - t0) * 1000, 2)
            }

        # 2. Literature Review Synthesis
        elif intent in ("review", "literature_review", "survey"):
            topic = target_ref or str(val or "Test-Time Compute and Verifiable Reasoning")
            papers = args.get("papers") or self.search.search_local_corpus(topic, max_results=5)
            review_res = self.review.synthesize_review(topic, papers)
            review_res["lane"] = "research"
            review_res["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
            return review_res

        # 3. LaTeX Academic Paper Generation
        elif intent in ("latex", "compile_latex", "paper_draft"):
            title = target_ref or str(val or "Scalable Autonomous Cognitive Systems")
            authors = args.get("authors", ["KOSIF Research Team"])
            abstract = args.get("abstract", "We present a unified multimodal agentic framework capable of test-time deliberate search, deep reasoning, and multi-device execution.")
            sections = args.get("sections") or [
                {"title": "Introduction", "content": "Recent foundation models demonstrate remarkable task adaptability, yet remain susceptible to planning horizon breakdown in dynamic environments."},
                {"title": "Methodology", "content": "Our architecture combines continuous Bayesian belief propagation with symbolic truth verification."},
                {"title": "Empirical Evaluation", "content": "Experiments conducted on multi-step reasoning benchmarks demonstrate superior consistency and verifiable accuracy."},
                {"title": "Conclusion", "content": "We have established that verifiable external feedback loops substantially enhance autonomous execution."}
            ]
            latex_code = self.latex.generate_paper_latex(
                title=title,
                authors=authors,
                abstract=abstract,
                sections=sections,
                equations=args.get("equations")
            )
            return {
                "status": "ok",
                "lane": "research",
                "action": "latex",
                "title": title,
                "latex_code": latex_code,
                "latency_ms": round((time.perf_counter() - t0) * 1000, 2)
            }

        # 4. Citations & BibTeX
        elif intent in ("cite", "citation", "bibtex"):
            paper_data = val if isinstance(val, dict) else {
                "title": target_ref or "DeepSeek-R1 Technical Report",
                "authors": ["Daya Guo", "Dejian Yang"],
                "year": 2025,
                "paper_id": "2501.12948"
            }
            bib = self.citations.to_bibtex(paper_data)
            apa = self.citations.to_apa(paper_data)
            ieee = self.citations.to_ieee(paper_data)
            return {
                "status": "ok",
                "lane": "research",
                "bibtex": bib,
                "apa": apa,
                "ieee": ieee,
                "latency_ms": round((time.perf_counter() - t0) * 1000, 2)
            }

        # 5. Statistical Rigor Verification
        elif intent in ("stats", "verify_stats", "t_test"):
            g_a = args.get("group_a", [82.5, 84.1, 86.3, 85.0, 87.2])
            g_b = args.get("group_b", [76.0, 78.4, 75.2, 79.1, 77.0])
            t_res = self.stats.two_sample_t_test(g_a, g_b)
            ci_res = self.stats.confidence_interval(g_a)
            return {
                "status": "ok",
                "lane": "research",
                "t_test": t_res,
                "confidence_interval": ci_res,
                "latency_ms": round((time.perf_counter() - t0) * 1000, 2)
            }

        # 6. Co-STORM Perspective-Guided Academic Exploration
        elif intent in ("storm", "perspectives", "question_tree", "academic_tree"):
            topic = target_ref or str(val or "Frontier Artificial Intelligence")
            if "tree" in intent or args.get("mode") == "tree":
                q_tree = self.storm.generate_question_tree(topic)
                return {
                    "status": "ok",
                    "lane": "research",
                    "mode": "question_tree",
                    "tree": q_tree,
                    "latency_ms": round((time.perf_counter() - t0) * 1000, 2)
                }
            persp = self.storm.expand_perspectives(topic)
            return {
                "status": "ok",
                "lane": "research",
                "mode": "multi_perspective",
                "topic": topic,
                "perspectives": persp,
                "latency_ms": round((time.perf_counter() - t0) * 1000, 2)
            }

        return {
            "status": "ok",
            "lane": "research",
            "action": intent,
            "latency_ms": round((time.perf_counter() - t0) * 1000, 2)
        }
