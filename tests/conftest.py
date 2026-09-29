"""The suite runs offline: model settings from the developer's shell must not make tests call a real model."""

import os

for _name in ("ANTHROPIC_API_KEY", "KOSIF_MODEL_PROVIDER", "KOSIF_OPENAI_BASE_URL", "OLLAMA_HOST"):
    os.environ.pop(_name, None)
