"""
Multi-Provider LLM Router & Budget Limiter for KOSIF Think.
Inspired by LiteLLM, OpenRouter, and Ollama.
Manages automatic failover across OpenAI, Anthropic, Gemini, and Local Ollama,
tracks cumulative token usage and USD costs, and enforces session budget limits.

Providers with a ``ModelClient`` attached (see ``connectors/models.py``) are really called and their reported
token usage is billed. When no client is attached to any provider the router answers with a placeholder and
marks the record ``simulated: True`` so nothing downstream mistakes it for model output.
"""

from typing import Dict, Any, List, Optional, Iterable
import copy
import time
import os

from .models import ModelClient, ModelError
from ..model_gateway_router import ProviderModel, RouteRequest
from .verified_gateway import GatewayBlocked, execute_verified

class BudgetExceededException(Exception):
    """Raised when cumulative session cost exceeds configured hard limit."""
    pass


class ModelProvider:
    def __init__(self, provider_id: str, default_model: str, cost_per_1k_input: float, cost_per_1k_output: float):
        self.provider_id = provider_id
        self.default_model = default_model
        self.cost_per_1k_input = cost_per_1k_input
        self.cost_per_1k_output = cost_per_1k_output
        self.is_healthy = True
        self.consecutive_failures = 0

    def compute_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        input_cost = (prompt_tokens / 1000.0) * self.cost_per_1k_input
        output_cost = (completion_tokens / 1000.0) * self.cost_per_1k_output
        return round(input_cost + output_cost, 6)


