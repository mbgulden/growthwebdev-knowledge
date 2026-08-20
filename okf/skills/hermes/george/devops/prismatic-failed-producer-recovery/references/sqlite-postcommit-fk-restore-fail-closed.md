# SQLite post-commit FK restore failure must fail closed without retry

## When this applies

Use this pattern for SQLite migration repairs that temporarily disable `PRAGMA foreign_keys`, perform a successful migration `COMMIT`, and then restore/read back FK state before returning the caller connection.

## Durable lesson

A failed FK restore/readback **after a successful commit** is not the same as a rollback-time recovery failure. The data/schema changes may already be durable, but the caller connection state is unsafe. Do not route this case through the general migration recovery handler if that handler will retry `PRAGMA foreign_keys = ON`, perform extra readbacks, or rewrap the exception as a rollback/migration failure.

## Required behavior

1. Track a dedicated post-commit restoration failure sentinel, e.g. `post_commit_restore_failed`.
2. After the real migration `COMMIT`, attempt exactly one FK restoration/readback sequence.
3. If `PRAGMA foreign_keys = ON` raises, readback raises, or readback is not `(1,)`:
   - mark the post-commit sentinel before leaving the branch;
   - close/invalidate the caller connection immediately;
   - raise a stable bounded authority error such as `foreign_keys_restore_failed`;
   - preserve the direct readback/restore exception as `__cause__` when applicable;
   - do not retry `ON`/readback in an outer recovery path.
4. In the outer/general recovery handler, check the post-commit sentinel first and re-raise the stable restoration error directly.

## Tests to require

Add adversarial tests for both post-commit restore outcomes:

- readback returns a non-enabled value after successful migration commit;
- readback itself raises after successful migration commit.

The tests should prove:

```text
MIGRATION_COMMITTED=true
CALLER_CONNECTION=closed_or_invalidated
POST_OFF_ON_ATTEMPTS=1
POST_COMMIT_READBACK_ATTEMPTS=1
GENERAL_RECOVERY_RETRY=false
STABLE_ERROR_CODE=foreign_keys_restore_failed
DIRECT_CAUSE_PRESERVED=true_when_exception_case
SUBSEQUENT_USE_FAILS=true
```

When a baseline FK enable occurs before the migration, count it separately from the post-`OFF` restoration attempt. Do not falsely classify the baseline `ON` as a retry.

## Reporting boundary

Focused tests for these cases are ad-hoc targeted verification unless the repository canonical suite also passes. If the canonical suite fails the same way as the immutable base, report `candidate-only canonical errors: none`, not canonical green.
