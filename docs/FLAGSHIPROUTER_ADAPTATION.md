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
- This feature is NOT wired to production, because live runtime/provider configuration, owner authorization and receipts must be integrated and verified first.

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
