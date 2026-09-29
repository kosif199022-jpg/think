"""
Unified Execution lanes for KOSIF Think (Super-Intelligence & Multi-Device Edition):
- Reasoning (Fast, Council, Cognitive, Tree of Thoughts, Graph of Thoughts, Reflexion, MCTS, DSPy, MultiAgentGraph, RepoIntelligence, ThoughtMap, DeepThink, Symbolic)
- Coding (AST Parser, Atomic Patcher, Test Sandbox, Repo Mapper, Autonomous Debugger, TDD)
- Graphics (SVG Builder, Diagram Synthesizer, Generative Canvas, Visual Layout Analyzer)
- Computer (Windows UI Automation, apps, window focus, keystrokes, clipboard, files, screen)
- Browser (Jev-Browser action graph, CDP, persistent Chrome, stealth bezier)
- WhatsApp (Messaging, media, delivery verification)
- iOS (Apple Shortcuts bridge, WDA developer client, iPhone control from ChatGPT)
- Voice (SAPI Voice synthesis, SSML, Audio transcription)
- Mobile (Unified Android ADB, UIAutomator, gestures, calling, SMS, iOS bridge)
- Telephony (Voice calls, VoIP, SIP, Twilio, IVR, Astra real-time conversational voice)
- Research (Academic ArXiv/PubMed search, literature reviews, LaTeX compilation, citations, statistics)
- Office (Microsoft Word .docx, PowerPoint .pptx & HTML decks, Excel .xlsx formulas & financial modeling)
"""

from .reasoning import (
    ReasoningLane, CouncilReasoning, CognitiveUnderstanding,
    TreeOfThoughts, GraphOfThoughts, ReflexionEngine, MCTSPlanner,
    DSPyOptimizer, DSPySignature, MultiAgentGraph, RepoIntelligence,
    CodeAgentInterpreter, RLVRReasoner, AffectiveCognitiveEngine,
    EmotionalPersonaType, AffectiveSynthesis
)
from .coding import (
    CodingLane, ASTCodeParser, AtomicPatcher,
    TestSandbox, RepoMapper, AutonomousDebugger,
    SWEAgentOrchestrator
)
from .graphics import (
    GraphicsLane, SVGBuilder, DiagramSynthesizer,
    GenerativeCanvas, VisualLayoutAnalyzer
)
from .computer import ComputerLane, AppControl, FileControl, ScreenState
from .browser import (
    BrowserLane, ActionGraph, JevDecisionRouter, PlaywrightCDPClient,
    BrowserUseEngine
)
from .whatsapp import WhatsAppLane, WhatsAppBridge
from .ios import IOSLane, ShortcutsBridge, WDAClient
from .voice import VoiceLane, VoiceSynthesizer, AudioTranscriber
from .mobile import MobileLane, AndroidController, AppAgentOrchestrator
from .telephony import TelephonyLane, CallManager, AstraVoiceSession
from .research import (
    ResearchLane, AcademicSearchEngine, AcademicPaper,
    LiteratureReviewSynthesizer, LatexBuilder, CitationEngine, StatisticalVerifier,
    PerspectiveResearchEngine
)
from .office import (
    OfficeLane, WordDocumentBuilder, PowerPointBuilder, Slide,
    ExcelEngine, ExcelWorksheet
)

__all__ = [
    "ReasoningLane",
    "CouncilReasoning",
    "CognitiveUnderstanding",
    "TreeOfThoughts",
    "GraphOfThoughts",
    "ReflexionEngine",
    "MCTSPlanner",
    "DSPyOptimizer",
    "DSPySignature",
    "MultiAgentGraph",
    "RepoIntelligence",
    "CodeAgentInterpreter",
    "RLVRReasoner",
    "AffectiveCognitiveEngine",
    "EmotionalPersonaType",
    "AffectiveSynthesis",
    "CodingLane",
    "ASTCodeParser",
    "AtomicPatcher",
    "TestSandbox",
    "RepoMapper",
    "AutonomousDebugger",
    "SWEAgentOrchestrator",
    "GraphicsLane",
    "SVGBuilder",
    "DiagramSynthesizer",
    "GenerativeCanvas",
    "VisualLayoutAnalyzer",
    "ComputerLane",
    "AppControl",
    "FileControl",
    "ScreenState",
    "BrowserLane",
    "ActionGraph",
    "JevDecisionRouter",
    "PlaywrightCDPClient",
    "BrowserUseEngine",
    "WhatsAppLane",
    "WhatsAppBridge",
    "IOSLane",
    "ShortcutsBridge",
    "WDAClient",
    "VoiceLane",
    "VoiceSynthesizer",
    "AudioTranscriber",
    "MobileLane",
    "AndroidController",
    "AppAgentOrchestrator",
    "TelephonyLane",
    "CallManager",
    "AstraVoiceSession",
    "ResearchLane",
    "AcademicSearchEngine",
    "AcademicPaper",
    "LiteratureReviewSynthesizer",
    "LatexBuilder",
    "CitationEngine",
    "StatisticalVerifier",
    "PerspectiveResearchEngine",
    "OfficeLane",
    "WordDocumentBuilder",
    "PowerPointBuilder",
    "Slide",
    "ExcelEngine",
    "ExcelWorksheet",
]
