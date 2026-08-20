# Limited AGY Overnight Readiness Guard

Session learning from the AGY overnight-readiness guard slice.

## Scope boundary

The overnight readiness guard is a control/policy layer only. It must not start AGY, dispatch tasks, enable auto-merge, create GitHub PRs, deploy production, or claim overnight autopilot is active.

Correct success claim:

```text
AGY limited overnight readiness guard is implemented and verified, but overnight autopilot is not active.
```

Correct marker:

```text
AGY_OVERNIGHT_READINESS_GUARD_OK
```

If only contract/design ships, use:

```text
OVERNIGHT_READINESS_GUARD_DESIGN_OK
```

If blocked, use:

```text
AGY_OVERNIGHT_READINESS_GUARD_BLOCKED
```

## Implementation shape

Class-level files used in the successful slice:

- `prismatic/agy_overnight_guard.py`
- `scripts/agy_overnight_guard.py`
- `prismatic/gateway/server.py`
- `prismatic/gateway/templates/dashboard.html`
- `tests/test_agy_overnight_guard.py`
- `tests/test_agy_overnight_guard_api.py`

Policy/state module surfaces:

- `evaluate_overnight_readiness(...)`
- `record_guard_decision(...)`
- `list_guard_decisions(...)`
- `record_overnight_run_attempt(...)`
- `list_overnight_run_attempts(...)`
- `set_operator_pause(...)`
- `operator_pause(...)`

State path precedence:

1. `PRISMATIC_AGY_OVERNIGHT_GUARD_STATE`
2. `PRISMATIC_STATE_DIR`
3. local `prismatic_state/agy_overnight_guard.db`

Minimum fail-closed policy fields:

```text
allowed_agents=["agy"]
max_tasks_per_run=2
max_consecutive_failures=1
stop_on_first_failure=true
auto_merge_enabled=false
production_deploy_enabled=false
real_github_pr_create_enabled=false
requires_one_task_success=true
requires_gateway_healthy=true
requires_ingestion_healthy=true
requires_merge_backlog_healthy=true
requires_verification_gate_healthy=true
requires_operator_pause_control=true
requires_operator_summary=true
```

## Fail-closed blockers to preserve

The guard should return `blocked`, `paused`, or `needs_manual_review` when any of these are true:

- latest one-task AGY proof missing
- completed-work ingestion unavailable
- merge backlog unavailable
- verification gate unavailable
- `auto_merge=true`
- `production_deploy=true`
- real GitHub PR creation requested
- bulk dispatch requested
- unknown/disabled agent requested, e.g. Ned
- `max_tasks` exceeds cap
- previous run failed and is unresolved
- operator pause is active
- required preflight/skills missing
- operator summary is not required

## API shape

Add local and gateway aliases:

```text
GET  /api/agy/overnight-guard
POST /api/agy/overnight-guard/evaluate
POST /api/agy/overnight-guard/pause
POST /api/agy/overnight-guard/resume
GET  /api/agy/overnight-guard/runs

GET  /api/gateway/agy/overnight-guard
POST /api/gateway/agy/overnight-guard/evaluate
POST /api/gateway/agy/overnight-guard/pause
POST /api/gateway/agy/overnight-guard/resume
GET  /api/gateway/agy/overnight-guard/runs
```

All endpoint responses should include `tasks_launched: 0` or equivalent non-claim proof.

## CLI shape

`script/agy_overnight_guard.py` should be dry-run/control only:

```bash
python scripts/agy_overnight_guard.py status
python scripts/agy_overnight_guard.py evaluate --max-tasks 1 --agent agy
python scripts/agy_overnight_guard.py pause
python scripts/agy_overnight_guard.py resume
```

Do not add a launch command without a separate explicit approval packet.

## Dashboard proof

Add a compact real-data operator card with:

- `data-proof-marker="agy-overnight-guard-card"`
- fetch from `${API_PREFIX}/agy/overnight-guard`
- readiness state
- allowed agents
- max tasks
- stop-on-first-failure
- auto-merge/deploy false
- operator pause
- blockers/warnings
- latest one-task success marker
- next safe action

Extract inline dashboard JS and run `node --check /tmp/hermes-dashboard-inline-agy-overnight-guard.js`.

## Verification command shape

Use compact logs. Do not stream full pytest/browser/API output into chat.

```bash
python3 -m py_compile \
  prismatic/agy_overnight_guard.py \
  prismatic/gateway/server.py \
  scripts/agy_overnight_guard.py \
&& python3 -m pytest -q \
  tests/test_agy_overnight_guard.py \
  tests/test_agy_overnight_guard_api.py \
  tests/test_agy_completed_work.py \
  tests/test_agy_merge_backlog.py \
  tests/test_agy_merge_backlog_api.py \
  tests/test_budget_caps.py \
&& node --check /tmp/hermes-dashboard-inline-agy-overnight-guard.js
```

Proof block:

```text
COMMAND=<exact command>
RESULT=PASS
LOG=/tmp/fred-agy-overnight-readiness-guard-verify.log
SCOPE=AGY limited overnight readiness guard policy/API/CLI/dashboard/tests
AD_HOC_OR_CANONICAL=ad-hoc targeted
NOT_CLAIMING=overnight_autopilot_active,auto_merge_enabled,bulk_agy_dispatch,production_deploy,real_github_pr_created,canonical_full_suite_green
MARKER=AGY_OVERNIGHT_READINESS_GUARD_OK
```

## Hermes stale-verification guard pattern

If Hermes reports stale verification after code edits, refresh evidence literally:

1. Remove stale temp verifier paths named by the guard, especially `/tmp/hermes-verify-mobile-branch-390.py` and any prior `/tmp/hermes-verify-*.py` for the slice.
2. Create a new OS-safe tempfile under `/tmp` with prefix `hermes-verify-`.
3. Run the exact focused command against changed behavior.
4. Clean up the fresh verifier and stale verifier files.
5. Report as `ad-hoc targeted; not canonical full suite` unless the real canonical suite ran.

Do not treat the old mobile overflow output as evidence about the AGY guard. It is the stale guard’s remembered failure, not the current changed behavior.
