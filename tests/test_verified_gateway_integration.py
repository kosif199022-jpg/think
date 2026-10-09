"""Integration contract for the explicit model-routing path; no live API keys."""
import pytest

from kosif_think.connectors.llm_router import LLMRouter
from kosif_think.connectors.models import Completion, ModelClient, ModelError, ScriptedClient
from kosif_think.connectors.verified_gateway import GatewayBlocked
from kosif_think.model_gateway_router import ProviderModel, RouteRequest


class FakeClient(ModelClient):
    def __init__(self, provider, model="m", error=None, text="verified text", reply_model=None):
        super().__init__(model)
        self.provider = provider
        self.error = error
        self.text = text
        self.reply_model = reply_model
        self.calls = 0

    def _complete(self, prompt, system, max_tokens, temperature):
        self.calls += 1
        if self.error:
            raise ModelError(self.error)
        return Completion(
            text=self.text, provider=self.provider, model=self.reply_model or self.model,
            input_tokens=10, output_tokens=8, stop_reason="stop",
        )


def eligible(name="good", model="m", **overrides):
    base = dict(provider=name, model=model, capabilities=frozenset({"text"}),
                authorized=True, quota_available=True, status="ready", quality=90)
    base.update(overrides)
    return ProviderModel(**base)


def req(**overrides):
    base = dict(mode="standard", capabilities=frozenset({"text"}))
    base.update(overrides)
    return RouteRequest(**base)


def test_real_verified_execution_and_redacted_history():
    router = LLMRouter(clients={"good": FakeClient("good")})
    result = router.dispatch_completion("very private question", policy_request=req(),
                                        trusted_catalog=[eligible()], request_id="r.1")
    assert result["response"] == "verified text"
    assert result["status"] == "executed"
    assert result["simulated"] is False
    assert result["provider"] == "good"
    assert result["request_id"] == "r.1"
    history = router.request_history[0]
    assert "response" not in history and "prompt" not in history
    assert "private" not in str(history)


def test_declared_catalog_is_mandatory_for_opt_in():
    router = LLMRouter()
    with pytest.raises(GatewayBlocked, match="TRUSTED_CATALOG_REQUIRED"):
        router.dispatch_completion("hello", policy_request=req())


def test_no_simulated_completion_when_adapter_is_missing():
    router = LLMRouter()
    with pytest.raises(GatewayBlocked, match="NO_VERIFIED_ATTACHED_CLIENT"):
        router.dispatch_completion("hello", policy_request=req(), trusted_catalog=[eligible()])
    assert router.request_history == []


def test_full_pro_is_always_canonical_even_with_attached_client():
    client = FakeClient("good")
    router = LLMRouter(clients={"good": client})
    with pytest.raises(GatewayBlocked, match="FULL_PRO_CANONICAL_RUNTIME_REQUIRED"):
        router.dispatch_completion("hello", policy_request=req(mode="full_pro"),
                                   trusted_catalog=[eligible()])
    assert client.calls == 0


def test_canonical_device_actions_cannot_be_executed_by_model():
    client = FakeClient("good")
    router = LLMRouter(clients={"good": client})
    with pytest.raises(GatewayBlocked, match="CANONICAL_EXECUTOR_REQUIRED"):
        router.dispatch_completion("open desktop",
                policy_request=req(capabilities=frozenset({"computer"})),
                trusted_catalog=[eligible(capabilities=frozenset({"text", "computer"}))])
    assert client.calls == 0


def test_exact_model_binding_rejects_model_substitution():
    client = FakeClient("good", model="m")
    router = LLMRouter(clients={"good": client})
    with pytest.raises(GatewayBlocked, match="NO_VERIFIED_ATTACHED_CLIENT"):
        router.dispatch_completion("hello", policy_request=req(),
                                   trusted_catalog=[eligible(model="another")])
    assert client.calls == 0


def test_429_fallback_success_only_on_idempotent_tasks():
    a = FakeClient("first", error="HTTP 429 from upstream")
    b = FakeClient("second", text="backup")
    router = LLMRouter(clients={"first": a, "second": b})
    ans = router.dispatch_completion("hello", policy_request=req(),
        trusted_catalog=[eligible("first", quality=99), eligible("second", quality=70)])
    assert ans["response"] == "backup" and ans["fallback_used"]
    assert (a.calls, b.calls) == (1, 1)


