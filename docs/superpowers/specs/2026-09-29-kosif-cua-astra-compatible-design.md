# KOSIF CUA / Astra-Compatible Computer Use Design

## Status
Approved architecture design for implementation planning. This document defines how KOSIF Think acquires Astra-class computer/browser execution capabilities without copying unlicensed OpenAI-internal binaries or source.

## Goal
Make KOSIF Think the cognitive owner of a unified Computer Use capability surface while KOSIF Computer remains the controlled execution authority.

Success means KOSIF Think can plan, route, execute, observe, verify, recover, and audit desktop/browser actions through interchangeable adapters with no dependence on one proprietary runtime.

## Non-Goals
- Do not copy or redistribute `@oai/sky`, `@oai/cua-repl`, Codex Computer Use binaries, or other OpenAI-internal components unless an explicit redistribution license is later verified.
- Do not bypass permissions, MFA/OTP, CAPTCHA, payments, credential prompts, or OS security boundaries.
- Do not expose secrets or private chain-of-thought in traces.
- Do not make transport success equivalent to task completion.

## Licensing / Provenance Rule
Every adapter or embedded dependency MUST carry a recorded provenance entry: project, source URL, version/commit, license, and allowed mode of use.

Permitted integration modes:
1. `vendored_or_dependency` — only when license explicitly allows it.
2. `runtime_bridge` — invoke an installed runtime without copying it.
3. `behavioral_compatibility` — independently implement a compatible public interface from observed behavior and permitted documentation.
4. `disabled` — when provenance or permission is uncertain.

## Architecture
`User -> KOSIF Think -> Planner -> Risk Gate -> KOSIF CUA Broker -> Adapter -> Observe -> Verify -> Recover -> Audit -> Final Result`

KOSIF Think owns intent, planning, model/agent selection, risk decisions, retry policy, and completion criteria.

KOSIF CUA Broker owns capability discovery, adapter selection, normalized actions, normalized observations, adapter health, and failover.

KOSIF Computer adapters own authorized side effects on desktop/browser surfaces.

## Adapter Stack
Priority is policy-driven rather than hard-coded.

### 1. Open / licensed CUA adapter
Preferred production path where a verified open-source implementation provides required capabilities. Initial candidates include OpenSky-compatible and CUA-driver-compatible implementations after provenance verification.

### 2. Installed Codex runtime bridge
Optional compatibility adapter that may call a locally installed Computer Use runtime only through a stable, permitted interface. It MUST NOT copy bundled OpenAI files into KOSIF or GitHub.

### 3. KOSIF native Windows adapter
Independent implementation using Windows UI Automation/accessibility, screenshots, native input, clipboard, process/window APIs, and existing KOSIF Computer functions.

### 4. Browser adapter
Independent browser execution via Playwright/CDP and, where appropriate, a KOSIF-owned Chrome extension/native messaging bridge.

### 5. Legacy fallback
Existing PowerShell/SendKeys/screenshot behavior remains available only as a bounded fallback until parity tests allow retirement.

## Normalized Capability Contract
The broker exposes stable semantic actions independent of adapter implementation.

### Observation
- `get_state()` — current apps/windows/tabs, focused surface, capability health.
- `list_apps()` / `list_windows()` — top-level application/window inventory.
- `get_window_state(window_ref)` — accessibility tree, bounds, enabled/visible state, focused element, title/process metadata.
- `screenshot(surface_ref=None)` — screenshot plus stable observation identifier.
- `get_browser()` / `get_tab()` / `create_tab()` — browser/session/tab inventory and acquisition.

### Actions
- `launch_app`, `activate_window`, `close_app`
- `click`, `double_click`, `move`, `drag`, `scroll`
- `type_text`, `press_key`, `key_down`, `key_up`
- `set_value` for semantically addressable editable elements
- `clipboard_read`, `clipboard_write`, `paste`
- browser semantic actions for navigation, DOM targeting, form input, download/upload, and tab lifecycle

Targets SHOULD prefer stable semantic locators in this order:
1. accessibility element id / role-name relation
2. DOM selector / accessible name / href / placeholder
3. visual grounded region tied to a screenshot observation id
4. coordinates only as last-resort fallback

Every action returns normalized evidence: adapter, action id, target, before observation id, after observation id, changed flag, latency, and error/recovery metadata.

## Routing and Health
The broker probes adapters at startup and periodically records supported capabilities, latency, recent failures, and circuit-breaker state.

