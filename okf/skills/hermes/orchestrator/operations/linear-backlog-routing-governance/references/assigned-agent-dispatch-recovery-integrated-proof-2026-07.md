# Assigned-agent dispatch recovery integrated proof — 2026-07

Use this reference when finishing the assigned-agent recovery sequence after the separate queue, exact-agent dispatch, and result-writeback slices are already proven.

## Target marker

`ASSIGNED_AGENT_DISPATCH_RECOVERY_OK`

This marker is not earned by pointing to prior independent proofs. It requires one controlled task that exercises the whole chain in a single run:

1. Durable queue row exists for a controlled fixture identifier.
2. Resolver maps it to exactly one intended known agent.
3. Preflight passes for that exact agent.
4. Wake records exactly one dry-run wake for that agent.
5. Result writeback persists a dry-run Linear comment/update preview with `linear_mutation=False`.
6. Queue status exposes `dispatch_recovery_marker=ASSIGNED_AGENT_DISPATCH_RECOVERY_OK`.

## Implementation pattern

- Add a narrow integration helper/path that composes the existing primitives instead of duplicating resolver, preflight, wake, or writeback logic.
- Recommended helper shape:
  - input: `identifier`, `result_status`, `result_summary`, `blocker_summary`, `dry_run=True`
  - internally calls exact-agent dispatch by identifier
  - then calls result-writeback by `run_id`
  - returns `{marker, ok, phases, dispatch, writeback, linear_mutation}`
- `phases` should make the proof legible:
  - `resolver: true`
  - `preflight: true`
  - `wake: true`
  - `result_writeback: true`

## Controlled fixture proof

Use temp state and a controlled identifier such as `GRO-RECOVERY-CONTROLLED` with a single explicit label, e.g. `agent:kai`.

Assertions:

```text
marker=ASSIGNED_AGENT_DISPATCH_RECOVERY_OK
chain_proof=resolver:true,preflight:true,wake:true,result_writeback:true
controlled_task=<identifier> agent:<agent> dry-run
linear_mutations=0
old_poller_processes=0
old_poller_user_unit=disabled
allow_file_absent=true
```

Also assert queue-row readback:

- `resolver_status=resolved`
- `preflight_status=passed`
- `claim_owner=<agent>`
- `result_status=completed` or the controlled expected result
- `writeback_status=dry_run`
- `retry_status=not_required` for completed fixtures

## Verification packet shape

Use a fresh `/tmp/hermes-verify-*` tempfile script and delete it after the run.

Recommended compact packet:

```text
COMMAND=python3 -m py_compile prismatic/dispatcher.py prismatic/ingestion_queue.py prismatic/gateway/server.py scripts/drain_webhook_queue.py prismatic/linear_rate_limit.py && python3 -m pytest -q tests/test_assigned_agent_event_dispatch.py tests/test_linear_webhook_queue_active.py tests/test_dispatcher_polling_budget.py tests/test_dispatcher_activation.py; plus tempfile one controlled task resolver→preflight→wake→result-writeback proof
AD_HOC_VERIFICATION=PASS
RESULT=PASS
LOG=/tmp/fred-assigned-agent-dispatch-recovery-verify.log
SCOPE=assigned-agent recovery chain for one controlled task
MARKER=ASSIGNED_AGENT_DISPATCH_RECOVERY_OK
changed_paths_checked=<exact absolute paths from detector or edit set>
runtime_head=<short sha when deployed>
chain_proof=resolver:true,preflight:true,wake:true,result_writeback:true
controlled_task=<identifier> agent:<agent> dry-run
dashboard_api_proof=/api/gateway/webhooks/queue/status 200 dispatch_recovery_marker
linear_mutations=0
old_poller_processes=0
old_poller_user_unit=disabled
allow_file_absent=true
pytest_summary=<focused pytest summary>
NOT_CLAIMING=live_Linear_mutations,old_poller_reenabled,bulk_redispatch,canonical_full_suite_green
cleanup=PASS
fresh_verifier_absent=true
```

## Pitfalls

- Do not claim the recovery marker from the separate `ASSIGNED_AGENT_EVENT_DISPATCH_OK` and `ASSIGNED_AGENT_RESULT_WRITEBACK_OK` proofs; run one combined proof.
- Do not use a live Linear mutation for the recovery proof. Dry-run writeback is the acceptance target unless explicitly authorized otherwise.
- Do not broaden the proof into backlog redispatch. One controlled task is the gate.
- If the stale verifier repeats with unrelated mobile-dashboard output, rerun the fresh scoped tempfile verifier and emit only the compact proof block with the exact changed paths.
