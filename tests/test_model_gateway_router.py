from kosif_think.model_gateway_router import (
    ProviderModel, RouteRequest, choose_models, safe_fallback
)


def provider(name, **kw):
    return ProviderModel(
        provider=name, model="test", capabilities=frozenset({"text"}),
        status="ready", authorized=True, quota_available=True, **kw
    )


def request(**kw):
    return RouteRequest(mode="standard", capabilities=frozenset({"text"}), **kw)


def test_model_catalog_ranks_quality_and_has_deterministic_ties():
    ranked = choose_models(request(), [provider("z", quality=70), provider("a", quality=85)])
    assert ranked.status == "selected"
    assert ranked.model_ids == ("a/test", "z/test")


def test_disallow_unverified_auth_and_quota():
    models = [
        ProviderModel("x", "test", frozenset({"text"}), status="ready"),
        provider("y", free_tier_verified=True),
    ]
    assert choose_models(request(), models).model_ids == ("y/test",)


def test_free_only_requires_verified_free_tier():
    r = choose_models(request(free_only=True), [
        provider("paid"), provider("free", free_tier_verified=True)
    ])
    assert r.model_ids == ("free/test",)


def test_confidential_requires_explicit_trusted_local():
    r = choose_models(request(sensitivity="confidential"), [
        provider("cloud", allows_confidential=True),
        provider("local", is_local=True, allows_confidential=True),
    ])
    assert r.model_ids == ("local/test",)


def test_requires_matching_capabilities_and_optional_allowlist():
    r = choose_models(request(permitted_providers=frozenset({"a"})), [
        provider("a", quality=20), provider("b", quality=100)
    ])
    assert r.model_ids == ("a/test",)
    assert choose_models(
        RouteRequest(mode="fast", capabilities=frozenset({"vision"})), [provider("a")]
    ).status == "blocked"


def test_full_pro_never_downgrades_to_regular_model():
    r = choose_models(
        RouteRequest(mode="full_pro", capabilities=frozenset({"text"})), [provider("a")]
    )
    assert r.status == "blocked" and r.reason == "FULL_PRO_CANONICAL_RUNTIME_REQUIRED"


def test_tools_never_become_side_effect_executors():
    for op, owner in [
        ("whatsapp_send", "KOSIF WhatsApp"),
        ("computer", "KOSIF Computer"),
        ("voice_generate", "KOSIF Voice Director"),
        ("release", "KOSIF Release Bridge"),
    ]:
        r = choose_models(
            RouteRequest(mode="standard", capabilities=frozenset({op})), [provider("a")]
        )
        assert r.status == "blocked" and r.canonical_owner == owner


def test_fallback_only_for_transient_errors_on_idempotent_request():
    decision = choose_models(request(), [
        provider("a", quality=90), provider("b", quality=70)
    ])
    assert safe_fallback(decision, "a/test", "rate_limit").model_ids == ("b/test",)
    assert safe_fallback(decision, "a/test", "auth").status == "blocked"
    assert safe_fallback(decision, "a/test", "timeout", idempotent=False).status == "blocked"
    assert safe_fallback(decision, "b/test", "timeout").reason == "FALLBACK_STATE_MISMATCH"
    second = safe_fallback(decision, "a/test", "timeout")
    assert safe_fallback(second, "b/test", "timeout").reason == "FALLBACK_EXHAUSTED"


def test_budget_and_unknown_model_fail_closed():
    assert choose_models(
        request(max_estimated_cost_usd=-1), [provider("x")]
    ).reason == "INVALID_BUDGET"
    assert choose_models(
        request(), []
    ).reason == "NO_VERIFIED_AUTHORIZED_COMPATIBLE_MODEL"


def test_latency_preferred_on_fast_mode():
    req = RouteRequest(mode="fast", capabilities=frozenset({"text"}))
    decision = choose_models(req, [
        provider("slow", quality=81, latency_ms=3000),
        provider("fast", quality=80, latency_ms=50),
    ])
    assert decision.model_ids[0] == "fast/test"
