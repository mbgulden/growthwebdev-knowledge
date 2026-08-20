# Event admission → review_pending loop verification

Use this when reviewing Prismatic workflow health after a producer run, especially when the question is whether the Engine has crossed from backlog/event admission into bounded producer execution and canonical review state.

## Durable lesson

A successful producer run is not the same as a closed product-backlog loop. Report the conveyor in separate gates:

1. Linear/backlog metadata and dependency state.
2. Authenticated dashboard/event admission.
3. Durable outbox/consumer processing.
4. Producer execution and terminal process receipt.
5. Candidate artifact/proof packet.
6. Canonical terminal reconciliation (`review_pending`, `accepted`, `repair_required`, etc.).
7. Independent exact-head review.
8. PR/merge/deploy authorization.
9. Completed-work projection / Linear dry-run.
10. Automatic next dependency-ready selection.

Do not collapse these into a single PASS. A run can prove steps 2-6 while steps 1 and 7-10 remain partial or unproven.

## Verification pattern

For a bounded AGY admission run, collect compact evidence from the original sources, not from chat memory:

- Frozen task/TASK.md authorization boundary.
- Spool `RESULT.md`, `stdout.log`, `stderr.log`, verifier log digest, and any producer diagnostics.
- Runtime receipt/process result under the runtime directory, including exit code, cleanup verification, result path, and surviving process identities.
- Exact worktree git state: `HEAD`, merge-base/base ancestry, changed paths, `git diff --check`, and dirty tracked state.
- Gateway/dashboard API state for AGY activity/completed work.
- Linear bounded metadata for the current issue and likely successors.
- Outbox/claim state where available.

## Reporting rule

Lead with the behavior/state before IDs:

- Problem
- Changed
- Why it matters
- State
- Next move
- IDs/hashes/logs

Use `PARTIAL` when the event/producer/review-pending path works but Linear write-back, independent review, or next-task selection is still pending.

## Pitfalls

- A stale frozen task header like `QUEUED_NOT_ADMITTED` may remain after successful admission; call it a stale projection instead of treating it as the live state.
- If an initial consumer attempt failed but a bounded retry against the same event succeeded, record the hardening note without over-claiming full hands-off autonomy.
- Dashboard/API `review_pending` is a canonical terminal state for producer completion, not independent acceptance.
- Do not admit successors (for example runner/export validation tasks) before exact-head review and acceptance of the predecessor.
- Do not claim Linear ordering/dependencies are operational unless relation metadata or a dry-run proves it.
