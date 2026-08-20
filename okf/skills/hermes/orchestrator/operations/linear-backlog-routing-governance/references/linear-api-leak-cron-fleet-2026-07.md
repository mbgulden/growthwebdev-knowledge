# Linear API Leak / Cron Fleet Mitigation — July 2026

## Trigger

Michael asked whether the Linear API leak/rate-limit problem already had tasks set aside or required fresh research. The correct answer was: research already existed (`GRO-1972` / LinearBudget work), but the remaining leak was operational drift in the cron fleet. Michael then clarified the desired finish line: make it **permanent-permanent** so all future dev follows the same budgeted shim until a better way exists.

## Durable Pattern

When Linear rate limits persist after the `LinearBudget`/dispatcher work is marked Done, do not redo broad research first. Check for cron-fleet bypasses and schedule drift:

1. Confirm whether a known umbrella issue/spec exists for Linear API rate-limit optimization.
2. Inspect **enabled active cron jobs** first; inactive or paused legacy files are secondary.
3. Look for direct `urllib.request`, `urlopen`, `requests.post`, `curl`, or raw `https://api.linear.app/graphql` usage outside the shared budget helper.
4. Patch legacy scripts to route through the compatibility shim / shared budget gate rather than each script owning its own raw GraphQL caller.
5. Check cron metadata for schedule drift: job name/paused reason may say “daily safety-net” while the actual schedule is still every 5 minutes.
6. Reduce high-frequency polling when event/delta paths exist; prefer daily safety-net + event-driven path over frequent broad pollers.
7. Add a recurring guard cron so future bypasses fail loudly.
8. Document the policy in OKF/standards for future dev.

## Required Standard Until Replaced

All Hermes/Prismatic automation that calls Linear GraphQL must route through the shared budgeted shim until a better central provider replaces it.

### Python cron/scripts

```python
from linear_api_compat import linear_call

data = linear_call("cron.<script_or_job_name>", query, variables)
```

The caller name must be stable and specific, for example:

- `cron.kai_delta_dispatcher`
- `cron.ned_delta_dispatcher`
- `cron.peer_review_orchestrator`

### Shell cron/scripts

Use a shell-safe wrapper instead of raw `curl`:

```bash
printf '%s' '{"query":"query { ... }", "variables": {}}' \
  | python3 /home/ubuntu/.hermes/profiles/orchestrator/scripts/linear_budgeted_query.py cron.<script_name>
```

## Concrete July 2026 Fix Shape

- `linear_api_compat.py` pinned shared state:
  - `PRISMATIC_STATE_DIR=/home/ubuntu/work/prismatic-engine/prismatic_state`
  - `LINEAR_BUDGET_DB=/home/ubuntu/work/prismatic-engine/prismatic_state/linear_budget.db`
  - `LINEAR_RATE_LIMIT_COOLDOWN=/home/ubuntu/work/prismatic-engine/prismatic_state/linear_rate_limit_until.txt`
- `linear_budgeted_query.py` was added as the shell-safe stdin JSON wrapper for shell crons.
- High-frequency and scheduled active cron scripts were converted to the budget shim, including:
  - `jules_session_watchdog.py`
  - `peer_review_orchestrator.py`
  - `jules_dispatcher.py`
  - `kai_delta_dispatcher.py`
  - `ned_delta_dispatcher.py`
  - `agy_completion_pinger.py`
  - `in_progress_long_runner_alerter.py`
  - `morning_queue_digest.py`
  - `aot_broken_link_check.py`
  - `nightly_backlog_delta.py`
  - `second_witness_agy_proxy.py`
  - `morning_digest.py`
  - `telegram_factory_digest.py`
  - `milestone_watch.sh` via `linear_budgeted_query.py`
- `Agent Dispatcher — Daily Safety-Net Sweep` was corrected from `every 5m` to daily (`0 8 * * *`) because webhook/event-driven dispatch is primary.
- `Kai Callback Monitor` was relaxed from every 2 minutes to every 5 minutes; it already had event-bus/delta-cache gating.
- `linear_api_budget_guard.py` was added and scheduled every 6 hours as a no-agent cron to scan enabled active cron scripts for unbudgeted Linear GraphQL calls.
- Policy doc was written at `okf/standards/linear-api-budget-policy.md`.

## Guard Pattern

A good guard should:

- Read the scheduler’s current `cron/jobs.json` rather than scanning every stale file in the repo.
- Consider only enabled, non-paused jobs.
- Resolve relative scripts under the active profile scripts directory.
- Fail if an active script contains raw Linear GraphQL endpoint usage without one of the budget markers:
  - `linear_api_compat`
  - `linear_call(`
  - `linear_budgeted_query.py`
- Allow only explicit exceptions:
  - the shim/wrapper/guard files themselves
  - OAuth/token refresh scripts that are not task-state GraphQL pollers
  - inactive legacy scripts
  - documented one-off migrations

Expected guard evidence shape:

```text
LINEAR_BUDGET_GUARD_PASS active cron Linear callers are budgeted
checked_linear_callers=8
budgeted_linear_callers=8
skipped_allowed_or_missing=2
```

## Verification Pattern

Use a `/tmp/hermes-verify-*` Python script that:

- `py_compile`s every changed Python script.
- Runs `bash -n` on changed shell scripts.
- Runs `linear_api_budget_guard.py` and asserts it passes.
- Imports/executes `linear_budgeted_query.py` with a mocked `linear_api_compat.linear_call` so no live Linear calls are made.
- Statically asserts each patched cron has the expected `linear_call("cron.<name>"...)` attribution marker.
- Checks the policy doc contains the future-dev standard.
- Cleans the temp script/workdir and reports the result as **ad hoc targeted verification**, not full suite green.

Example evidence shape:

```text
AD_HOC_VERIFY_PASS permanent linear budget enforcement
py_compile=passed
bash_n=passed
active_cron_guard=pass
shell_cli_routes_through_budget_shim=mocked_no_live_linear
patched_cron_attribution_markers=present
policy_doc=present
cleanup_exists=false
```

## Pitfalls

- Do not treat a Done umbrella issue as proof the live cron fleet is enforcing the budget; inspect actual cron scripts and schedules.
- Do not burn more Linear quota to diagnose quota burn. Prefer local docs/specs, cron metadata, source scans, and mocked verification.
- Do not patch one caller and stop if sibling cron scripts still own raw GraphQL helpers.
- Do not leave shell crons on raw `curl`; give them the same budget contract via a wrapper.
- Do not scan every virtualenv/build artifact when making the operational decision. Start from enabled active cron jobs.
- Do not claim canonical suite green for profile-script changes unless a real canonical suite exists and was run; use explicit ad hoc scope.
