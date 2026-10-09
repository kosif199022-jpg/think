# FlagshipRouter concepts → KOSIF Think model gateway (candidate)

Source inspiration: https://github.com/theRizwan/FlagshipRouter (MIT), especially README and docs/ARCHITECTURE.md. We distilled routing ideas and did **not** copy proxy implementation or third-party provider executors.

## Architecture and ownership

- KOSIF SEE remains the front door: Registry → Stage-0 → appropriate owner.
- KOSIF Think is the canonical reasoning/model backend.
- KOSIF Computer, WhatsApp, Voice Director and Release Bridge retain their separate side-effect rights.
- Explicit Full Pro always requires the canonical runtime and request-bound receipts. This prototype must **not** silently replace Full Pro with an ordinary model combo.

## Included candidate

- src/kosif_think/model_gateway_router.py: deterministic model ranking and explicit safe-fallback decisions; no network or credentials.
- tests/test_model_gateway_router.py: covers health, auth, quota, free-tier verification, privacy, provider consent, capability checks, Full Pro, canonical side effects and idempotent-only retry.
- Python LLMRouter is now wired via explicit opt-in `dispatch_completion(policy_request=..., trusted_catalog=..., request_id=...)`. The legacy call path is unchanged; verified dispatch fails closed rather than simulating success. **Cloudflare KOSIF Think/ChatGPT production is a different runtime and has NOT been updated.**

## Minimum integration contract

1. Read fresh sanitized provider catalogue: provider/model, verified health, quota availability, auth state, capabilities, measured latency, estimated cost and privacy classification.
2. For ordinary model calls only: evaluate choose_models and select the first **actually** verified compatible entry.
3. Execute via an authorized KOSIF Think provider adapter; preserve response/tool-call schemas and streaming boundaries; never run third-party code from the model catalogue.
4. Pass transient retryable failures to safe_fallback. Do not replay non-idempotent or ambiguous operations. Record and verify an execution receipt first.
5. Log request ID, model ID, state age, rate-limit/error reason, tokens/cost and fallback path. Redact prompts, auth headers, secrets and sensitive inputs.
6. Verify provider ToS, rate limits, key ownership, billing and residency/privacy policies. A 'free tier' must not be treated as unlimited free use.

## Risks observed in source

- FlagshipRouter documents a default dashboard password of 123456: never reuse this in KOSIF; provision strong runtime secrets and restrict binding to localhost during initial setup.
- FlagshipRouter architecture describes persisted provider tokens and optional full-body debug logging. KOSIF should use managed secrets and redacted telemetry, not those shortcuts.
- In its README, upstream reports some known test failures. Validate against a baseline rather than claiming upstream's full test suite is green.

## Release gates

- Revalidate fresh Plugin Creator release/version, local Registry/Reference/Fabric/Eval version equality and nine method-pack paths.
- Add contract and integration tests for provider handoff, tool-call translation, streaming, OAuth/key refresh, privacy, concurrency, SSRF allowlists, breaker cooldown, observability and exact cost accounting.
- Shadow-route representative tasks and compare against the existing selector before enabling traffic.
- Verify stable, request-bound Full Pro/side-effect receipts. Never classify an index entry or a provider status check as execution proof.
- Maintain immutable repair-log chain and guarded publication/read-back.


## Python integration contract (opt-in, not Cloudflare deployment)

The Python caller obtains fresh provider health, auth, quota, capabilities, price and privacy claims **server-side** from trusted KOSIF services; it MUST NOT trust a raw user-submitted catalogue. Attach matching authorized ModelClient instances to LLMRouter. Call:

```python
from kosif_think.connectors.llm_router import LLMRouter
from kosif_think.connectors.models import ScriptedClient
from kosif_think.model_gateway_router import ProviderModel, RouteRequest

router = LLMRouter(clients={"scripted": ScriptedClient(["test reply"])})
request = RouteRequest(mode="standard", capabilities=frozenset({"text"}))
verified_catalog = [
    ProviderModel(provider="scripted", model="scripted",
                  capabilities=frozenset({"text"}), status="ready",
                  authorized=True, quota_available=True)
]
receipt = router.dispatch_completion("hello", policy_request=request,
                                     trusted_catalog=verified_catalog,
                                     request_id="example.1")
assert receipt["status"] == "executed" and not receipt["simulated"]
```

`ScriptedClient` is a **test double**, not a real AI provider. For actual calls attach a configured real ModelClient, and derive its readiness from fresh independent provider checks. The public HTTP /v1/chat/completions API is **not** switched to this route, because it exposes broader execution paths and requires separate review of auth, approval gates and multi-tenant policy.

The guarded path rejects no client, unknown authorization, quota or health, Full Pro, canonical side-effect owner misuse and unsupported model/capability matches. Transient fallbacks require idempotent requests and only use already verified candidates. A returned receipt proves a model adapter executed, NOT factual accuracy, external QA or Full Pro.

Provider rates in the legacy Python CATALOG are estimates and need active verification before paid traffic. The preflight reservation is conservative, but actual provider billing can exceed predicted cost; overruns are recorded and fail closed without claiming a hard real-time billing guarantee. Don't enable paid traffic without an upstream hard budget guard, key authorization and cost consent.

### Remaining production activation gates

1. Find the actual canonical Cloudflare worker source and inspect current release, security and provider adapters.
2. Add analogous policy routing to that JS/Worker runtime, behind an off-by-default feature flag.
3. Obtain fresh provider config and authorize only trusted services, not user-supplied status.
4. Test request-bound Full Pro receipts, selected model identity, provider-failure fallback, billing, and rollback.
5. Canary rollout, smoke tests, and read-back before enabling wider live traffic.

This Python integration is complete as an opt-in library feature only, not proof of production Cloudflare activation.
