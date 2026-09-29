# KOSIF Unified System Specification

## Status
Design specification for the next unified KOSIF architecture. GitHub is the canonical source for declarative system definition; runtime state remains outside Git.

## Goal
Present one coherent KOSIF surface to the user while preserving specialized internal execution engines. KOSIF Think is the cognitive orchestrator and capability owner; KOSIF Computer is the device/browser execution authority; Jev is a bounded decision specialist; Cloud/runtime services execute versioned manifests generated from the GitHub source.

## 1. Canonical Source of Truth
GitHub is authoritative for:
- versioned capability manifest
- lane definitions and contracts
- agent/model catalog and roles
- tool schemas and adapters
- routing policy
- risk gates and human checkpoints
- browser/Jev decision contract
- verification and recovery contracts
- benchmark definitions
- release metadata and migration rules

GitHub is NOT authoritative for live state such as:
- working/episodic memory
- telemetry and traces
- device/browser session state
- transient credentials/tokens
- health counters and latency statistics
- temporary routing scores

Runtime state belongs in approved runtime stores such as Upstash/Qdrant/local state stores and must be referenced by versioned interfaces rather than committed as live data.

## 2. Version Identity
Every deployed surface MUST expose the same identity tuple:

`release_id + git_sha + manifest_hash + schema_version`

Consumers:
- Cloudflare/runtime KOSIF Think
- ChatGPT KOSIF Think plugin
- KOSIF Computer capability adapter
- local CLI/API surfaces

If any consumer differs from the canonical manifest, it reports `OUT_OF_SYNC` rather than silently continuing as if current.

## 3. Unified Capability Manifest
Create a single machine-readable manifest that defines:
- KOSIF Think cognitive capabilities
- all KOSIF Computer capabilities exposed to Think
- browser execution capabilities
- WhatsApp/mobile/office/research/coding/graphics/voice lanes
- agent catalog
- cognitive perspective catalog
- routing constraints
- cost classes
- verification requirements
- permissions and human gates

KOSIF Think owns the user-facing capability catalog. KOSIF Computer remains an internal specialized executor rather than a duplicated implementation.

## 4. KOSIF Think / KOSIF Computer Contract
### KOSIF Think
Responsible for:
- intent understanding
- task decomposition
- cognitive perspective selection
- agent/model selection
- evidence collection
- routing
- Jev escalation when bounded ambiguity remains
- risk gating
- verification policy
- final synthesis
- learning signals and evolution proposals

### KOSIF Computer
Responsible for authorized side effects on device/browser surfaces:
- Playwright/CDP
- Chrome DevTools
- UI Automation
- App Manager
- Dialog Controller
- Screen State
- file operations
- workflows/watchers
- AutoHotkey/native input fallback
- Android/ADB and related device adapters when configured
- deterministic verification evidence collection

Think may expose all Computer capabilities as native KOSIF capabilities, but implementation remains single-sourced in Computer adapters to avoid duplicate code paths.

## 5. Cognitive Perspectives Engine
Perspectives are bounded evaluators, not simulated moods or identities. Each perspective must return structured claims, evidence, assumptions, risks, objections, confidence and recommendation.

Initial perspectives:
- Skeptic / Failure Analyst: searches for weak assumptions and failure modes
- Opportunity Seeker: searches for upside and overlooked possibilities
- Blunt Realist: tests feasibility against constraints
- Devil's Advocate: intentionally challenges the leading hypothesis
- Evidence Auditor: grades evidence quality and flags unsupported claims
- Synthesis Chair: reconciles evidence without erasing disagreement

Any sufficiently capable model may serve a perspective. Model identity is separate from perspective identity.

## 6. Jev Role
Jev is a bounded decision specialist, not a universal executor and not a permission authority.

Jev may:
- choose among a closed, observed candidate set
- score alternatives
- provide a structured decision packet

Jev may not:
- invent unobserved actions as executable candidates
- grant high-risk approval
- bypass human gates
- directly mutate permissions

For browser/device ambiguity, KOSIF Computer revalidates the one-time decision packet before side effects.

## 7. Meta-Router / Evolution Agent
Introduce a Meta-Router (Evolution Agent) that learns from telemetry and proposes routing/configuration improvements.

Inputs:
- task category
- selected agent/model/tool
- success/failure
- verifier outcome
- latency
- recoveries/stalls
- cost class
- evidence quality

The Evolution Agent MAY:
- propose weight changes
- propose prompt/policy changes
- propose new adapters or perspectives
- open a versioned change proposal/PR

