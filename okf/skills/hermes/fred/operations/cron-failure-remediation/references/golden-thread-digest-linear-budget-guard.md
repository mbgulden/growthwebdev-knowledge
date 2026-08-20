# Golden Thread Digest Linear Budget Guard Recovery

## When this applies

Use this when the Linear API Budget Guard cron reports an active deterministic digest or watchdog script bypassing the shared Linear budget shim.

## Failure signature

Latest cron output for `Linear API Budget Guard — active cron enforcement` shows:

```text
LINEAR_BUDGET_GUARD_FAIL active cron scripts bypass budget shim
- <job_id> <job name> script=<profile>/scripts/<script>.py schedule=<schedule>
Policy: route Linear GraphQL through linear_api_compat.linear_call() or linear_budgeted_query.py.
```

In this session the offender was `golden_thread_daily_digest.py`, which still had a raw direct `https://api.linear.app/graphql` / `urllib.request` path even though the system had a shared budget shim.

## Fix pattern

1. Read the exact latest guard output to identify the active offender.
2. Patch the offender, not the guard allowlist, unless the offender is a true documented exception.
3. For Python cron scripts:

```python
from linear_api_compat import linear_call

payload = linear_call(
    "cron.<script_or_job_name>",
    query,
    variables,
)
```

4. Remove raw Linear HTTP surfaces from that script:
   - `https://api.linear.app/graphql`
   - `urllib.request` / `urlopen` for Linear
   - `LINEAR_GQL` constants
   - direct Authorization header construction for Linear task queries
5. Keep graceful degradation: if `linear_call()` raises or returns GraphQL errors, the digest should emit a bounded note, not crash a user-facing summary unless the cron's contract is to fail.
6. Run the budget guard directly.
7. Run the affected cron through Hermes scheduler so its `last_status` becomes `ok`.
8. Run Tier-1 Silent Failure Watchdog dry-run/no-linear/no-send and confirm the recovered job is no longer a current silent failure.

## Verification checklist

Use a fresh `/tmp/hermes-verify-*` script and clean it up. Verify:

- `py_compile` for the changed offender and guard script.
- static contract:
  - imports `linear_call`
  - has caller attribution like `cron.golden_thread_daily_digest`
  - no raw `api.linear.app/graphql`
  - no `urllib.request` Linear path
  - no `LINEAR_GQL` constant
- direct guard run includes `LINEAR_BUDGET_GUARD_PASS` and not `FAIL`.
- latest scheduler output for the guard job contains PASS and not FAIL.
- Tier-1 dry-run JSON has `silent_failures: 0` or at least does not include the recovered job id as current.

Report this as **ad hoc targeted verification**, not full suite green.

## Pitfalls

- Do not silence the guard by adding broad exceptions for active cron scripts. Patch the active caller to use the shared budget gate.
- Do not trust budget DB silence as proof the path is budgeted; a bypass can skip the DB entirely.
- Do not rely on a direct script run only. Also run/read the scheduler output so future watchdogs see recovered state.
- Do not parse `linear_api_compat.linear_call()` responses with one assumed wrapper shape in all scripts; normalize direct GraphQL data-object vs top-level `data` wrappers where needed.
