"""Policy-only KOSIF model gateway candidate inspired by FlagshipRouter (MIT).
No network calls, third-party executors, credentials, or authorization bypasses.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import FrozenSet, Iterable, Literal, Optional, Tuple

Sensitivity = Literal["public", "internal", "confidential"]
Mode = Literal["fast", "standard", "deep", "full_pro"]
EXECUTOR_OWNERS = {
    "computer": "KOSIF Computer",
    "device_write": "KOSIF Computer",
    "whatsapp_send": "KOSIF WhatsApp",
    "voice_generate": "KOSIF Voice Director",
    "release": "KOSIF Release Bridge",
}
RETRYABLE_ERRORS = frozenset({"timeout", "network", "rate_limit", "overloaded", "upstream_5xx"})


@dataclass(frozen=True)
class ProviderModel:
    provider: str
    model: str
    capabilities: FrozenSet[str]
    status: Literal["ready", "unknown", "offline", "rate_limited"] = "unknown"
    authorized: bool = False
    quota_available: bool = False
    free_tier_verified: bool = False
    estimated_cost_usd: float = 0.0
    latency_ms: int = 1000
    quality: int = 50
    allows_confidential: bool = False
    is_local: bool = False


@dataclass(frozen=True)
class RouteRequest:
    mode: Mode
    capabilities: FrozenSet[str]
    sensitivity: Sensitivity = "public"
    free_only: bool = False
    max_estimated_cost_usd: Optional[float] = None
    permitted_providers: Optional[FrozenSet[str]] = None
    idempotent: bool = True


@dataclass(frozen=True)
class RouteDecision:
    status: Literal["selected", "blocked"]
    model_ids: Tuple[str, ...]
    reason: str
    canonical_owner: Optional[str] = None


def _eligible(p: ProviderModel, req: RouteRequest) -> bool:
    if p.status != "ready" or not p.authorized or not p.quota_available:
        return False
    if not req.capabilities.issubset(p.capabilities):
        return False
    if req.permitted_providers is not None and p.provider not in req.permitted_providers:
        return False
    if req.free_only and not p.free_tier_verified:
        return False
    if req.max_estimated_cost_usd is not None and p.estimated_cost_usd > req.max_estimated_cost_usd:
        return False
    if req.sensitivity == "confidential" and not (p.is_local and p.allows_confidential):
        return False
    if p.estimated_cost_usd < 0 or p.latency_ms < 0 or not 0 <= p.quality <= 100:
        return False
    return True


def choose_models(req: RouteRequest, catalog: Iterable[ProviderModel]) -> RouteDecision:
    """Rank policy-eligible candidates without executing them."""
    if req.mode == "full_pro":
        return RouteDecision("blocked", (), "FULL_PRO_CANONICAL_RUNTIME_REQUIRED", "KOSIF Think")
    for operation in sorted(req.capabilities):
        if operation in EXECUTOR_OWNERS:
            return RouteDecision("blocked", (), "CANONICAL_EXECUTOR_REQUIRED", EXECUTOR_OWNERS[operation])
    if req.max_estimated_cost_usd is not None and req.max_estimated_cost_usd < 0:
        return RouteDecision("blocked", (), "INVALID_BUDGET")

    candidates = [p for p in catalog if _eligible(p, req)]
    quality_weight = 4 if req.mode == "deep" else 2
    latency_weight = 3 if req.mode == "fast" else 1
    candidates.sort(key=lambda p: (
        -(p.quality * quality_weight - p.latency_ms / 100 * latency_weight),
        p.estimated_cost_usd, p.provider, p.model,
    ))
    ids = tuple(f"{p.provider}/{p.model}" for p in candidates)
    if ids:
        return RouteDecision("selected", ids, "POLICY_ELIGIBLE_CANDIDATES")
    return RouteDecision("blocked", (), "NO_VERIFIED_AUTHORIZED_COMPATIBLE_MODEL")


def safe_fallback(
    decision: RouteDecision, failed_model_id: str, error_code: str, *, idempotent: bool = True
) -> RouteDecision:
    """Retry only a transient failure on a replay-safe request."""
    if decision.status != "selected" or not idempotent or error_code not in RETRYABLE_ERRORS:
        return RouteDecision("blocked", (), "FALLBACK_NOT_PERMITTED")
    if not decision.model_ids or decision.model_ids[0] != failed_model_id:
        return RouteDecision("blocked", (), "FALLBACK_STATE_MISMATCH")
    remaining = decision.model_ids[1:]
    if not remaining:
        return RouteDecision("blocked", (), "FALLBACK_EXHAUSTED")
    return RouteDecision("selected", remaining, "FALLBACK_AFTER_RETRYABLE_FAILURE")
