"""
Scientific Research & Academic Intelligence Lane for KOSIF Think.
"""

from .academic_search import AcademicSearchEngine, AcademicPaper
from .literature_review import LiteratureReviewSynthesizer
from .latex_builder import LatexBuilder
from .citations import CitationEngine
from .stats_verifier import StatisticalVerifier
from .engine import ResearchLane

__all__ = [
    "AcademicSearchEngine",
    "AcademicPaper",
    "LiteratureReviewSynthesizer",
    "LatexBuilder",
    "CitationEngine",
    "StatisticalVerifier",
    "ResearchLane"
]