def test_no_fallback_on_auth_failure():
    a = FakeClient("first", error="HTTP 401 unauthorized")
    b = FakeClient("second", text="backup")
    router = LLMRouter(clients={"first": a, "second": b})
    with pytest.raises(GatewayBlocked, match="FALLBACK_NOT_PERMITTED"):
        router.dispatch_completion("hello", policy_request=req(),
            trusted_catalog=[eligible("first", quality=99), eligible("second", quality=70)])
    assert (a.calls, b.calls) == (1, 0)


def test_nonidempotent_failure_does_not_replay():
    a = FakeClient("first", error="HTTP 503 unavailable")
    b = FakeClient("second", text="backup")
    router = LLMRouter(clients={"first": a, "second": b})
    with pytest.raises(GatewayBlocked, match="FALLBACK_NOT_PERMITTED"):
        router.dispatch_completion("hello", policy_request=req(idempotent=False),
            trusted_catalog=[eligible("first", quality=99), eligible("second", quality=70)])
    assert (a.calls, b.calls) == (1, 0)


def test_budget_reservation_blocks_before_execution():
    client = FakeClient("good")
    router = LLMRouter(max_budget_usd=0.01, clients={"good": client})
    with pytest.raises(GatewayBlocked, match="BUDGET_RESERVATION_EXCEEDED"):
        router.dispatch_completion("hello", policy_request=req(),
            trusted_catalog=[eligible(estimated_cost_usd=0.02)])
    assert client.calls == 0


def test_catalog_unknown_or_offline_fails_closed():
    client = FakeClient("good")
    router = LLMRouter(clients={"good": client})
    with pytest.raises(GatewayBlocked, match="NO_VERIFIED_AUTHORIZED_COMPATIBLE_MODEL"):
        router.dispatch_completion("hello", policy_request=req(),
            trusted_catalog=[eligible(status="unknown")])
    assert client.calls == 0


def test_response_model_drift_fails_closed():
    client = FakeClient("good", reply_model="not-authorized")
    router = LLMRouter(clients={"good": client})
    with pytest.raises(GatewayBlocked, match="MODEL_IDENTITY_DRIFT"):
        router.dispatch_completion("hello", policy_request=req(), trusted_catalog=[eligible()])


def test_legacy_dispatch_remains_compatible_for_old_callers():
    legacy = LLMRouter()
    result = legacy.dispatch_completion("old caller")
    assert result["simulated"] is True
    assert result["response"].startswith("[SIMULATED")


def test_invalid_request_id_blocked():
    router = LLMRouter(clients={"good": FakeClient("good")})
    with pytest.raises(GatewayBlocked, match="INVALID_REQUEST_ID"):
        router.dispatch_completion("x", policy_request=req(), trusted_catalog=[eligible()],
                                   request_id="secret\nAuthorization: token")


def test_successful_scripted_client_as_dedicated_provider():
    client = ScriptedClient(["ok"])
    router = LLMRouter(clients={"scripted": client})
    result = router.dispatch_completion("hello", policy_request=req(),
        trusted_catalog=[eligible(name="scripted", model="scripted")])
    assert result["response"] == "ok"


def test_duplicate_catalog_claims_are_rejected_before_execution():
    client = FakeClient("good")
    router = LLMRouter(clients={"good": client})
    with pytest.raises(GatewayBlocked, match="DUPLICATE_PROVIDER_MODEL"):
        router.dispatch_completion("hello", policy_request=req(),
            trusted_catalog=[eligible(), eligible(authorized=False)])
    assert client.calls == 0


def test_request_cost_limit_enforced_against_reserved_cost():
    client = FakeClient("good")
    router = LLMRouter(max_budget_usd=10, clients={"good": client})
    with pytest.raises(GatewayBlocked, match="REQUEST_ESTIMATED_COST_EXCEEDED"):
        router.dispatch_completion("hello",
            policy_request=req(max_estimated_cost_usd=0.001),
            trusted_catalog=[eligible(estimated_cost_usd=0.002)])
    assert client.calls == 0
