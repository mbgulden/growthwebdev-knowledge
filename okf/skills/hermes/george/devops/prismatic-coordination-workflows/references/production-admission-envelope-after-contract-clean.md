# Production Admission Envelope After Contract CLEAN/PASS

Use this pattern after a production-enforcement contract has been frozen and independently reviewed CLEAN/PASS, but before event admission or producer launch.

## Trigger

A Prismatic production contract has passed read-only review and the user authorizes continuing to the next safe stop, but has **not** explicitly authorized event admission, producer launch, PR, deployment, cron/timer mutation, or Linear writes.

## Pattern

1. **Bind to the exact merged base**
   - Fetch/read `origin/main` and record commit/tree.
   - Verify no local or remote branch already exists for the next slice.
   - Verify the target worktree path does not already exist.
   - Verify current event count for the future `task_id` is zero.

2. **Create only a local clean worktree/branch**
   - `git worktree add -b <slice-branch> <worktree> <exact-base-sha>`.
   - Verify `HEAD`, `HEAD^{tree}`, branch name, and tracked cleanliness.
   - Do not push.

3. **Freeze exact reviewed contract bytes as task envelope**
   - Copy the reviewed contract bytes into:
     - bus task path, e.g. `prismatic-agent-bus/tasks/<TASK-DIR>/TASK.md`;
     - worktree-local task path, e.g. `<worktree>/.prismatic-task/<TASK_ID>.md`.
   - Use byte-preserving copy (`install -D -m 0644` or equivalent) when file-tool size limits prevent a single exact read/write.
   - Verify `sha256sum` and `cmp` against the reviewed contract source.

4. **Prove admission-ready but not admitted**
   - Worktree must be tracked-clean.
   - The only allowed untracked path should be the bounded `.prismatic-task/<TASK_ID>.md` envelope.
   - Remote branch must not exist.
   - `task_admissions` count for the task must remain zero.
   - Producer launched must remain false/no receipt.

5. **Dispatch a read-only admission-envelope review**
   - The review should verify: exact contract hash, bus/worktree copies, exact base/tree, tracked clean state, bounded untracked task copy, absent remote branch, deployed schema-valid task ID/payload shape, zero admission, and explicit non-authority for event/producer/PR/deploy/cron/Linear.
   - Stop at `ENVELOPE_REVIEW=pending`; do not POST an event until the envelope review returns CLEAN/PASS and the user gives a separate explicit event-admission instruction.

## Proof packet fields

```text
CONTRACT_REVIEW=<delegation>:CLEAN/PASS
TASK_ID=<id>
TASK_SHA256=<reviewed-contract-sha256>
BASE=<exact-merge-base>
TREE=<exact-tree>
WORKTREE=<path>
BRANCH=<local-branch>
TRACKED_STATUS=clean
UNTRACKED=.prismatic-task/<TASK_ID>.md
REMOTE_BRANCH_EXISTS=false
EVENT_COUNT=0
PRODUCER_LAUNCHED=false
ENVELOPE_REVIEW=<delegation>:pending
AD_HOC_OR_CANONICAL=ad-hoc targeted admission-envelope readback
NOT_CLAIMING=admission, producer launch, implementation, remote push, PR, merge, deployment/restart, cron/timer mutation, tests executed, canonical green, or Linear write
```

## Pitfalls

- **Contract CLEAN/PASS is not event authorization.** It only permits preparing the next local envelope when user authorization says “continue to next safe stop.”
- **Do not let exact copies hide mutation.** Hash all copies and verify the worktree has no tracked changes after creating `.prismatic-task`.
- **Do not turn schema/table probing failures into doctrine.** If an optional DB table name is wrong, verify the authoritative zero-admission table and inspect live tables rather than recording a broad negative claim.
- **One-way provenance contracts need adversarial review before envelope prep.** If review finds circular digests or unsupported provenance (for example, runtime recomputation of Git tree IDs without Git-object evidence), freeze a corrected version and re-review exact bytes before preparing the envelope.
