# Dispatch cursor lock-release recovery addendum

Use this reference when reviewing or repairing Prismatic dispatch-cursor/generation safety work after a candidate appears locally green but still touches cursor state, SQLite backup sets, or lock release ordering.

## Session-derived pitfall

A candidate can pass focused/idempotency/static checks and still be unsafe if cursor mutation occurs inside a context manager whose `__exit__`/lock-release failure is outside the repair recovery handler.

Observed failure class:

```text
DEFECT=CursorLock release failure bypasses repair recovery
SYMPTOM=generic OSError after cursor mutation
CURSOR_MUTATED=true
BACKUPS_RETAINED=true
EXPLICIT_RECOVERY_REQUIRED=false
VERDICT=REPAIR
```

This is not acceptable for dispatch-cursor repair semantics: post-write errors must be handled as part of the same recovery/reporting contract, not leak as generic exceptions after state mutation.

## Required review probes

When a dispatch-cursor candidate claims repair safety:

1. Inject a failure in cursor lock release/`__exit__` after cursor write.
2. Verify the failure is converted into the explicit repair recovery result/exception class expected by the contract.
3. Verify cursor state is either restored exactly or retained backups are reported explicitly as operator-actionable recovery material.
4. Verify backups are not deleted before cursor restoration and post-write recovery have completed successfully.
5. Verify final reports distinguish:
   - backup failure before cursor mutation;
   - cursor write failure;
   - post-write revalidation failure;
   - lock-release/fsync/cleanup failure after mutation.
6. Keep any SIGTERM/timeout-after-edits producer as an untrusted snapshot until this probe, canonical/focused checks, build/install proof, and fresh exact-head independent review all pass.

## Proof packet fields

```text
COMMAND=<focused pytest/adversarial verifier/canonical/build commands>
RESULT=<PASS|REPAIR|BLOCKED>
LOG=<path>
SCOPE=dispatch cursor state write, lock release, rollback/backup retention
AD_HOC_OR_CANONICAL=<ad-hoc targeted|canonical suite|package proof>
NOT_CLAIMING=<merge/deploy/live cursor mutation/cap increase>
MARKER=DISPATCH_CURSOR_LOCK_RELEASE_RECOVERY_OK
```

## Boundary

Do not treat retained backups alone as success. Retention is acceptable only when paired with explicit recovery reporting and no misleading completion marker. A generic uncaught filesystem exception after mutation is a repair blocker even if byte artifacts remain available.
