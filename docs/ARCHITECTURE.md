# KOSIF Think Unified Architecture

## Core loop
User request -> KOSIF Think preflight -> task planner -> tool/capability router -> risk gate -> executor -> verifier -> recovery/trace -> final result.

## Execution lanes
### Reasoning
Fast / Council / Deep, with independent frontier agents where needed.

### Computer
UI Automation, app lifecycle, workflows, dialogs, screen-state, file operations, Android/media/network helpers when available.

### Browser
Stable semantic action graph -> deterministic local ranking -> bounded Jev choice only when ambiguous -> Playwright/CDP execution -> DevTools diagnostics -> verifier -> delta/recovery.

### WhatsApp
Pair, send text/files/bundles, receive, groups, scheduling and job verification through the existing protected bridge.

## Safety boundaries
- CAPTCHA, OTP, payment and credential/security confirmations remain human checkpoints.
- Secrets never live in repository source or chat output.
- Cancellation must stop before the next side effect.
- A successful click or API call is not proof of task completion; verify observable postconditions.

## Migration approach
1. Keep current production tools live.
2. Import capability contracts/adapters into this repository.
3. Expose one KOSIF Think surface while retaining old tools as internal compatibility backends.
4. Add tests and health checks.
5. Switch routing gradually, then retire duplicate public surfaces only after verification.
