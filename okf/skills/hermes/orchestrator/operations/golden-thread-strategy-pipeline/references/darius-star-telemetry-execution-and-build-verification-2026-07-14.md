# Darius Star telemetry execution + build verification nudge (2026-07-14)

## Context

Daily Golden Thread selected Darius Star because the registry had the oldest stalled timestamp. AGY research succeeded, but AGY execution timed out after partially editing the code.

## Durable workflow lesson

When AGY times out after partial edits:

1. Treat AGY as **timed out**, not as PASS.
2. Inspect the intended changed paths and AGY output.
3. Remove scratch/debug artifacts from the partial implementation before verification.
4. Run the smallest deterministic tests that satisfy the task rubric.
5. If a post-turn verifier names a canonical command, run that exact command too, even if stronger targeted tests already passed.
6. Report the canonical command separately as fresh verification evidence.

## Darius-specific implementation lesson

Darius Star’s `npm run build` exits `0` while warning that `js/main.js` is absent because the ES module conversion was superseded. This warning is expected for the current repo architecture; `AGENTS.md` says the game is served directly through ordered global scripts. Do not treat that warning as a failure when exit code is `0`.

## Verification sequence used

- `node tests/telemetry_test.js` — unit telemetry queue/privacy/resilience checks.
- `python3 scripts/verify_syntax.py` — repo syntax/load-order sanity for current architecture.
- `node tests/telemetry_integration_test.js` — Playwright/static-server smoke for telemetry events.
- `npm run build` — post-turn canonical verification nudge; passed with expected abandoned-ES-module warning.

## Pitfalls

- Do not claim the workspace is fully verified if the verification nudge asks for a specific command and it has not been run in the current post-edit state.
- Do not harden the `npm run build` warning into a general failure rule; the durable rule is: check exit code and repo architecture notes.
- If a local static-server integration test leaves a port occupied, free the port and rerun once; capture the retry pattern, not the transient port conflict.
