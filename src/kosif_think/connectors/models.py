"""
Model clients for KOSIF Think.

One small interface, ``ModelClient.complete(prompt, system=None, max_tokens=...)``, over:

- ``AnthropicClient``: Claude through the official ``anthropic`` SDK (``pip install kosif-think[claude]``).
- ``OllamaClient``: a local Ollama server (``/api/chat``), standard library only.
- ``OpenAICompatibleClient``: any ``/v1/chat/completions`` server (DeepSeek, OpenRouter, vLLM, llama.cpp,
  LM Studio), standard library only.
- ``ScriptedClient``: deterministic replies for tests and offline demos.

``resolve_default_client()`` picks one from the environment, or returns None so callers can say plainly that
no model is configured instead of pretending to reason.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Sequence, Union
import json
import os
import time
import urllib.error
import urllib.request


class ModelError(RuntimeError):
    """A model call failed (network, HTTP status, refusal or malformed reply)."""


@dataclass
class Completion:
    text: str
    provider: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    stop_reason: Optional[str] = None
    duration_ms: float = 0.0
    raw: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "provider": self.provider,
            "model": self.model,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "stop_reason": self.stop_reason,
            "duration_ms": self.duration_ms,
        }


class ModelClient:
    """Base class. Subclasses implement ``_complete``."""

    provider = "base"

    def __init__(self, model: str):
        self.model = model

    def complete(self, prompt: str, system: Optional[str] = None, max_tokens: int = 4096,
                 temperature: Optional[float] = None) -> Completion:
        t0 = time.perf_counter()
        result = self._complete(prompt, system, max_tokens, temperature)
        result.duration_ms = round((time.perf_counter() - t0) * 1000, 2)
        return result

    def _complete(self, prompt: str, system: Optional[str], max_tokens: int,
                  temperature: Optional[float]) -> Completion:
        raise NotImplementedError

    def describe(self) -> Dict[str, Any]:
        return {"provider": self.provider, "model": self.model}


class AnthropicClient(ModelClient):
    """Claude through the official Anthropic SDK. Reads ANTHROPIC_API_KEY unless a key is passed."""

    provider = "anthropic"
    DEFAULT_MODEL = "claude-opus-5"

    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None,
                 thinking: bool = True, effort: Optional[str] = None, client: Any = None):
        super().__init__(model or os.environ.get("KOSIF_CLAUDE_MODEL") or self.DEFAULT_MODEL)
        self.thinking = thinking
        self.effort = effort
        if client is not None:
            self._client = client
        else:
            try:
                import anthropic  # optional dependency
            except ImportError as ex:
                raise ModelError("The anthropic package is not installed: pip install 'kosif-think[claude]'") from ex
            self._client = anthropic.Anthropic(api_key=api_key) if api_key else anthropic.Anthropic()

    def _complete(self, prompt, system, max_tokens, temperature):
        kwargs: Dict[str, Any] = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            kwargs["system"] = system
        # Temperature is not sent: current Claude models reject non-default sampling parameters, and sample
        # diversity comes from thinking and from the prompt instead.
        if self.thinking:
            kwargs["thinking"] = {"type": "adaptive"}
        if self.effort:
            kwargs["output_config"] = {"effort": self.effort}
        try:
            response = self._client.messages.create(**kwargs)
        except Exception as ex:  # anthropic.APIError subclasses, connection errors
            raise ModelError(f"Claude request failed: {type(ex).__name__}: {ex}") from ex
        if response.stop_reason == "refusal":
            raise ModelError("Claude declined this request (stop_reason=refusal).")
        text = "".join(block.text for block in response.content if block.type == "text")
        usage = getattr(response, "usage", None)
        return Completion(
            text=text,
            provider=self.provider,
            model=getattr(response, "model", self.model),
            input_tokens=getattr(usage, "input_tokens", 0) or 0,
            output_tokens=getattr(usage, "output_tokens", 0) or 0,
            stop_reason=response.stop_reason,
        )


def _post_json(url: str, payload: Dict[str, Any], headers: Dict[str, str], timeout: float) -> Dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json",
                                                          "User-Agent": "KOSIF-Think/2.0", **headers})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as ex:
        body = ex.read().decode("utf-8", "replace")[:300]
        raise ModelError(f"HTTP {ex.code} from {url}: {body}") from ex
    except (urllib.error.URLError, TimeoutError, OSError) as ex:
        raise ModelError(f"Could not reach {url}: {ex}") from ex
    except json.JSONDecodeError as ex:
        raise ModelError(f"Malformed JSON from {url}") from ex


class OllamaClient(ModelClient):
    """A local Ollama server. No API key and no cost."""

    provider = "ollama"

    def __init__(self, model: Optional[str] = None, base_url: Optional[str] = None, timeout: float = 120.0):
        super().__init__(model or os.environ.get("KOSIF_OLLAMA_MODEL") or "llama3.1:8b")
        self.base_url = (base_url or os.environ.get("OLLAMA_HOST") or "http://localhost:11434").rstrip("/")
        self.timeout = timeout

    def _complete(self, prompt, system, max_tokens, temperature):
        messages = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": prompt}]
        options: Dict[str, Any] = {"num_predict": max_tokens}
        if temperature is not None:
            options["temperature"] = temperature
        body = _post_json(f"{self.base_url}/api/chat",
                          {"model": self.model, "messages": messages, "stream": False, "options": options},
                          {}, self.timeout)
        text = (body.get("message") or {}).get("content")
        if text is None:
            raise ModelError("Ollama reply has no message content.")
        return Completion(text=text, provider=self.provider, model=body.get("model", self.model),
                          input_tokens=body.get("prompt_eval_count", 0) or 0,
                          output_tokens=body.get("eval_count", 0) or 0,
                          stop_reason=body.get("done_reason"))


class OpenAICompatibleClient(ModelClient):
    """Any server that speaks ``POST {base_url}/chat/completions`` (DeepSeek, OpenRouter, vLLM, LM Studio)."""

    provider = "openai_compatible"

    def __init__(self, model: str, base_url: str, api_key: Optional[str] = None, timeout: float = 120.0,
                 provider_name: Optional[str] = None):
        super().__init__(model)
        self.base_url = base_url.rstrip("/")
        self._api_key = api_key
        self.timeout = timeout
        if provider_name:
            self.provider = provider_name

    def _complete(self, prompt, system, max_tokens, temperature):
        messages = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": prompt}]
        payload: Dict[str, Any] = {"model": self.model, "messages": messages, "max_tokens": max_tokens}
        if temperature is not None:
            payload["temperature"] = temperature
        headers = {"Authorization": f"Bearer {self._api_key}"} if self._api_key else {}
        body = _post_json(f"{self.base_url}/chat/completions", payload, headers, self.timeout)
        try:
            choice = body["choices"][0]
            text = choice["message"]["content"] or ""
        except (KeyError, IndexError, TypeError) as ex:
            raise ModelError("Reply has no choices[0].message.content.") from ex
        usage = body.get("usage") or {}
        return Completion(text=text, provider=self.provider, model=body.get("model", self.model),
                          input_tokens=usage.get("prompt_tokens", 0) or 0,
                          output_tokens=usage.get("completion_tokens", 0) or 0,
                          stop_reason=choice.get("finish_reason"))


Reply = Union[str, Callable[[str, Optional[str]], str]]


class ScriptedClient(ModelClient):
    """Deterministic replies for tests and offline demos.

    ``replies`` is either a sequence (consumed in order, the last one repeats) or a function
    ``(prompt, system) -> text``. Every call is recorded in ``calls``.
    """

    provider = "scripted"

    def __init__(self, replies: Union[Sequence[str], Callable[[str, Optional[str]], str]], model: str = "scripted"):
        super().__init__(model)
        self._replies = replies if callable(replies) else list(replies)
        self._index = 0
        self.calls: List[Dict[str, Any]] = []

    def _complete(self, prompt, system, max_tokens, temperature):
        self.calls.append({"prompt": prompt, "system": system, "max_tokens": max_tokens, "temperature": temperature})
        if callable(self._replies):
            text = self._replies(prompt, system)
        else:
            if not self._replies:
                raise ModelError("ScriptedClient has no replies.")
            text = self._replies[min(self._index, len(self._replies) - 1)]
            self._index += 1
        return Completion(text=text, provider=self.provider, model=self.model,
                          input_tokens=max(1, len(prompt) // 4), output_tokens=max(1, len(text) // 4),
                          stop_reason="end_turn")


def resolve_default_client(env: Optional[Dict[str, str]] = None) -> Optional[ModelClient]:
    """The client the environment configures, or None.

    ``KOSIF_MODEL_PROVIDER`` (anthropic | ollama | openai_compatible) chooses explicitly. Otherwise:
    ANTHROPIC_API_KEY -> Claude; KOSIF_OPENAI_BASE_URL -> an OpenAI-compatible server; OLLAMA_HOST -> Ollama.
    """
    env = dict(os.environ if env is None else env)
    choice = (env.get("KOSIF_MODEL_PROVIDER") or "").strip().lower()
    if not choice:
        if env.get("ANTHROPIC_API_KEY"):
            choice = "anthropic"
        elif env.get("KOSIF_OPENAI_BASE_URL"):
            choice = "openai_compatible"
        elif env.get("OLLAMA_HOST"):
            choice = "ollama"
        else:
            return None
    if choice == "anthropic":
        return AnthropicClient(model=env.get("KOSIF_CLAUDE_MODEL"), api_key=env.get("ANTHROPIC_API_KEY"))
    if choice == "ollama":
        return OllamaClient(model=env.get("KOSIF_OLLAMA_MODEL"), base_url=env.get("OLLAMA_HOST"))
    if choice in ("openai_compatible", "openai"):
        base = env.get("KOSIF_OPENAI_BASE_URL")
        model = env.get("KOSIF_OPENAI_MODEL")
        if not base or not model:
            raise ModelError("KOSIF_OPENAI_BASE_URL and KOSIF_OPENAI_MODEL must both be set.")
        return OpenAICompatibleClient(model=model, base_url=base, api_key=env.get("KOSIF_OPENAI_API_KEY"))
    raise ModelError(f"Unknown KOSIF_MODEL_PROVIDER: {choice}")
