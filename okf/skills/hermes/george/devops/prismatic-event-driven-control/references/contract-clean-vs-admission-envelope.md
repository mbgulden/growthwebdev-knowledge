# Contract CLEAN/PASS vs admission-envelope CLEAN/PASS

Use when Prismatic event admission is being prepared from a reviewed task contract.

## Gate distinction

Do not treat a reviewed contract as an admitted or admission-ready task. Keep these gates separate:

1. **Contract artifact frozen** — exact Markdown/spec bytes exist and are hashed.
2. **Contract review CLEAN/PASS** — an independent reviewer accepted those exact bytes.
3. **Task copies frozen** — the exact reviewed bytes are copied verbatim to the durable bus task and worktree `.prismatic-task` in the contract-declared clean worktree.
4. **Envelope review CLEAN/PASS** — an independent read-only reviewer verifies copied bytes, local branch/worktree/base/tree, zero tracked implementation diff, expected orchestration artifacts only, zero event/claim/lifecycle/outbox rows, and preservation of any overlapping recovery checkpoint.
5. **Explicit admission authorization** — Michael authorizes the exact one-event/one-cap-1-producer action.
6. **Event admitted / producer launched** — only after the authenticated route accepts the event and the consumer launch receipt is verified.

## Required zero-side-effect checks before admission

```text
TASK_ID=<task id>
CONTRACT_REVIEW=<delegation:CLEAN/PASS>
BUS_TASK_SHA256=<sha>
WORKTREE_TASK_SHA256=<same sha>
WORKTREE_HEAD=<base commit>
WORKTREE_TREE=<base tree>
TRACKED_DIFF_COUNT=0
EXPECTED_UNTRACKED=<e.g. .prismatic-task/>
EVENT_COUNT=0
CLAIM_COUNT=0
LIFECYCLE_COUNT=0
OUTBOX_COUNT=0
ACTIVE_SLOT_COUNT=0
RECOVERY_CHECKPOINT_UNCHANGED=<true|n/a>
ENVELOPE_REVIEW=<delegation:CLEAN/PASS>
NOT_CLAIMING=event, producer, implementation, canonical suite, PR, merge, deploy, cron/timer mutation, or Linear write
```

## Pitfalls

- A stale async review can be valid for an older SHA and irrelevant to the current envelope. Bind every review to exact artifact SHA and version.
- Do not reuse a dirty or previously-used worktree for a new envelope. Create the contract-declared local branch/worktree at the exact base/tree.
- If a preserved recovery checkpoint overlaps adjacent production files, prove its patch SHA and implementation blob IDs are unchanged before claiming the new envelope is isolated.
- Envelope `CLEAN/PASS` still stops before admission unless the user explicitly authorizes the exact event and cap-1 producer launch.
