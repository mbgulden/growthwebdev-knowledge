# AGY unattended-window guard lessons — July 2026

Session-specific notes for the AGY class-level governance skill.

## What changed

Prompt 2 implemented the operator-approved `max_tasks=2` unattended-window guard/controller as a control-plane slice only:

- Marker: `AGY_LIMITED_UNATTENDED_WINDOW_GUARD_OK`
- No AGY task launches in this slice (`launched_tasks=0`, `two_AGY_tasks_launched=false`)
- Still AGY-only, one-task-at-a-time, stop-on-first-failure, no auto-merge, no bulk dispatch, no production deploy, no real GitHub PR creation, no live Linear mutation.
- API/CLI/status surfaces evaluate whether a 2-task window *would be allowed*, not execute it.

## Durable pitfall: predecessor marker compatibility

The existing overnight-readiness guard originally looked only for the older one-task proof marker:

```text
AGY_AUTOPILOT_ONE_TASK_DRY_RUN_OK
```

The newer Prompt 1 path completes through:

```text
AGY_LIMITED_OVERNIGHT_DRY_RUN_OK
AGY_LIMITED_OVERNIGHT_DRY_RUN_PACKET_OK
```

When Prompt 2 builds on Prompt 1, the guard must recognize the newer limited dry-run proof as satisfying the predecessor proof requirement. Otherwise the unattended-window controller may be correctly implemented but live evaluation will 409 with:

```text
overnight guard blocked/paused/manual_review
reason=latest one-task AGY proof missing
```

Fix pattern: teach the guard compatibility layer to accept both proof families, preserving the old marker path:

```text
AGY_AUTOPILOT_ONE_TASK_DRY_RUN_OK OR AGY_LIMITED_OVERNIGHT_DRY_RUN_OK
```

Add regression tests that seed a completed-work row with `AGY_LIMITED_OVERNIGHT_DRY_RUN_PACKET_OK` and assert `evaluate_overnight_readiness(max_tasks=2)` is ready.

## Durable pitfall: PR merged before late compatibility patch

If a PR is merged/deployed and its branch deleted before a late compatibility fix lands, do not force-push against the deleted/stale branch. Convert only the missing compatibility diff into a small follow-up branch from fresh `origin/main`, open a new PR, wait for CI, then deploy.

## Verification pattern

For Prompt 2, use compact ad-hoc proof like:

```text
COMMAND=python3 -m py_compile prismatic/agy_overnight_guard.py prismatic/agy_unattended_window.py prismatic/gateway/server.py scripts/agy_unattended_window.py && python3 -m pytest -q tests/test_agy_overnight_guard.py tests/test_agy_unattended_window.py tests/test_agy_unattended_window_api.py; plus tempfile allowed max_tasks=2 guard proof + blocked max_tasks=3 proof + CLI status outside repo
AD_HOC_VERIFICATION=PASS
RESULT=PASS
LOG=/tmp/fred-agy-unattended-window-guard-verify.log
SCOPE=AGY max_tasks=2 unattended window guard/controller/API proof for workspace changed files
MARKER=AGY_LIMITED_UNATTENDED_WINDOW_GUARD_OK
```

Always distinguish:

- GitHub CI green for PRs
- deployed runtime/API readback
- workspace-changed-path ad-hoc verification when Hermes stale verifier complains

The stale verifier may reference an unrelated old mobile dashboard verifier; refresh against the changed workspace paths under `/home/ubuntu/work/prismatic-engine`, not only the deployed runtime checkout.