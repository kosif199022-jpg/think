"""
Execution lanes for KOSIF Think:
- Reasoning (Fast Heuristic, Council, Deep Cognitive)
- Computer (Windows UI Automation, apps, files, screen)
- Browser (Jev-Browser action graph, CDP, persistent Chrome)
- WhatsApp (Messaging, media, delivery verification)
"""

from .reasoning import ReasoningLane, CouncilReasoning, CognitiveUnderstanding
from .computer import ComputerLane, AppControl, FileControl, ScreenState
from .browser import BrowserLane, ActionGraph, JevDecisionRouter, PlaywrightCDPClient
from .whatsapp import WhatsAppLane, WhatsAppBridge

__all__ = [
    "ReasoningLane",
    "CouncilReasoning",
    "CognitiveUnderstanding",
    "ComputerLane",
    "AppControl",
    "FileControl",
    "ScreenState",
    "BrowserLane",
    "ActionGraph",
    "JevDecisionRouter",
    "PlaywrightCDPClient",
    "WhatsAppLane",
    "WhatsAppBridge",
]
