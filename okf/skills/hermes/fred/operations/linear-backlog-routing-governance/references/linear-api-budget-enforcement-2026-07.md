# Linear API Budget Enforcement — 2026-07

## When this matters

Use this when Linear starts rate-limiting, Hermes/Prismatic cron jobs are suspected of leaking Linear API calls, or a new scheduled automation calls Linear GraphQL.

## Durable pattern

Do not only fix the current noisy job. Make the class of failure harder to reintroduce:

1. Inventory enabled cron jobs in `~/.hermes/profiles/orchestrator/cron/jobs.json`.
2. For every enabled job with a script, scan the script for direct Linear GraphQL usage:
   - `https://api.linear.app/graphql`
   - raw `urllib.request.urlopen(...)`/`requests.post(...)` against Linear
   - shell `curl https://api.linear.app/graphql`
3. Route Python callers through the shared budget shim:

```python
from linear_api_compat import linear_call

data = linear_call("cron.<stable_job_or_script_name>", query, variables)
```

4. Route shell callers through a shell-safe wrapper:

```bash
printf '%s' '{"query":"query { ... }", "variables": {}}' \
  | python3 /home/ubuntu/.hermes/profiles/orchestrator/scripts/linear_budgeted_query.py cron.<script_name>
```

5. Pin all legacy callers to the same budget/cooldown state:
   - `PRISMATIC_STATE_DIR=/home/ubuntu/work/prismatic-engine/prismatic_state`
   - `LINEAR_BUDGET_DB=/home/ubuntu/work/prismatic-engine/prismatic_state/linear_budget.db`
   - `LINEAR_RATE_LIMIT_COOLDOWN=/home/ubuntu/work/prismatic-engine/prismatic_state/linear_rate_limit_until.txt`
6. Add/schedule a guard that fails if any active cron script calls Linear GraphQL directly without the shim.
7. Demote stale high-frequency safety-net jobs to the intended cadence; a hidden every-5-minute poller can undo all code-level rate-limit work.

## Verification shape

Use an ad hoc `/tmp/hermes-verify-*` script that:

- `py_compile`s changed Python scripts.
- Runs `bash -n` for changed shell scripts.
- Runs the active cron budget guard and expects a pass.
- Mocks `linear_api_compat.linear_call` to test wrapper/call routing without burning live Linear quota.
- Asserts each patched script contains stable `cron.*` attribution.
- Removes temporary verifier/work directories and prints cleanup status.

Label this as **ad hoc targeted verification only — not full suite green** unless the full canonical suite was actually run.

## Pitfalls

- Do not spend Linear quota proving quota protection. Mock `linear_call` where possible.
- Do not stop after fixing the single script that triggered rate-limit symptoms. Scan enabled scheduled jobs; the leak is often a fleet/cadence problem.
- Do not trust comments like “daily safety net” — verify the actual cron schedule.
- Do not preserve or print Linear token values while inspecting auth/config.