The Evolution Agent MUST NOT:
- merge directly to protected main
- grant itself permissions
- expose or rewrite secrets
- disable human gates
- deploy an unbenchmarked behavior change directly to production

## 8. Self-Improvement Pipeline
`Telemetry -> Evaluation -> Evolution Proposal -> GitHub PR -> Tests -> Benchmarks -> Canary -> Verification -> Merge/Reject -> Versioned Release`

Every self-improvement proposal must compare against a baseline. If quality, safety, latency, or cost regress beyond configured thresholds, the proposal is rejected or rolled back.

## 9. Meta-Evaluator and Agent Reputation
Maintain task-specific performance profiles rather than one global agent ranking.

Example metrics:
- verified success rate
- evidence quality
- contradiction rate
- hallucination/error rate
- median/p95 latency
- recovery count
- cost class
- disagreement resolution quality

Reputation affects routing recommendations but never overrides permissions or safety gates.

## 10. Dynamic Council
Do not call every agent for every task.

Routing policy:
- simple/low-risk: deterministic/local fast path
- moderate ambiguity: 1-2 specialists
- high ambiguity/complexity: selected perspectives + specialist agents
- strong disagreement: add auditor or chair
- browser/device ambiguity: bounded Jev choice over observed candidates

The council is adaptive to task type, evidence needs and cost constraints.

## 11. Evidence and Verification Layer
Every substantive agent output is classified as one or more of:
- observed fact
- source-backed fact
- inference
- hypothesis
- opinion/recommendation
- unverified claim

Side-effect completion is never inferred from transport success alone. Observable postconditions are required.

## 12. Open-Source Intake Pipeline
New GitHub/open-source capabilities enter KOSIF through:
1. project discovery
2. license/provenance check
3. architectural review
4. capability extraction
5. sandboxed prototype/adaptation
6. security review
7. benchmarks and regression tests
8. compatibility adapter
9. optional production adoption

Prefer extracting robust ideas and interfaces over copying dependencies blindly.

## 13. Runtime Memory
Use separated memory tiers:
- Working memory: current task/session
- Episodic memory: completed task traces and outcomes
- Semantic memory: reusable knowledge and capability facts
- Procedural memory: verified workflows and recovery strategies

Runtime stores remain external to GitHub. Only schemas, retention policies and interfaces are versioned in Git.

## 14. Observability
A unified dashboard/status API should expose:
- current release identity
- sync state per consumer
- selected lane/agent/tool
- task state
- verifier status
- latency and recovery metrics
- cost class
- capability health

Secrets and private chain-of-thought are never exposed.

## 15. Safety and Permission Boundaries
Mandatory human gates include at least:
- CAPTCHA/anti-bot challenge handling
- OTP/MFA
- credential/security changes
- payment confirmation

Additional risk gates apply to destructive writes, publishing, external communications and permission changes.

The cognitive system can recommend an action; execution authority remains with the appropriate controlled executor and permission layer.

## 16. Generated Consumers
From the canonical GitHub manifest, generate or validate:
- Cloud/runtime capability config
- ChatGPT plugin metadata/tool catalog where supported
- KOSIF Computer adapter catalog
- CLI/API capability descriptions
- version/sync endpoints

Static schemas that require a ChatGPT plugin release remain versioned artifacts; dynamic capability metadata may be fetched from the runtime manifest endpoint.

## 17. Migration Strategy
1. Inventory current GitHub, Cloud/runtime and ChatGPT definitions.
2. Build the canonical manifest schema.
3. Import all existing capabilities without deleting working backends.
4. Add KOSIF Computer capabilities as internal Think-owned capability contracts.
5. Add version identity and drift detection.
6. Add Cognitive Perspectives and Meta-Evaluator.
7. Add Evolution Agent in proposal-only mode.
8. Add benchmark and canary gates.
9. Switch Cloud/runtime to generated manifest consumption.
10. Update ChatGPT plugin metadata/tool catalog from the same release.
11. Retire duplicate definitions only after verified parity.

## 18. Success Criteria
The migration is complete when:
- GitHub contains the canonical declarative definition.
- Cloud/runtime, ChatGPT and KOSIF Computer report the same release identity.
- no capability is independently hand-defined in multiple places without a generated/validated contract.
- KOSIF Think can route to all approved KOSIF Computer capabilities.
- Jev remains bounded and revalidated.
- Cognitive Perspectives are measurable evaluators.
- Evolution Agent can propose improvements but cannot self-authorize them.
- benchmark/regression/canary gates protect releases.
- runtime memory and secrets remain outside the repository.
