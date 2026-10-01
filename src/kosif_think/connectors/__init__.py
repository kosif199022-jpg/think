"""
Connectors package: OpenAI-compatible API bridge, ChatGPT Custom Actions, and Multi-App Hub.
"""

from .openai_bridge import OpenAIBridge
from .app_hub import AppHub
from .models import (AnthropicClient, Completion, ModelClient, ModelError, OllamaClient, OpenAICompatibleClient,
                     ScriptedClient, resolve_default_client)

__all__ = ["OpenAIBridge", "AppHub", "AnthropicClient", "Completion", "ModelClient", "ModelError", "OllamaClient",
           "OpenAICompatibleClient", "ScriptedClient", "resolve_default_client"]
