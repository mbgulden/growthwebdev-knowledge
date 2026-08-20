# Limited guarded AGY overnight dry run — July 2026 pattern

Use this reference when advancing from `AGY_OVERNIGHT_READINESS_GUARD_OK` to a first limited dry run (`AGY_LIMITED_OVERNIGHT_RUNNER_OK` / `AGY_LIMITED_OVERNIGHT_DRY_RUN_OK`).

## Guard-first rule

Before building or running anything, prove the guard is live in the deployed runtime:

```bash
git -C /home/ubuntu/.prismatic/runtime/prismatic-engine rev-parse --short HEAD
systemctl is-active prismatic-gateway
curl -fsS http://127.0.0.1:9000/api/gateway/agy/overnight-guard
curl -fsS -X POST http://127.0.0.1:9000/api/gateway/agy/overnight-guard/evaluate \
  -H 'Content-Type: application/json' \
  -d '{"allowed_agents":["agy"],"max_tasks":1,"requested_by":"fred","auto_merge":false,"production_deploy":false,"real_github_pr_create":false,"bulk_dispatch":false}'
```

Expected marker: `AGY_OVERNIGHT_READINESS_GUARD_OK`. If routes are 404 or readiness is blocked, do not bypass the guard by launching AGY directly.

## Stale PR pitfall

A prior readiness-guard PR can be open/green but not deployed. Audit `gh pr view`, current runtime HEAD, and route readback. If the PR is stale and its diff would delete newer dispatcher/queue/rate-limit work, do **not** merge it as-is. Salvage only the guard module/routes/tests onto current `main` and preserve newer lanes.

## Runner/control layer contract

The limited runner must:

- preflight the assigned-agent recovery/status surface before guard/model/launch when the slice is framed as continuing assigned-agent recovery; require `LINEAR_WEBHOOK_QUEUE_ACTIVE_OK`, `ASSIGNED_AGENT_EVENT_DISPATCH_OK`, `ASSIGNED_AGENT_RESULT_WRITEBACK_OK`, and `ASSIGNED_AGENT_DISPATCH_RECOVERY_OK`
- call the overnight guard before model preflight or launch (`runner_called_guard=true`)
- require `allowed_agents=["agy"]`, `agent=agy`, and `max_tasks<=1`
- fail closed on missing assigned-agent recovery markers, operator pause, guard blocked/manual review, unknown/ambiguous agent, `auto_merge`, `production_deploy`, real PR creation, bulk dispatch, or `stop_on_first_failure=false`
- verify AGY model with installed display name `Gemini 3.5 Flash (Medium)`; avoid stale aliases such as `gemini-3.5-flash-high`
- launch at most one AGY task and never run a second task to repair a bad packet; if a continuation arrives after success, do safe readbacks only rather than re-launching AGY
- persist run state and expose API readback: latest status, run_id, resolved_agent, max_tasks, launched_tasks, completed_work_id, merge_backlog_id, verification_gate, stop_reason, non_claims, all disabled side effects, and `assigned_agent_writeback_state=dry_run_no_live_linear_mutation`
- ingest the AGY packet through the real completed-work store, then evaluate merge backlog and verification gate
- stop after one task

## CLI vs gateway state pitfall

If the CLI uses a different state directory than the live gateway, the CLI runner may block before AGY launch because it cannot see the healthy completed-work/merge-backlog rows that made the gateway guard ready. Count this as `AGY_task_count=0`, not a failed AGY task. For the actual live proof, prefer the gateway dry-run endpoint so the runner calls/readbacks the same deployed state surface.

## Test portability pitfall

GitHub Actions cannot assume `/home/ubuntu` is writable. Unit tests may use safe `/home/ubuntu/...` provenance strings required by completed-work validation, but should not `mkdir /home/ubuntu` on CI. Use mocks/fakes for AGY launch in tests; only the final runtime proof launches one real AGY task.

## Runtime success proof fields

Final proof should include:

```text
guard_marker=AGY_OVERNIGHT_READINESS_GUARD_OK
runner_marker=AGY_LIMITED_OVERNIGHT_DRY_RUN_OK
runner_called_guard=true
guard_allowed=true
resolved_agent=agy
AGY_task_count=1
no_other_tasks_launched=true
bulk_dispatch=false
auto_merge=false
production_deploy=false
real_github_pr_created=false
stop_on_first_failure=true
completed_work_ingested=true
merge_backlog_evaluated=true
verification_gate_evaluated=true
dashboard_or_api_readback=true
completed_work_id=<id>
merge_backlog_id=<id>
verification_gate=<pass|blocked with reason>
```

Correct final claim after success: “A limited guarded AGY overnight dry-run path completed one controlled AGY task and stopped. Overnight autopilot is still not unbounded or active.”
