# Assigned-Agent Result Writeback Recovery (2026-07)

Use after `ASSIGNED_AGENT_EVENT_DISPATCH_OK` is proven. This slice proves agent outcome/blocker persistence and safe operator-visible Linear writeback without making live Linear mutations.

## Contract

`agent run result/blocker → durable queue/run state → dashboard/operator visibility → explicit dry-run Linear writeback proof → retry/recovery status → no live mutation unless authorized`

## Durable queue row fields

Extend/verify `linear_webhook_queue` rows expose:

- `result_status`: `completed`, `blocked`, or `failed`
- `result_summary`
- `blocker_summary`
- `writeback_status`: e.g. `dry_run` or `blocked_live_unauthorized`
- `writeback_mode`: usually `linear_comment_preview`
- `writeback_preview`: exact Linear comment/update body preview, including marker
- `writeback_at`
- `retry_status`: `not_required`, `blocked_until_operator_review`, `retry_eligible`, `retry_requested`, etc.
- `retry_count`
- `recovery_status`: `completed`, `blocked`, `failed_retryable`, `queued_for_retry`, `writeback_blocked`, etc.

Expose these via `/api/gateway/webhooks/queue/status` on `latest_event` plus `result_writeback_marker=ASSIGNED_AGENT_RESULT_WRITEBACK_OK`.

## Safe writeback behavior

- Default to dry-run Linear writeback proof.
- Persist an exact Linear comment/update preview as durable operator-visible state.
- Completed result: `result_status=completed`, `retry_status=not_required`, `recovery_status=completed`.
- Blocker result: `result_status=blocked`, `retry_status=blocked_until_operator_review`, `recovery_status=blocked`.
- Failed result: `result_status=failed`, `retry_status=retry_eligible`, `recovery_status=failed_retryable`.
- Retry action should move the queue row back to `pending`, increment `retry_count`, set `retry_status=retry_requested`, and set `recovery_status=queued_for_retry`.
- If live Linear writeback is requested without explicit authorization, fail closed with `writeback_status=blocked_live_unauthorized`, `recovery_status=writeback_blocked`, and `linear_mutation=False`.

## Required fixture proof

Use temp HOME/state or fixture DB when possible. Do not touch live Linear. Prove:

1. Completed result produces persisted dry-run writeback preview and no retry required.
2. Blocker result produces persisted blocker preview and operator-review retry state.
3. Failed result produces persisted failure preview and retry-eligible state.
4. Retry moves failed row to pending and sets `retry_requested/queued_for_retry`.
5. Unauthorized live writeback request is blocked and records no live mutation.
6. Queue status API/dashboard fields expose result/writeback/retry/recovery state.
7. Old poller remains disabled/gated and allow-file absent.

## Compact proof packet shape

```text
COMMAND=<py_compile + focused pytest + tempfile completed/blocker/failed dry-run Linear writeback and retry/recovery proof>
AD_HOC_VERIFICATION=PASS
RESULT=PASS
LOG=/tmp/fred-assigned-agent-result-writeback-*.log
SCOPE=agent run result/blocker → durable queue/run state → dashboard/operator visibility → explicit dry-run Linear writeback proof → retry/recovery status
MARKER=ASSIGNED_AGENT_RESULT_WRITEBACK_OK
writeback_proof=completed/blocker/failed dry_run previews persisted; unauthorized live request blocked
retry_recovery_proof=failed retry_eligible then retry_requested/queued_for_retry
linear_mutations=0
NOT_CLAIMING=live_Linear_mutations,old_poller_reenabled,canonical_full_suite_green
cleanup=PASS
```

## Pitfalls

- Do not claim live Linear mutation/writeback from this slice unless an authorized live path is actually implemented and verified.
- Do not collapse result-writeback proof into the previous exact-agent wake proof; `ASSIGNED_AGENT_EVENT_DISPATCH_OK` only proves resolver/preflight/wake.
- Do not leave retry/recovery as implied by `dispatch_status`; persist explicit retry/recovery fields for operators.
- Do not reuse a stale `/tmp/hermes-verify-*` path. Create a fresh tempfile verifier and remove it after each stale-detector prompt.