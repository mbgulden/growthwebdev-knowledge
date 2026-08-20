# Exact-head re-review after successive independent blockers (2026-07-25)

## Trigger

An independent exact-head reviewer returns `CHANGES_REQUIRED` after a candidate already passed local focused/canonical/build gates, and a later repair itself receives another independent `CHANGES_REQUIRED` finding.

## Durable workflow

1. Accept valid findings immediately and mark the current commit blocked. Do not push, publish, merge, or use the candidate downstream.
2. Repair on the same focused branch/worktree when the task boundary still matches; do not widen paths silently.
3. Add permanent adversarial regression coverage for every valid blocker, including the prior blockers and the new one.
4. Run gates in distinct proof classes:
   - focused required/adversarial tests;
   - canonical local `tests/` suite when in scope;
   - clean-room wheel/non-editable proof when package import behavior matters;
   - post-commit exact readback for commit/tree/log/report bindings.
5. Commit the repair only after scope and worktree cleanliness are verified.
6. Dispatch a new independent exact-head review bound to the new commit/tree/parent and explicitly instruct the reviewer to reproduce **all prior blockers**, not only inspect the latest two-line delta.
7. Update outbox/report artifacts to show the previous review as `CHANGES_REQUIRED` and the new review as pending/active; then run a post-write verifier if those artifacts changed.

## Report boundary

Until the fresh reviewer returns `CLEAN`, report:

```text
STATUS=PARTIAL
REPAIRED_COMMIT=<sha>
REVIEW=<delegation id or reviewer id> ACTIVE
NOT_CLAIMING=independent CLEAN, PR, merge, deployment, hosted CI, or Linear update
```

## Pitfalls

- Do not treat local canonical green as a substitute for independent exact-head review after security/fail-closed defects.
- Do not let the reviewer scope collapse to only the last repair; prior valid findings must become permanent reproductions.
- Do not publish a repaired candidate while a fresh exact-head reviewer is still active.
- Do not edit proof packets after final verification without a new readback verifier that covers those packet edits.