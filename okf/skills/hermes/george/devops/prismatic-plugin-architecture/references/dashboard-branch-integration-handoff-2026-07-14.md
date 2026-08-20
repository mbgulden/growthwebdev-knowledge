# Dashboard branch integration handoff pattern — 2026-07-14

## Context

Michael asked for a Markdown report Fred could use while doing a painful dashboard integration lift. The risk was not a single code bug: it was losing well-planned dashboard/plugin/release-proof work while Fred integrated a large protected governance dashboard branch.

Observed pattern:

- `deploy-fresh` carried Fred's protected dashboard shell and live-adapter wiring.
- `origin/main` carried newer North Star / OKF / public launch / plugin architecture / PWP lifecycle / security / release proof docs, scripts, and tests.
- The branches had diverged; neither was ancestor of the other.
- The correct answer was not “reset one branch to the other.” It was a preservation/integration report.

## Useful report structure

For future Prismatic dashboard handoffs, produce a report with:

1. **Executive summary** — preserve both sides; identify the current branch/HEAD and main reference.
2. **What is already good** — recent PR stack, protected dashboard route, current tabs, current live adapters.
3. **Branch divergence warning** — explicitly say not to reset either branch over the other.
4. **Assets to preserve from each side**:
   - Fred/dashboard branch: dashboard shell, gateway routes, integration verifier, ingestion/merge/foundation/native cron/timeline adapters.
   - Main/Kai branch: North Star, dashboard-primary docs, OKF evidence map, public launch/security/release docs, smoke scripts, visual QA, plugin/PWP/dashboard tests.
5. **Current ingestion queue status** — distinguish compatibility/read-only status from a true durable queue runner.
6. **Optimal path** — create a clean integration branch from the dashboard branch, port missing proof assets, reconcile checks, upgrade ingestion queue, run combined verification, then PR.
7. **Do-not-do list** — no blind reset, no wholesale dashboard replacement, no treating docs/proof scripts as disposable, no claiming readiness from route existence alone.
8. **Final marker** — e.g. `DASHBOARD_MAIN_PROOF_INTEGRATION_OK`.

## Key technique

Use static inspection to map dashboard tabs and API wiring before writing the handoff:

- Extract tab buttons / section IDs from `prismatic/gateway/templates/dashboard.html`.
- Extract FastAPI route decorators from `prismatic/gateway/server.py`.
- Compare path existence between the dashboard branch and main reference for docs, scripts, tests, and plugin modules.
- Run lightweight syntax checks if dependencies are missing:
  - extract inline dashboard `<script>` and run `node --check`
  - run `python3 -m py_compile` on key modules
- If canonical FastAPI/TestClient tests are blocked by missing deps, label that as environment-prep blocker, not dashboard failure.

## Ingestion queue distinction

A dashboard queue tab that reads recent EventBus history or returns compatibility `accepted_noop` retry/purge responses is not yet the real ingestion queue runner.

Optimal next state:

- Read durable `linear_webhook_queue.db` under `PRISMATIC_STATE_DIR`.
- Show real event statuses: `pending`, `processing`, `completed`, `failed`, `stale`, `dead_letter`, `replayed`.
- Provide bounded drain-now action shared with `scripts/drain_webhook_queue.py` or its internal queue-drain function.
- Retry should re-enqueue or move failed/stale rows back to `pending` with audit note.
- Purge must be confirmation-gated and limited to safe terminal/stale rows.
- Avoid unsafe shell execution inside the web request path.

## Ad-hoc verification for Markdown handoffs

After writing a report artifact, create a temporary `/tmp/hermes-verify-*.py` script that checks:

- file exists
- required headings/phrases are present
- expected tab labels or path references are present
- obvious token/secret assignment patterns are absent
- line count, byte count, SHA256

Run it, remove it, and report it explicitly as **ad-hoc targeted verification**, not canonical suite green.
