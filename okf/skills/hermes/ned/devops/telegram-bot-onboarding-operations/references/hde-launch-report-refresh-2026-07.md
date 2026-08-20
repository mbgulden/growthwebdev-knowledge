# HDE Launch Report Refresh Pattern — 2026-07

Use when refreshing a stale Human Design Engine launch report after staging/runtime changes.

## Durable pattern

- Treat server-side checks and live Telegram proof as separate evidence classes.
- If router/API/container/Redis/canary are healthy but live Telegram document proof is pending, mark the report **YELLOW**, not GREEN.
- Do not overwrite a stale RED report unless asked; prefer a dated superseding report such as `reports/hde_launch_verification_summary_YYYYMMDD.{json,md}`.
- Include both machine-readable JSON and human-readable Markdown when the report is launch evidence.
- Record branch and commit checked, service health, router metrics, Telegram `getMe` safe identity fields, guest canary status, build result or branch-shape caveat, live media proof status, remaining risks, and launch recommendation.
- Never include bot tokens, API keys, DB/Redis URLs, cookies, or raw Telegram logs.

## Live Telegram proof semantics

A live proof is complete only when the watcher observes:

1. at least two successful Telegram `sendDocument` deliveries for the intended comparison/report flow,
2. media queue pending count drains to `0`,
3. chat queue pending count drains to `0`,
4. router metrics remain healthy,
5. no fresh post-watch-start router delivery errors appear.

If the watcher is running but waiting for Michael to send the live prompt, write the report as **YELLOW / blocked pending user message** and name the watcher session. Do not claim launch-ready.

## Branch-shape caveats

On `deploy-fresh`/checkpoint-derived branches, frontend files such as `package.json` may be absent. Report this as a branch-shape caveat, not a build failure. If a router service is checked from that branch, ensure the router support modules required by `hde_tenant_router.py` are present in the branch being committed (`hde_rate_limits.py`, `hde_job_queue.py`, `hde_usage_budgets.py`, and `hde_router_metrics.py`) or the service/metrics check can be false evidence.

## Verification pattern

Before committing a launch report:

- run py_compile for router/canary/watcher/metrics modules using the venv that has repo dependencies when needed,
- run `hde_router_metrics.py --pretty`,
- run `hde_guest_canary.py --guest-id 23 --pretty`,
- check `hde_router.service`, `hde_api_staging.service`, and `guest-hermes-23`,
- run `git diff --cached --check`,
- run a staged secret scan that allows env var names/labels but rejects actual token-shaped strings and URL credentials.

For repeated Hermes verification nudges on report files, create a fresh `/tmp/hermes-verify-*` script that parses the JSON report, checks key Markdown phrases, confirms YELLOW/GREEN semantics match live proof state, and scans report text for secret-looking tokens/URLs. Remove the verifier and call it ad-hoc verification, not suite green.
