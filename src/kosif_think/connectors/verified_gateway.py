"""Verified opt-in model execution adapter for the KOSIF Python runtime.

The caller MUST supply trusted, freshly checked provider metadata. This module
never reads credentials, never calls a missing client and never routes Full Pro.
"""
from __future__ import annotations

import math
import re
import time
from typing import Iterable, Optional

from kosif_think.connectors.models import ModelError
from kosif_think.model_gateway_router import (
    ProviderModel, RouteDecision, RouteRequest, choose_models, safe_fallback,
)


class GatewayBlocked(RuntimeError):
    """Fail-closed routing decision with a non-secret reason code."""

    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(reason)


def _failure_code(exc: ModelError) -> str:
    """Classify conservative retry-safe provider errors; do not log raw bodies."""
    status = getattr(exc, "status_code", None)
    if status is None:
        match = re.search(r"\\bHTTP (\\d{3})\\b", str(exc))
        status = int(match.group(1)) if match else None
    if status == 429:
        return "rate_limit"
    if isinstance(status, int) and 500 <= status <= 599:
        return "upstream_5xx"
    msg = str(exc).lower()
    if "could not reach" in msg or "connection error" in msg:
        return "network"
    if "timed out" in msg or "timeout" in msg:
        return "timeout"
    return "not_retryable"


def execute_verified(
    router,
    prompt: str,
    request: RouteRequest,
    trusted_catalog: Iterable[ProviderModel],
    *,
    system_instruction: Optional[str] = None,
    max_tokens: int = 1024,
    temperature: Optional[float] = None,
    request_id: str = "",
) -> dict:
    """Call only explicitly authorized, attached and matching ModelClients.

    Catalog assertions are authoritative ONLY when produced by trusted runtime
    provider probes, not user-submitted JSON. This is not an HTTP endpoint.
    """
    if not isinstance(max_tokens, int) or not 1 <= max_tokens <= 16384:
        raise GatewayBlocked("INVALID_MAX_TOKENS")
    if request_id and (len(request_id) > 128 or not re.fullmatch(r"[A-Za-z0-9_.:-]+", request_id)):
        raise GatewayBlocked("INVALID_REQUEST_ID")

    catalog = tuple(trusted_catalog)
    decision = choose_models(request, catalog)
    if decision.status != "selected":
        raise GatewayBlocked(decision.reason)

    trusted_lookup = {(p.provider, p.model): p for p in catalog}
    attached = []
    for identity in decision.model_ids:
        # The identity is assembled from trusted catalogue fields; exact match
        # against an attached client prevents provider/model substitution.
        provider_id, model = identity.split("/", 1)
        client = router.clients.get(provider_id)
        config = router.CATALOG.get(provider_id)
        if client is None or config is None or not config.is_healthy:
            continue
        if client.model != model or (provider_id, model) not in trusted_lookup:
            continue
        if identity not in attached:
            attached.append(identity)
    if not attached:
        raise GatewayBlocked("NO_VERIFIED_ATTACHED_CLIENT")

    state = RouteDecision("selected", tuple(attached), "VERIFIED_ATTACHED_CLIENTS")
    started = time.perf_counter()
    prompt_estimate = router.estimate_tokens(prompt) + router.estimate_tokens(system_instruction or "")
    while state.model_ids:
        identity = state.model_ids[0]
        provider_id, model = identity.split("/", 1)
        client = router.clients[provider_id]
        provider = router.CATALOG[provider_id]
        metadata = trusted_lookup[(provider_id, model)]

        if not provider.is_healthy:
            raise GatewayBlocked("PROVIDER_HEALTH_CHANGED")
        # Conservative reservation: twice heuristic prompt input + requested
        # maximum output, with trusted catalogue estimate as a lower bound.
        projected_cost = max(
            provider.compute_cost(2 * prompt_estimate, max_tokens),
            metadata.estimated_cost_usd,
        )
        if not math.isfinite(projected_cost) or projected_cost < 0:
            raise GatewayBlocked("INVALID_PRICE_ESTIMATE")
        if router.cumulative_cost_usd + projected_cost > router.max_budget_usd:
            raise GatewayBlocked("BUDGET_RESERVATION_EXCEEDED")

        try:
            completion = client.complete(
                prompt, system=system_instruction, max_tokens=max_tokens, temperature=temperature
            )
        except ModelError as exc:
            provider.consecutive_failures += 1
            if provider.consecutive_failures >= 3:
                provider.is_healthy = False
            reason = _failure_code(exc)
            replacement = safe_fallback(
                state, identity, reason, idempotent=request.idempotent,
            )
            if replacement.status != "selected":
                raise GatewayBlocked(replacement.reason) from None
            state = replacement
            continue

        # The client has already executed; never silently assign a different
        # provider/model or accept a second model's result as the first.
        if completion.model != model:
            raise GatewayBlocked("MODEL_IDENTITY_DRIFT")
        if completion.provider not in (provider_id, client.provider):
            raise GatewayBlocked("PROVIDER_IDENTITY_DRIFT")

        provider.consecutive_failures = 0
        prompt_tokens = completion.input_tokens or prompt_estimate
        output_tokens = completion.output_tokens or router.estimate_tokens(completion.text)
        cost = provider.compute_cost(prompt_tokens, output_tokens)
        if not math.isfinite(cost) or cost < 0:
            raise GatewayBlocked("INVALID_ACTUAL_COST")
        router.cumulative_prompt_tokens += prompt_tokens
        router.cumulative_completion_tokens += output_tokens
        router.cumulative_cost_usd = round(router.cumulative_cost_usd + cost, 6)
        # Keep request_history free of prompts, responses, keys and raw errors.
        public_receipt = {
            "status": "executed",
            "request_id": request_id,
            "provider": provider_id,
            "model": model,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": output_tokens,
            "cost_usd": cost,
            "simulated": False,
            "fallback_used": identity != attached[0],
            "duration_ms": round((time.perf_counter() - started) * 1000, 2),
        }
        router.request_history.append(dict(public_receipt))
        if router.cumulative_cost_usd > router.max_budget_usd:
            raise GatewayBlocked("ACTUAL_BUDGET_OVERRUN")
        return {
            **public_receipt,
            "response": completion.text,
            "stop_reason": completion.stop_reason,
            "cumulative_cost_usd": router.cumulative_cost_usd,
            "budget_remaining_usd": round(router.max_budget_usd - router.cumulative_cost_usd, 6),
        }
    raise GatewayBlocked("FALLBACK_EXHAUSTED")
