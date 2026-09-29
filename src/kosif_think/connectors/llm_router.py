"""
Multi-Provider LLM Router & Budget Limiter for KOSIF Think.
Inspired by LiteLLM, OpenRouter, and Ollama.
Manages automatic failover across OpenAI, Anthropic, Gemini, and Local Ollama,
tracks cumulative token usage and USD costs, and enforces session budget limits.
Zero external dependencies. Pure Python.
"""

from typing import Dict, Any, List, Optional
import time
import os

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
        "anthropic": ModelProvider("anthropic", "claude-3-5-sonnet", cost_per_1k_input=0.003, cost_per_1k_output=0.015),
        "gemini": ModelProvider("gemini", "gemini-2.5-flash", cost_per_1k_input=0.0001, cost_per_1k_output=0.0004),
        "ollama": ModelProvider("ollama", "llama3:8b", cost_per_1k_input=0.0, cost_per_1k_output=0.0)  # Free local
    }

    def __init__(
        self,
        max_budget_usd: float = 10.0,
        primary_provider: str = "openai",
        max_session_budget_usd: Optional[float] = None,
        **kwargs
    ):
        self.max_budget_usd = max_session_budget_usd if max_session_budget_usd is not None else max_budget_usd
        self.primary_provider = primary_provider
        self.failover_order = [primary_provider, "gemini", "anthropic", "ollama"]
        self.cumulative_prompt_tokens = 0
        self.cumulative_completion_tokens = 0
        self.cumulative_cost_usd = 0.0
        self.request_history: List[Dict[str, Any]] = []

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
        model_override: Optional[str] = None
    ) -> Dict[str, Any]:
        """Dispatches completion through healthy providers in cascade order."""
        t0 = time.perf_counter()
        prompt_tokens = self.estimate_tokens(prompt) + self.estimate_tokens(system_instruction or "")

        last_error = None
        for prov_id in self.failover_order:
            provider = self.CATALOG.get(prov_id)
            if not provider or not provider.is_healthy:
                continue

            try:
                # Pre-budget check
                est_cost = provider.compute_cost(prompt_tokens, 150)
                if self.cumulative_cost_usd + est_cost > self.max_budget_usd:
                    raise BudgetExceededException(
                        f"Cumulative cost (${self.cumulative_cost_usd:.4f}) exceeds hard limit (${self.max_budget_usd:.2f})"
                    )

                # Simulated high-intelligence response synthesis (or provider API call)
                target_model = model_override or provider.default_model
                response_text = f"[{provider.provider_id.upper()}:{target_model}] Synthesized reasoning for: '{prompt[:60]}...'"
                completion_tokens = self.estimate_tokens(response_text)

                actual_cost = provider.compute_cost(prompt_tokens, completion_tokens)
                self.cumulative_prompt_tokens += prompt_tokens
                self.cumulative_completion_tokens += completion_tokens
                self.cumulative_cost_usd = round(self.cumulative_cost_usd + actual_cost, 6)

                rec = {
                    "provider": provider.provider_id,
                    "model": target_model,
                    "response": response_text,
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

            except BudgetExceededException:
                raise
            except Exception as ex:
                provider.consecutive_failures += 1
                if provider.consecutive_failures >= 3:
                    provider.is_healthy = False
                last_error = str(ex)

        raise RuntimeError(f"All LLM providers in cascade failed. Last error: {last_error}")
