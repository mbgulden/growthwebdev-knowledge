# North Star stop-line containment and same-task restart

Use this reference when the supervised cap-1 North Star plan is resumed and live state shows the predecessor gate was bypassed or helper agents continued work despite holds.

## Trigger signals

- A predecessor gate is still `NO_REPAIR`/unclosed, but `origin/main` advanced through successor PRs.
- A held PR or branch advances after a George hold/comment/restart instruction.
- Authorship or branch naming shows owner-lane confusion, e.g. one helper writing to another helper's branch.
- Hosted CI cannot start product checks because of a platform/billing/spending-limit condition; treat this as `BLOCKED`, not green or red product evidence.
- Manual one-shot cron runs report `execution_success=false` even though gateway logs may later prove actual delivery.

## Stop-line sequence

1. **Bind direct-source truth first.** Read `origin/main`, retained predecessor branch head, held PR head/base/files/checks, and active producer/process state. Trust GitHub/Git/process truth over stale handoff/control state.
2. **Issue a durable stop-line.** Use exact `@` mention for the owner lane and post durable GitHub holds when a PR is already involved. Make the boundary explicit: no new tasks, no merges, no PR close/delete/reset unless separately authorized.
3. **Preserve current-main containment evidence.** Create an isolated detached worktree at the actual `origin/main` SHA and rerun adversarial probes against current main, not only the original PR head. Distinguish focused tests/lint/build from semantic review.
4. **Supersede the repair contract from current main.** If the same defect still reproduces after successor merges, write/hash a current-main repair packet with exact base SHA/tree, retained branch, path allowlist, semantics, non-claims, and marker.
5. **Hold successor PRs, but do not close them without explicit authorization.** Post an explicit hold if a successor PR is open or advancing. Record head/parent/tree, files, auto-merge status, and check conclusion/start failure.
6. **Contain active writers.** If a helper continues writing after holds, distinguish manual task-level stop, process/gateway pause, and source-state stabilization. Do not assume a process is stopped just because the human says the task was stopped; verify process and source heads separately. Service/gateway pause and PR close/delete remain explicit operational decisions.
7. **Restart only after stability.** Before reissuing the same-task repair, prove `main`, predecessor branch, and held successor PR head are stable over a bounded window or via a change-only watcher. If stable, send one exact restart message bound to the current-main repair contract.
8. **Install or retarget a broad watcher.** Monitor `main`, predecessor repair branch, held successor PR head/state/checks, and new owner-lane PRs. Validate unchanged-baseline silence under cron-equivalent HOME. Pause narrower obsolete watchers.
9. **Update handoff/control/receipt.** Record the latest direct-source truth, current-main contract hash, watcher job id, delivery job/artifact hash, PR hold links, cap/producers/generic-dispatch state, and explicit non-claims.
10. **Final detector.** Run a state verifier that binds Git heads, durable JSON fields, handoff markers, delivery artifact content, watcher identity, active producers, and queued-not-dispatched next task.

## Delivery-proof discipline

- Scheduler output is not delivery proof by itself.
- A manual `cron run` returning `execution_success=false` can be a known false-negative for no-agent one-shots. Treat it as non-proof; check gateway/scheduler logs for `Job '<id>': delivered to <target>` and read back the generated artifact.
- After delivery, list active cron jobs. If the one-shot remains enabled, remove it before it can duplicate. If absent, record `NO_DUPLICATE_RISK`.

## Proof packet shape

```text
STATUS=<PARTIAL|BLOCKED|WAITING>
VERDICT=<STOP_LINE|MANUAL_CONTAINMENT_RESTARTED|AWAITING_REPAIR_HEAD>
MAIN=<sha>
PREDECESSOR_BRANCH=<sha>
SUCCESSOR_PR=<number>@<sha>
SUCCESSOR_HOLD=<url>
CONTRACT_SHA256=<sha256>
DELIVERY_JOB=<job_id>
DELIVERY_ARTIFACT_SHA256=<sha256>
WATCHER=<job_id>
GENERIC_DISPATCH=PAUSED
ACTIVE_PRODUCERS=0
NEXT_TASK=QUEUED_NOT_DISPATCHED
NOT_CLAIMING=<merge|deploy|restart|Linear|PR close/delete|cap increase>
```

## Pitfalls

- Do not retrofit approval after a PR was merged before George's verdict. Review anyway and issue the honest verdict.
- Do not let successor merges reset the same-task obligation. Rebase/supersede the repair contract to current main if the predecessor defect still reproduces.
- Do not call GitHub billing/spending-limit check-start failure a product-test failure, but also do not treat it as hosted CI green.
- Do not treat a gateway process being alive as proof a task is still writing; do not treat a manual task stop as proof the gateway process is gone. Verify both separately.
- Do not let held successor PRs become the next admitted work while the predecessor repair is still open.
