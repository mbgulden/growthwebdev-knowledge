# North Star reset execution when the prompt state is stale or already merged

Use this reference when Michael asks George to execute a Prismatic North Star reset / reset-prompt and live readback contradicts the prompt's assumed active PR state.

## Trigger

- A reset prompt names an active PR, producer, or gate, but direct GitHub/runtime proof shows the PR is already merged, the source main has advanced, or runtime/control state has drifted.
- The slice still needs George's merge-judge decision because the merge happened before a valid George `YES`.

## Required sequence

1. **Bind direct source truth first.** Read GitHub PR state, head SHA, merge SHA, remote `main`, tree parity, CI status, gateway health, runtime release SHA, generic dispatch/cap/producers, bus DB identity, bus `max(rowid)`, cursor, and relevant owner-lane repo truth before admitting the prompt's premise.
2. **If already merged, preserve the PR head anyway.** Create a clean detached worktree or durable ref at the exact merged PR head. Verify HEAD/tree/status/path allowlist. Do not review mutable `main` alone unless the merge tree is exactly bound to the PR head.
3. **Run adversarial semantic probes even when CI is green.** Time-window/journal-tail/freshness fixes especially need executable probes for offset preservation, future timestamps, exact cutoff boundaries, leading/unterminated complete-line behavior, multibyte slicing, and successful-stderr suppression.
4. **Separate proof classes in the verdict.** Focused tests, hosted PR/head CI, post-merge main CI, package build, Ruff lint/format, unfiltered Pytest, and ad-hoc semantic probes must be labeled separately. Green CI cannot override reproduced semantic failures.
5. **If George's verdict is `NO_REPAIR` after an unauthorized/early merge, issue a post-merge repair packet.** GitHub PR comment or checked-in report is the durable authority. If Telegram is used, verify scheduler/gateway delivery and read back the artifact containing the exact bot mention and repair scope.
6. **Do not produce an immutable release from a failed merge.** Write a release receipt marked `BLOCKED_NOT_PROMOTED`; keep deploy/restart/runtime repoint/Linear/generic-dispatch/cap changes false unless explicitly authorized and independently proven.
7. **Queue, but do not dispatch, the next task.** If the prompt requires a next Phase 3/runtime task, write/hash a task-manager-neutral queue brief with `BASE_SHA=DEFER_UNTIL_PREDECESSOR_CLOSES`, `STATUS=QUEUED_NOT_DISPATCHED`, no changed paths, and predecessor set to the failed repair gate.
8. **Reconcile both human and machine state.** Update `PRISMATIC_CURRENT_HANDOFF.md` and control JSON to the live truth, including stale prompt boundary, current verdict, repair owner, watcher state, delivery proof, queue status, and explicit non-claims.
9. **Run a final detector-style state verifier after the last artifact write.** Bind GitHub PR/merge/main truth, exact worktree, bus/cursor identity, delivery artifact, control JSON, handoff markers, queue status, active producers, and artifact digests. After this verifier passes, do not keep editing the proof files in the same execution unless a previously dispatched asynchronous reviewer returns with material evidence.
10. **If an asynchronous independent review returns after closeout, treat it as a new evidence event, not background noise.** First re-read the live PR head/state and any watcher baseline; if the head changed, invalidate the old review instead of appending it. If the head is unchanged, publish a durable addendum on the PR or checked-in packet, update handoff/control/review receipts from `pending` to the exact verdict, rehash touched artifacts, and run a small supplemental state verifier that binds the addendum URL, PR head, producer count, dispatch pause, and queue status. Keep this update evidence-only: no duplicate producer, no widened task, and no redispatch unless the live head changed or Michael explicitly authorizes a new slice.

## Verdict vocabulary

```text
STATUS=PARTIAL
VERDICT=NO_REPAIR
PR_STATE=MERGED_BEFORE_GEORGE_VERDICT
RELEASE_STATUS=BLOCKED_NOT_PROMOTED
GENERIC_DISPATCH=PAUSED
CAP=1
ACTIVE_PRODUCERS=0
QUEUE_STATUS=QUEUED_NOT_DISPATCHED
NOT_CLAIMING=George approved prior merge, immutable release, deploy/restart, runtime convergence, cursor/bus repair, Linear writeback, dispatch readiness, or cap increase
```

## Common pitfalls

- Treating a merged PR as automatically accepted because GitHub CI is green.
- Reviewing only `main` without binding tree parity to the exact PR head that was merged.
- Publishing an immutable release receipt as success when the merge occurred before a George `YES`.
- Letting the required “next task” become a hidden dispatch. It must remain a frozen queue brief until the predecessor is closed.
- Claiming Telegram dispatch from a scheduled cron job alone. Delivery requires scheduler/gateway log proof plus artifact readback.
- Editing handoff/control after the final verifier, which invalidates the digest packet and causes verifier loops.
