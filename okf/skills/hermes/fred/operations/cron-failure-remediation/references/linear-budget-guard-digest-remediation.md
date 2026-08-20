# Linear Budget Guard Remediation — Digest Cron Direct GraphQL Caller

## When this applies

Use this pattern when the Tier-1 Silent Failure Watchdog reports the active cron `Linear API Budget Guard — active cron enforcement` or another budget guard as failing because an enabled no-agent cron still contains raw Linear GraphQL access.

Typical guard output:

```text
LINEAR_BUDGET_GUARD_FAIL active cron scripts bypass budget shim
- <job_id> <job name> script=<profile>/scripts/<script>.py schedule=<schedule>
Policy: route Linear GraphQL through linear_api_compat.linear_call() or linear_budgeted_query.py.
```

## Durable fix pattern

1. Read the latest guard cron output and identify the exact offender script.
2. Patch the offender, not the guard:
   - Python cron scripts should import `linear_call` from `linear_api_compat`.
   - Attribute the call with a stable source name such as `cron.golden_thread_daily_digest`.
   - Remove direct `urllib.request` / `requests` calls to `https://api.linear.app/graphql`.
   - Remove now-unused raw endpoint constants like `LINEAR_GQL`.
3. Preserve graceful degradation for digest/report crons:
   - If the budget shim raises or returns GraphQL errors, return a concise warning line and continue with fallback project/registry signals when safe.
   - Do not bypass the budget shim because the digest is “read-only”; read-only polling still burns the tenant quota.
4. Run the budget guard directly and through the scheduler so `last_status` updates to `ok`.
5. Run Tier-1 in dry-run/no-linear mode and verify the recovered job is no longer in the current failure list.

## Focused verification checklist

Use a fresh `/tmp/hermes-verify-*` script created with `tempfile.mkstemp` and delete it afterwards. Check:

- `py_compile` on the changed offender and the guard.
- Static contract on the offender:
  - imports `linear_call`
  - includes a stable cron attribution string
  - no raw `api.linear.app/graphql`
  - no direct `urllib.request` Linear path
  - no leftover raw endpoint constant
- Direct guard run returns `LINEAR_BUDGET_GUARD_PASS` and no fail marker.
- Latest scheduler output for the guard job contains `LINEAR_BUDGET_GUARD_PASS`.
- Tier-1 dry run with `--dry-run --no-linear --json` reports `silent_failures: 0` or at minimum does not mention the recovered job ID.

## Pitfalls

- Do not whitelist a live digest/report cron just because it is read-only. Route it through the shared Linear budget gate.
- Do not stop after editing the offender. The scheduler must run the guard job once so `last_status` clears from `error`.
- Do not treat a historical Tier-1 digest as current after repair. Run the Tier-1 detector dry-run to verify the active failure bucket.
- Do not let repeated post-edit verification prompts cause stale evidence reuse. Each guard prompt needs a fresh `/tmp/hermes-verify-*` run and fresh cleanup evidence.