Routing rules:
- choose the healthiest adapter that satisfies the exact requested capability and current surface;
- prefer semantic/actionable state over pure coordinate control;
- prefer browser-native execution for browser tasks and desktop-native execution for non-browser tasks;
- fail over only when the next adapter can preserve the same safety and verification contract;
- never retry an irreversible action blindly.

## Verification Contract
Every side effect MUST be followed by observable verification when a postcondition is available.

Verification primitives include:
- `all`, `any`, and `not` predicates;
- window/app existence or focus state;
- accessibility element state/value;
- URL/title/DOM assertions;
- screen-region change where semantic state is unavailable;
- file/process existence and metadata checks.

If no meaningful change is observed, the recovery engine may re-observe, re-ground, switch adapter, or stop with a bounded failure. It MUST NOT loop indefinitely.

## Safety and Human Checkpoints
Existing KOSIF Risk Gate remains authoritative above every adapter.
Mandatory human checkpoints continue for CAPTCHA/anti-bot challenges, OTP/MFA, credentials/security changes, payments, and similarly sensitive confirmations.
Destructive writes, publishing, external communications, permission changes, and broad system mutations receive explicit risk classification and audit events.

## Integration with Existing KOSIF Code
The design extends rather than replaces the current architecture.

Expected implementation boundaries:
- `src/kosif_think/lanes/computer/` — broker, capability protocol, desktop adapters, state normalization.
- `src/kosif_think/lanes/browser/` — browser adapter integration and browser state/action normalization.
- `src/kosif_think/core/router.py` — capability-aware adapter selection and health signals, without moving execution authority out of the lane.
- `src/kosif_think/core/verifier.py` — richer observable predicates.
- `src/kosif_think/core/recovery.py` — bounded adapter-aware recovery.
- `src/kosif_think/server/mcp.py` — expose stable CUA tools only after internal contracts are tested.
- `tests/` — contract, adapter, risk, verification, failover, and regression coverage.

The current `ComputerLane` remains the public internal lane boundary during migration. Its dispatch method will delegate normalized computer-use intents to the broker while preserving existing intents for compatibility.

## Test Strategy
Implementation follows red-green-refactor TDD.

Required test classes:
1. capability contract tests using a deterministic fake adapter;
2. adapter selection and health/failover tests;
3. semantic target preference tests;
4. postcondition verification and no-change recovery tests;
5. risk-gate tests proving sensitive actions cannot bypass checkpoints;
6. Windows smoke tests against harmless apps such as Notepad/Calculator;
7. browser smoke tests against a controlled local/static page;
8. regression suite for all existing KOSIF Think tests.

No live payment, credential, MFA, destructive filesystem, or external-send workflow is used as an automated smoke test.

## Migration Phases
### Phase 1 — Contract and broker
Add normalized types/protocols, fake adapter, health registry, selection policy, and contract tests. Existing production behavior remains default.

### Phase 2 — Native Windows parity
Implement accessibility/window state plus native input/screenshot/clipboard behind the broker. Verify harmless desktop workflows and preserve legacy fallback.

### Phase 3 — Browser parity
Route browser actions through Playwright/CDP and semantic DOM/accessibility targets with tab/session inventory and deterministic verification.

### Phase 4 — Licensed/open CUA intake
Integrate only components whose provenance and license permit the selected mode. Pin versions/commits and preserve attribution/license notices required by their licenses.

### Phase 5 — Installed runtime bridge
If a stable permitted local interface to the installed Codex Computer Use runtime is verified, add it as an optional adapter. Treat absence or version drift as a normal degraded state, never as a fatal dependency.

### Phase 6 — Capability expansion
After parity, add richer multi-window coordination, adaptive settling, learned recovery policies, task-specific adapter reputation, and selected Jev escalation for bounded ambiguity.

## Success Criteria
- KOSIF Think can discover and route desktop/browser capabilities through a single broker.
- The same high-level action works through multiple adapters without changing planner code.
- Accessibility/DOM semantic targeting is preferred over coordinates.
- Every supported side effect has observable verification or reports that verification is unavailable.
- Adapter failure can trigger bounded failover without duplicate irreversible actions.
- Existing Risk Gate and audit logging remain in force.
- No unlicensed OpenAI-internal code or binary is copied into the repository.
- Full automated test suite passes before migration defaults change.
