# Current Work Wrap + Course-Correction Prompt Pattern

Use when Michael asks whether George/Prismatic is on-track and wants a prompt to wrap the active work while easing into a correction. This is a narrower pattern than a broad readiness audit: answer the strategic question, then produce an executable closeout prompt that prevents new uncontrolled work.

## Trigger signals

- Current strategy is directionally correct but coordination/runtime/control-plane drift is accumulating.
- One exact producer or repair candidate is active, but state/handoff text is stale.
- Watchers, wrappers, pytest children, or old task processes may remain alive after a candidate appears committed.
- The next safe move is not a new slice; it is closing the current exact candidate and reconciling the truth plane.

## Required sequence

1. **Assess with direct proof before verdict.** Bind gateway/dashboard/API health, process state, active producer count, cap/dispatch status, relevant PR/head/CI state, runtime release/checkouts, cursor/bus identity, and current handoff/control summaries.
2. **Split the verdict.** It can be `PARTIAL — strategically on-track under supervision; operational course correction required now`.
3. **Finish the current exact task first.** Do not abandon a safety repair mid-flight just because the control plane needs cleanup. Bind branch/head/tree/changed paths and inspect the candidate independently.
4. **Freeze intake.** Keep generic dispatch paused and cap 1; launch no second producer, no unrelated helper slice, and no cap increase while closeout/correction is open.
5. **Contain task-owned process debt after inspection.** Identify wrapper/child/self-review/pytest processes; terminate only task-owned stale processes after preserving logs/state.
6. **If rejected, stop for redesign rather than automatic Repair N+1.** Multiple repairs on the same seam are a design-signal; require a short redesign brief before another repair.
7. **Reconcile the operator truth plane.** Update stale handoff/control fields, distinguish direct API truth from stale summary/audit truth, and remove superseded next-action text.
8. **Keep authorization gates explicit.** Production deploy/restart/repoint, live cursor/bus mutation, Linear writes, dispatch resumption, cap increases, credential rotation, and PR close/delete require separate authorization.
9. **Deliver as a Telegram-downloadable Markdown prompt** plus compact chat verdict. Include marker, exact head/task hash when known, phases, proof packet format, and non-claims.
10. **Verify the artifact after the final write.** Read back the key lines and hash the file before giving `MEDIA:/...`.

## Prompt phase skeleton

```markdown
# George Prompt — Close the Active Slice, Then Course-Correct Prismatic Operations

Current verdict: `PARTIAL — strategically on-track under supervision; operational course correction required now`

## Authority and safety boundary

Allowed: read-only inspection, exact-candidate local verification, task-owned process cleanup after inspection, durable handoff/control reconciliation, focused source repair within the current contract, PR creation, and merge only under exact-head policy.

Not allowed without separate authorization: deploy/restart/repoint, mutate live bus/cursor, resume dispatch, raise cap, write Linear, rotate credentials, close/delete PRs/branches, launch unrelated producers.

# Phase 0 — Freeze intake and bind exact current state
# Phase 1 — Inspect/contain task-owned process debt
# Phase 2 — Independent exact-candidate review
# Phase 3 — Closeout or redesign decision
# Phase 4 — Control-plane truth reconciliation
# Phase 5 — Next-slice decision gate
```

## Proof packet

```text
COMMAND=<grouped readback/verifier command>
RESULT=<PASS|PARTIAL|BLOCKED>
LOG=<downloadable .md path or verification log>
SCOPE=current active slice closeout + course-correction prompt
AD_HOC_OR_CANONICAL=ad-hoc targeted live readback
NOT_CLAIMING=<merge/deploy/runtime parity/dispatch readiness/cap increase/etc.>
MARKER=GEORGE_REPAIR_CLOSEOUT_AND_CONTROL_PLANE_COURSE_CORRECTION
```

## Pitfalls

- Do not let stale handoff `next_action` text override direct proof of current repair number/head/process state.
- Do not call API/dashboard availability `dispatch readiness` when consumer cursor/bus or downstream writeback is blocked.
- Do not turn a course-correction prompt into a deploy/restart authorization.
- Do not give only an in-chat prompt when Michael requested a downloadable `.md` document.
