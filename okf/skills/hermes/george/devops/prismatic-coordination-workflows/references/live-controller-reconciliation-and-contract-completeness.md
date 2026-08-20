# Live controller reconciliation and contract-completeness checks

Session-derived pattern from Prismatic better-than-North-Star execution where a durable ordered executor was ticking while George performed manual verification.

## Durable lessons

- Treat a five-minute executor as a concurrent actor. A verifier can fail because queue/control/handoff changed during the read, not because the candidate gate is invalid.
- When a state verifier fails after a live controller tick, do not force stale expectations. Re-read the authoritative queue, control state, current worktree head/tree, live producer PID, and handoff markers, then classify whether the semantic gate is equivalent or actually advanced.
- Derived artifact digests can legitimately change when the controller appends equivalent metadata such as a second read-only exact-head review to a pending receipt. Reconcile the digest fields rather than restarting the product gate.
- Duplicate read-only exact-head reviews are acceptable if both are bound to the same head/tree and there is no active writer. Record both reviewers; require unanimous CLEAN and let any valid REPAIR stop the line.
- Canonical green is not enough when the frozen repair contract required explicit negative regressions. Inspect the focused tests against every mandated failure mode before launching exact-head review.
- When a candidate is superseded by a repair, mark older reviews as superseded-head-only evidence so the executor cannot promote stale CLEAN/REPAIR results.

## Minimal reconciliation proof packet

```text
COMMAND=<state verifier over worktree head/tree, git status, producer PID, queue sha, control queue sha, receipt sha, handoff markers>
RESULT=PASS|BLOCKED
LOG=<path>
SCOPE=<issue/repair exact-head gate>
AD_HOC_OR_CANONICAL=state reconciliation
NOT_CLAIMING=<no merge/deploy/successor/cap increase unless explicitly authorized>
MARKER=<stable gate marker>
```

## Pitfalls

- Do not loop indefinitely chasing digest churn. If the semantic gate is unchanged and only derived receipt/queue hashes moved, reconcile once and report the boundary.
- Do not treat preparatory read-only next-slice analysis as successor implementation admission. Record it explicitly as analysis-only and keep implementation paused behind the active gate.
