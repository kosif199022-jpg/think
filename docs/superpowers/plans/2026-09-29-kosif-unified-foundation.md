# KOSIF Unified Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish one canonical, versioned KOSIF manifest in GitHub and make runtime/ChatGPT/Computer consumers detect and report version drift before deeper capability consolidation.

**Architecture:** Build a declarative manifest loader as the single source for release identity, lanes, capabilities, cognitive perspectives, safety gates, and consumer metadata. Existing planner/router/executor lanes remain intact; API/MCP/Computer adapters consume the manifest instead of duplicating version/capability literals. Runtime state remains outside Git.

**Tech Stack:** Python 3.10+, stdlib JSON/hashlib/dataclasses, existing KOSIF Think HTTP/MCP servers, pytest/unittest-compatible existing tests.

**Spec:** `docs/KOSIF_UNIFIED_SYSTEM_SPEC.md`

## Global Constraints

- GitHub is authoritative only for declarative definitions, not live runtime state, memory, credentials, telemetry, or routing scores.
- Every consumer exposes `release_id + git_sha + manifest_hash + schema_version`.
- A consumer with mismatched identity reports `OUT_OF_SYNC` rather than pretending to be current.
- KOSIF Think owns the capability catalog; KOSIF Computer remains the execution authority for device/browser side effects.
- Jev remains bounded and never grants permissions or bypasses human gates.
- Existing working lanes/backends stay operational during migration.

## Review Focus

- Missing or malformed manifest: startup/status must fail clearly or enter safe degraded mode; no silent defaults that invent capabilities.
- Version conflict inside the repo: API, package metadata, and manifest must resolve to one release identity instead of independent literals.
- Partial consumer metadata: missing `git_sha`/`manifest_hash` must produce `OUT_OF_SYNC` or `UNKNOWN`, never `IN_SYNC`.
- Capability duplication: Computer capabilities must be represented as contracts/adapters, not copied implementation code.
- Runtime secrets/state: manifest serialization and status responses must never expose tokens, credentials, private chain-of-thought, or live memory payloads.

---

### Task 1: Canonical Manifest Schema and Loader

**Files:**
- Create: `config/kosif_manifest.json`
- Create: `src/kosif_think/core/manifest.py`
- Create: `tests/test_manifest.py`
- Modify: `src/kosif_think/core/__init__.py`

**Interfaces:**
- Produces: `ManifestIdentity`, `CapabilityManifest`, `load_manifest(path: str | None = None) -> CapabilityManifest`, `compute_manifest_hash(data: dict) -> str`.
- Consumers later read `manifest.identity`, `manifest.lanes`, `manifest.capabilities`, `manifest.perspectives`, `manifest.human_gates`.

- [ ] **Step 1: Write failing tests** for deterministic manifest hashing, required identity fields, malformed JSON rejection, and absence of runtime-secret fields.
- [ ] **Step 2: Run** `python -m pytest tests/test_manifest.py -v`; expected: FAIL because manifest module does not exist.
- [ ] **Step 3: Implement** dataclasses/validation in `src/kosif_think/core/manifest.py` and seed `config/kosif_manifest.json` from the approved spec, including the 12 current lanes and Computer capability contracts.
- [ ] **Step 4: Run** `python -m pytest tests/test_manifest.py -v`; expected: PASS.
- [ ] **Step 5: Commit** `feat: add canonical KOSIF capability manifest`.

### Task 2: Single Release Identity and Drift Detection

**Files:**
- Create: `src/kosif_think/core/versioning.py`
- Create: `tests/test_versioning.py`
- Modify: `src/kosif_think/__init__.py`
- Modify: `src/kosif_think/server/api.py`
- Modify: `pyproject.toml`

**Interfaces:**
- Consumes: `CapabilityManifest` from Task 1.
- Produces: `ReleaseIdentity`, `get_release_identity() -> ReleaseIdentity`, `compare_consumer_identity(canonical, consumer) -> str` returning `IN_SYNC`, `OUT_OF_SYNC`, or `UNKNOWN`.

- [ ] **Step 1: Write failing tests** proving the current `pyproject.toml`/API version drift is eliminated and identity comparison handles missing/mismatched hashes.
- [ ] **Step 2: Run** `python -m pytest tests/test_versioning.py -v`; expected: FAIL.
- [ ] **Step 3: Implement** one version source derived from the manifest; remove hard-coded `1.2.0` and partial lane list from `/health`.
- [ ] **Step 4: Add** `/api/version` and include release identity plus sync state in `/health` without secrets.
- [ ] **Step 5: Run** `python -m pytest tests/test_versioning.py tests/test_core_loop.py -v`; expected: PASS.
- [ ] **Step 6: Commit** `feat: unify KOSIF release identity and drift detection`.

