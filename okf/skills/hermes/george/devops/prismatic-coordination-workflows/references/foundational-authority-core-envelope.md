# Foundational authority-core contract and admission-envelope pattern

Use when a Prismatic foundational issue is blocked at full production integration, but a smaller non-overlapping authority/core slice can be safely prepared.

## Trigger

- Linear issue is current and upstream dependencies are done, but merged topology lacks the final runtime surface or has a preserved dirty recovery checkpoint overlapping production adapter files.
- A full implementation contract would race or overwrite a preserved checkpoint, but a narrower authority-core slice can add isolated schema/API/process-adapter foundations.
- Async reviews return out of order and may be valid for stale contract hashes.

## Pattern

1. **Separate full blocker from narrower slice.** Preserve the full-integration blocker/precontract as authoritative for production integration. Do not treat a narrower authority-core contract as clearing the production blocker.
2. **Freeze contracts by version, never mutate blocked versions.** When an independent review blocks V1/V2, preserve it and write V2/V3 as a new immutable artifact with the minimal correction. Record each review by delegation ID, exact SHA, line count, and blocking reason.
3. **Triage stale async reviews by exact hash.** A CLEAN/PASS review for an older precontract is useful provenance only for that artifact; it does not unlock a newer contract or envelope.
4. **Require contract CLEAN/PASS before task copies.** Do not create the bus task/worktree task/event until the exact contract version has independent `CLEAN/PASS`.
5. **Freeze a pre-admission envelope, then review the envelope.** After contract acceptance, create the declared local-only branch/worktree at the exact base/tree, copy reviewed bytes verbatim into the bus task and `.prismatic-task`, prove tracked tree clean, and dispatch a fresh read-only envelope review before admission.
6. **Keep event rows zero until envelope review is clean and Michael explicitly authorizes admission.** Verify task-admissions/claims/lifecycle/outbox counts for the exact task ID are zero after every freeze/update.
7. **Prove overlapping recovery invariance.** If another preserved checkpoint shares the base or adjacent files, record its patch SHA and implementation blob IDs before and after envelope creation. The envelope may add only expected orchestration artifacts such as `.prismatic-task/`.
8. **Stop before side effects.** Envelope `CLEAN/PASS` means admission-ready at most; it is not event authorization, producer launch, implementation success, canonical suite green, PR, merge, deploy, cron/timer mutation, or Linear write.

## Minimum proof fields

```text
TASK_ID=<internal compliant task id>
CONTRACT_VERSION=<N>
CONTRACT_SHA256=<sha>
CONTRACT_REVIEW=<delegation:CLEAN/PASS>
BASE_COMMIT=<sha>
BASE_TREE=<tree>
BRANCH=<local branch>
WORKTREE=<path>
BUS_TASK=<path>
WORKTREE_TASK=<path>
TASK_COPIES_SHA256=<same sha>
TRACKED_DIFF_COUNT=0
EXPECTED_UNTRACKED=<e.g. .prismatic-task/>
EVENT_COUNT=0
CLAIM_COUNT=0
LIFECYCLE_COUNT=0
OUTBOX_COUNT=0
RECOVERY_CHECKPOINT_SHA256=<sha or n/a>
RECOVERY_BLOBS_UNCHANGED=<true|n/a>
ENVELOPE_REVIEW=<delegation:pending|CLEAN/PASS|BLOCKED>
NOT_CLAIMING=admission readiness/event/producer/implementation/canonical suite/PR/merge/deploy/cron mutation/Linear write
```

## Pitfalls

- Do not reuse a dirty or prior orchestration worktree just because it exists; create the contract-declared clean worktree at the exact base.
- Do not collapse `contract CLEAN/PASS`, `task copies frozen`, `envelope CLEAN/PASS`, and `event admitted` into one state. They are separate gates.
- Do not let stale review summaries overwrite newer contract lineage. Bind every review to exact artifact SHA.
- Do not claim downstream status/projection issues are unblocked until the upstream authority provides the durable read/query and schedule-bucket model they depend on.
