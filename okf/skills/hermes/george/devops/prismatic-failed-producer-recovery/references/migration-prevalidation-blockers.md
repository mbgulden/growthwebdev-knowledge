# Migration pre-validation blockers in failed-producer checkpoints

## Trigger

Use this reference when a failed/terminated Prismatic producer leaves dirty checkpoint bytes that compile or pass focused tests, but implementation review finds database migration defects.

Common shape from the CRONSTATUSCORE-1 checkpoint:

- checkpoint integrity/reproduction is `CLEAN/PASS`;
- the producer still failed and is not a candidate/result;
- technical review blocks on migration behavior, not on checkpoint preservation;
- migration code validates an old schema against new DDL before the rebuild can run;
- `PRAGMA foreign_keys=OFF` is issued after a transaction has begun, so SQLite does not apply it;
- no true populated prior-version fixture proves row/FK/index/trigger preservation and rollback.

## Review discipline

1. **Separate integrity from implementation correctness**
   - Integrity review can pass: exact dirty patch, byte reproduction, compile/lint/format/focused proof.
   - Implementation review can still block: schema migration semantics, compatibility, authority, or runtime durability.
   - Report both facts explicitly; do not let one verdict overwrite the other.

2. **Classify migration blockers as repair requirements**
   - Name the precise old schema version and new schema version.
   - Identify the exact validation/rebuild ordering defect.
   - Identify transaction/foreign-key pragma ordering defects.
   - Require fixture-backed tests that start from a real old-version database, not a newly created latest-schema database.

3. **Required repair-contract content**
   - build a true prior-version SQLite fixture with representative rows;
   - assert migration preserves rows and semantic fields;
   - assert FKs, indexes, and triggers exist after migration;
   - assert rollback leaves either the original valid DB or a clearly failed, unusable DB with no partial success claim;
   - run validation after rebuild, not before, when validating the target schema;
   - set `PRAGMA foreign_keys=OFF` before `BEGIN` when a table rebuild needs it, then restore and verify after commit;
   - specify migration-owned transaction lifecycle states, including whether FK disable succeeded, whether `BEGIN` succeeded, whether the migration-owned transaction is closed, and whether a caller-supplied connection has been invalidated.

4. **Exception-path ownership requirements**
   - Reject an active caller transaction before toggling FK mode; do not steal caller commit/rollback ownership.
   - If `BEGIN IMMEDIATE` fails, do **not** call rollback: migration never acquired transaction ownership. Restore FK mode while still non-transactional and preserve the BEGIN failure as primary.
   - If `COMMIT` fails, preserve the commit error as primary and attempt rollback only if the connection still reports `in_transaction`.
   - If rollback fails or the connection remains transactional afterward, close/invalidate even caller-supplied connections before raising a stable chained error. Never return a usable connection with FK enforcement disabled or an open transaction.
   - Restore `PRAGMA foreign_keys=ON` only after transaction closure is proven; FK-restore failure is fail-closed and should invalidate the connection.
   - Do not retry `BEGIN`, `COMMIT`, `ROLLBACK`, or FK-mode transitions; tests should assert exact call counts and caller connection usability/closure.

4. **Do not relaunch to test this**
   - Migration repair remains an implementation artifact gate.
   - No second event/producer, public PR, merge, deploy, or Linear action until exact-head repair review passes and Michael authorizes the next gate.

## Proof packet addition

```text
INTEGRITY_REVIEW=<delegation>:CLEAN/PASS
TECHNICAL_REVIEW=<delegation>:BLOCKED
MIGRATION_BLOCKER=<old_version>_to_<new_version>_prevalidation_or_fk_ordering
TRUE_OLD_SCHEMA_FIXTURE=<present|missing>
ROWS_FKS_INDEXES_TRIGGERS_TESTED=<true|false>
ROLLBACK_TESTED=<true|false>
NOT_CLAIMING=implementation correctness,migration safety,candidate acceptance,producer success,event,producer,PR,merge,deploy
```

## Pitfalls

- **New-schema fixture false pass:** A test that creates the latest schema and then calls migration does not prove old-version compatibility.
- **Pre-rebuild validation deadlock:** Comparing the old table to new DDL before copying/rebuilding guarantees a fail-closed blocker; the repair must validate the old shape separately or rebuild first, then validate target shape.
- **Foreign-key pragma timing:** In SQLite, `PRAGMA foreign_keys=OFF` inside an active transaction is ineffective for that transaction. If a rebuild depends on it, set it before `BEGIN` and verify restoration afterward.
- **Rollback without ownership:** A failed `BEGIN` means the migration never owned a transaction; calling rollback there can steal or obscure caller state. Exception-path tests must separately cover BEGIN failure, COMMIT failure, rollback failure, FK-disable readback failure, and FK-restore readback failure.
- **Unsafe returned connection:** If transaction closure or FK restoration cannot be proven, close/invalidate the connection even when it was caller-supplied. A stable fail-closed error is preferable to returning a connection that might still be transactional or FK-disabled.
- **Integrity verdict overclaim:** A reproduced dirty checkpoint with focused green is still blocked if migration review finds these defects.