### Task 3: Capability Catalog and KOSIF Computer Contract

**Files:**
- Create: `src/kosif_think/core/capabilities.py`
- Create: `src/kosif_think/connectors/computer_adapter.py`
- Create: `tests/test_capabilities.py`
- Modify: `src/kosif_think/core/router.py`
- Modify: `src/kosif_think/core/planner.py`

**Interfaces:**
- Consumes: manifest capabilities and existing lane handlers.
- Produces: `CapabilityDescriptor`, `CapabilityCatalog`, `ComputerCapabilityAdapter.describe()`, `ComputerCapabilityAdapter.execute(request)`.
- The adapter exposes Playwright/CDP, DevTools, UIA, app/dialog/screen-state, workflows/watchers, native input fallback, files, and configured device adapters as contracts while keeping implementation single-sourced in KOSIF Computer.

- [ ] **Step 1: Write failing tests** for catalog lookup, duplicate capability IDs, unavailable executor behavior, and planner routing to Computer capabilities without duplicating code.
- [ ] **Step 2: Run** `python -m pytest tests/test_capabilities.py -v`; expected: FAIL.
- [ ] **Step 3: Implement** catalog and adapter contracts; preserve current `computer` lane fallback during migration.
- [ ] **Step 4: Update** planner/router to resolve capabilities through the catalog first, then existing lane behavior for compatibility.
- [ ] **Step 5: Run** `python -m pytest tests/test_capabilities.py tests/test_planner.py tests/test_core_loop.py -v`; expected: PASS.
- [ ] **Step 6: Commit** `feat: expose KOSIF Computer capabilities through Think catalog`.

### Task 4: Consumer Status for Cloud, ChatGPT, Computer, and Local Surfaces

**Files:**
- Create: `src/kosif_think/core/sync_state.py`
- Create: `tests/test_sync_state.py`
- Modify: `src/kosif_think/server/api.py`
- Modify: `src/kosif_think/server/mcp.py`

**Interfaces:**
- Consumes: canonical `ReleaseIdentity` and consumer-reported identity tuples.
- Produces: `ConsumerSyncState`, `build_sync_report(consumers) -> dict` and `/api/sync/status`.

- [ ] **Step 1: Write failing tests** for exact match, stale ChatGPT plugin, stale Cloud runtime, missing Computer identity, and secret redaction.
- [ ] **Step 2: Run** `python -m pytest tests/test_sync_state.py -v`; expected: FAIL.
- [ ] **Step 3: Implement** sync report generation and expose it through HTTP/MCP status surfaces.
- [ ] **Step 4: Ensure** static ChatGPT schemas remain versioned artifacts while dynamic capability metadata comes from the runtime manifest endpoint.
- [ ] **Step 5: Run** `python -m pytest tests/test_sync_state.py tests/test_openai_bridge.py -v`; expected: PASS.
- [ ] **Step 6: Commit** `feat: add cross-surface KOSIF sync status`.

### Task 5: Foundation Regression Gate

**Files:**
- Create: `tests/test_unified_foundation.py`
- Modify: `README.md`
- Modify: `docs/ARCHITECTURE.md`

**Interfaces:**
- Consumes all Tasks 1-4.
- Produces a single regression proof that one manifest drives identity, capability discovery, and consumer sync state.

- [ ] **Step 1: Add integration tests** asserting: 12 registered lanes agree with manifest; `/health` version equals package/manifest version; Computer capability contracts are discoverable; stale consumer identity returns `OUT_OF_SYNC`; no runtime secret fields appear.
- [ ] **Step 2: Run focused suite** `python -m pytest tests/test_manifest.py tests/test_versioning.py tests/test_capabilities.py tests/test_sync_state.py tests/test_unified_foundation.py -v`; expected: PASS.
- [ ] **Step 3: Run full suite** `python -m pytest tests -v`; expected: existing tests plus new tests PASS with no lane regressions.
- [ ] **Step 4: Update docs** to point every consumer to `config/kosif_manifest.json` and document the migration compatibility path.
- [ ] **Step 5: Commit** `test: gate unified KOSIF foundation with regression suite`.

## Follow-on Plans

After this foundation is verified, create separate implementation plans for:
1. Cognitive Perspectives + Dynamic Council + Evidence Auditor.
2. Meta-Evaluator + task-specific Agent Reputation.
3. Evolution Agent + benchmark/canary/self-improvement PR pipeline.
4. Generated Cloudflare/ChatGPT consumer artifacts and deployment automation.

This separation is intentional: each subsystem can be rejected or rolled back without destabilizing the canonical manifest and Computer execution path.