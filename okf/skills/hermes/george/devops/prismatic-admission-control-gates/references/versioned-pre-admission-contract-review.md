# Versioned pre-admission contract review

Use this when a Prismatic contract/prompt is still under independent review and has not yet produced a task file, event, source mutation, PR, merge, deploy, or Linear write.

## Pattern

- Preserve every blocked contract version by immutable path and SHA-256.
- Supersede with a new version only for the minimum blocker correction.
- Record prior review IDs and blockers inside the successor artifact and in the handoff.
- Freeze each successor with SHA-256, line count, byte count, marker, and explicit zero-authority state.
- Before declaring a clean semantic contract review executable, validate any reserved future `TASK_ID`, task-copy path, idempotency preimage fields, producer identity, and payload fields against the **deployed** admission schema/policy. A semantic `CLEAN/PASS` can still be inadmissible if the execution identity cannot pass deployed schema.
- Review each successor from scratch; do not treat a clean delta as acceptance of inherited text.
- Keep exactly one active contract pointer in the handoff.

## Zero-authority assertions

```text
SOURCE_MUTATION=false
TASK_FILE_CREATED=false
EVENT_CREATED=false
PRODUCER_LAUNCHED=false
PR_OPENED=false
MERGE=false
DEPLOY=false
LINEAR_WRITE=false
```

## Review pitfalls

- A contract that forbids production access cannot also require production DB hash/stat/count proof. Split implementation verification from post-acceptance release/live proof.
- SQLite `BEGIN IMMEDIATE` exceptions have ambiguous ownership if a wrapper/fault injector executes the underlying BEGIN and then raises. Split by `conn.in_transaction` and fail closed when ownership is uncertain.
- Real-path fault wrappers are stronger than helper-only tests; require them when lifecycle behavior depends on the production decision path.