class LLMRouter:
    """Dispatches completions across providers with automatic failover and budget control."""

    # Standard pricing approximations per 1k tokens
    CATALOG = {
        "openai": ModelProvider("openai", "gpt-4o", cost_per_1k_input=0.005, cost_per_1k_output=0.015),
        "anthropic": ModelProvider("anthropic", "claude-opus-5", cost_per_1k_input=0.005, cost_per_1k_output=0.025),
        "gemini": ModelProvider("gemini", "gemini-2.5-flash", cost_per_1k_input=0.0001, cost_per_1k_output=0.0004),
        "deepseek": ModelProvider("deepseek", "deepseek-r1", cost_per_1k_input=0.0005, cost_per_1k_output=0.002),
        "qwen": ModelProvider("qwen", "qwen-2.5-coder-32b", cost_per_1k_input=0.0002, cost_per_1k_output=0.0005),
        "llama": ModelProvider("llama", "llama-3.3-70b", cost_per_1k_input=0.0004, cost_per_1k_output=0.0008),
        "ollama": ModelProvider("ollama", "llama3:8b", cost_per_1k_input=0.0, cost_per_1k_output=0.0),  # Free local
        "openai_compatible": ModelProvider("openai_compatible", "local", cost_per_1k_input=0.0, cost_per_1k_output=0.0),
        "scripted": ModelProvider("scripted", "scripted", cost_per_1k_input=0.0, cost_per_1k_output=0.0),
    }

    def __init__(
        self,
        max_budget_usd: float = 10.0,
        primary_provider: str = "openai",
        max_session_budget_usd: Optional[float] = None,
        clients: Optional[Dict[str, ModelClient]] = None,
        **kwargs
    ):
        # Health flags are per router, not shared through the class attribute.
        self.CATALOG = copy.deepcopy(type(self).CATALOG)
        self.clients: Dict[str, ModelClient] = {}
        self.max_budget_usd = max_session_budget_usd if max_session_budget_usd is not None else max_budget_usd
        self.primary_provider = primary_provider
        self.failover_order = [primary_provider] + [p for p in
                               ("deepseek", "qwen", "gemini", "anthropic", "ollama", "openai_compatible", "scripted")
                               if p != primary_provider]
        self.cumulative_prompt_tokens = 0
        self.cumulative_completion_tokens = 0
        self.cumulative_cost_usd = 0.0
        self.request_history: List[Dict[str, Any]] = []
        for prov_id, client in (clients or {}).items():
            self.attach_client(client, prov_id)

    def attach_client(self, client: ModelClient, provider_id: Optional[str] = None) -> None:
        """Routes ``provider_id`` (default: the client's own provider) to a real model client."""
        prov_id = provider_id or client.provider
        if prov_id not in self.CATALOG:
            self.CATALOG[prov_id] = ModelProvider(prov_id, client.model, 0.0, 0.0)
        self.clients[prov_id] = client
        if prov_id not in self.failover_order:
            self.failover_order.append(prov_id)

    @property
    def is_simulated(self) -> bool:
        """True when no provider has a real client, so completions are placeholders."""
        return not self.clients

    @property
    def total_cost_usd(self) -> float:
        return self.cumulative_cost_usd

    def has_budget(self) -> bool:
        return self.cumulative_cost_usd < self.max_budget_usd

    def track_usage(self, provider_id: str, input_tokens: int, output_tokens: int) -> float:
        provider = self.CATALOG.get(provider_id, self.CATALOG["openai"])
        cost = provider.compute_cost(input_tokens, output_tokens)
        self.cumulative_prompt_tokens += input_tokens
        self.cumulative_completion_tokens += output_tokens
        self.cumulative_cost_usd = round(self.cumulative_cost_usd + cost, 6)
        return cost

    def route(self, prompt: str, required_capability: str = "general") -> Dict[str, Any]:
        """Routes prompt to the most optimal healthy provider."""
        if required_capability == "deep_reasoning":
            chosen = "anthropic" if self.CATALOG["anthropic"].is_healthy else "openai"
        elif required_capability in ("open_deep_reasoning", "math", "analysis", "deepseek"):
            chosen = "deepseek" if self.CATALOG.get("deepseek") and self.CATALOG["deepseek"].is_healthy else "anthropic"
        elif required_capability in ("coding", "code", "ast"):
            chosen = "qwen" if self.CATALOG.get("qwen") and self.CATALOG["qwen"].is_healthy else "openai"
        elif required_capability == "fast":
            chosen = "gemini" if self.CATALOG["gemini"].is_healthy else "openai"
        elif required_capability == "local":
            chosen = "ollama"
        else:
            chosen = self.primary_provider
        return {
            "selected_provider": chosen,
            "model": self.CATALOG[chosen].default_model,
            "has_budget": self.has_budget(),
            "remaining_budget_usd": round(self.max_budget_usd - self.cumulative_cost_usd, 4)
        }

    def estimate_tokens(self, text: str) -> int:
        """Rough heuristic: ~4 characters per token."""
        return max(1, len(text) // 4)

    def dispatch_completion(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        model_override: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: Optional[float] = None,
        *,
        policy_request: Optional[RouteRequest] = None,
        trusted_catalog: Optional[Iterable[ProviderModel]] = None,
        request_id: str = "",
    ) -> Dict[str, Any]:
        """Dispatches a completion through healthy providers in cascade order.

        With clients attached only those providers are tried, and the returned usage is what the provider
        reported. With none attached the reply is a placeholder flagged ``simulated: True``.
        """
        # Explicit opt-in: never silently downgrade a failed verified route
        # into the legacy (possibly simulated) completion cascade.
        if policy_request is not None:
            if trusted_catalog is None:
                raise GatewayBlocked("TRUSTED_CATALOG_REQUIRED")
            return execute_verified(
                self, prompt, policy_request, trusted_catalog,
                system_instruction=system_instruction, max_tokens=max_tokens,
                temperature=temperature, request_id=request_id,
            )
        t0 = time.perf_counter()
        simulated = self.is_simulated
        est_prompt_tokens = self.estimate_tokens(prompt) + self.estimate_tokens(system_instruction or "")

        last_error = None
        for prov_id in self.failover_order:
            provider = self.CATALOG.get(prov_id)
            if not provider or not provider.is_healthy:
                continue
            client = self.clients.get(prov_id)
            if not simulated and client is None:
                continue

            # Pre-budget check on the estimate
            est_cost = provider.compute_cost(est_prompt_tokens, min(max_tokens, 1024) if client else 150)
            if self.cumulative_cost_usd + est_cost > self.max_budget_usd:
                raise BudgetExceededException(
                    f"Cumulative cost (${self.cumulative_cost_usd:.4f}) exceeds hard limit (${self.max_budget_usd:.2f})"
                )

            try:
                if client is not None:
                    if model_override:
                        client.model = model_override
                    completion = client.complete(prompt, system=system_instruction, max_tokens=max_tokens,
                                                 temperature=temperature)
                    target_model = completion.model
                    response_text = completion.text
                    prompt_tokens = completion.input_tokens or est_prompt_tokens
                    completion_tokens = completion.output_tokens or self.estimate_tokens(response_text)
                    stop_reason = completion.stop_reason
                else:
                    target_model = model_override or provider.default_model
                    response_text = (f"[SIMULATED {provider.provider_id.upper()}:{target_model}] No model client is "
                                     f"configured; placeholder for: '{prompt[:60]}...'")
                    prompt_tokens = est_prompt_tokens
                    completion_tokens = self.estimate_tokens(response_text)
                    stop_reason = None
            except ModelError as ex:
                provider.consecutive_failures += 1
                if provider.consecutive_failures >= 3:
                    provider.is_healthy = False
                last_error = f"{prov_id}: {ex}"
                continue

            provider.consecutive_failures = 0
            actual_cost = provider.compute_cost(prompt_tokens, completion_tokens)
            self.cumulative_prompt_tokens += prompt_tokens
            self.cumulative_completion_tokens += completion_tokens
            self.cumulative_cost_usd = round(self.cumulative_cost_usd + actual_cost, 6)

            rec = {
                "provider": provider.provider_id,
                "model": target_model,
                "response": response_text,
                "simulated": client is None,
                "stop_reason": stop_reason,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
                "cost_usd": actual_cost,
                "cumulative_cost_usd": self.cumulative_cost_usd,
                "budget_remaining_usd": round(self.max_budget_usd - self.cumulative_cost_usd, 4),
                "duration_ms": round((time.perf_counter() - t0) * 1000, 2)
            }
            self.request_history.append(rec)
            return rec

        raise RuntimeError(f"All LLM providers in cascade failed. Last error: {last_error}")
