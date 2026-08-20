# Dispatch cursor/generation side-effect binding and plan-auth repair addendum

Use this addendum when reviewing or repairing `dispatch_consumer_v3`-style cursor/generation safety work after candidates already pass focused/canonical tests. It captures semantic hazards found during DISPATCH-CURSOR-GENERATION-1 Repair 4 review.

## Review triggers

Apply these probes when a candidate touches dispatch cursor state, DB generation identity, repair dry-run/apply plans, WAL/raw backups, event claiming, Linear/supervisor side effects, or vacuum/processed-ledger cleanup.

## Must-prove invariants

1. **Generation binding survives through every side effect**
   - Startup generation validation is not enough.
   - Fetch must validate expected generation in the same read connection used to select rows.
   - Claim/mark-processed must validate expected generation in the same write transaction before any mutation.
   - Revalidate expected generation and canonical DB identity immediately before Linear access and immediately before supervisor spawn.
   - Vacuum/processed-ledger deletion must validate expected generation in the same transaction before deleting.
   - A same-path DB replacement after fetch but before claim, Linear, spawn, or vacuum must fail closed with zero replacement-DB mutation and zero downstream side effect.

2. **Repair and consumer cursor writes share one serialization primitive**
   - SQLite writer locks do not serialize independent cursor-file writes.
   - Use one restrictive, no-follow, canonical cursor lock file (or equivalent shared primitive) for all cursor writes and repair apply.
   - Repair holds that lock from source/plan revalidation through backups and final durable cursor write.
   - Keep SQLite writer exclusion until the repaired cursor is durably written; do not release the DB lock before writing the cursor.
   - Separate locked public wrappers from an internal already-locked cursor writer to avoid recursive-lock deadlock.
   - Require process/concurrency proof that consumer cursor advancement cannot occur in the backup-to-repair-write window or be silently overwritten.

3. **Externally supplied repair plans are untrusted**
   - Always recompute the deterministic plan from current source state and requested target.
   - If a plan is supplied, require exact deep equality/canonical digest agreement with the recomputed plan before using any field.
   - Never trust caller-supplied plan id, cursor state, source hashes, target, or backup destinations.
   - Reject unknown/missing/tampered nested fields and destination changes before backups or cursor mutation.

4. **Durability and cleanup must fail closed**
   - Cursor writes must propagate parent-directory open/fsync/close failures; never report success after swallowed durability failure.
   - Backup/copy cleanup failures are material. If primary and cleanup failures coexist, report both safely while preserving the primary causal chain.
   - Inject file-fsync, parent-directory-fsync, cleanup-remove, cleanup-directory-fsync, and later-member backup-set failures.
   - Success requires no leaked newly-created partial temp/backup artifacts, preservation of pre-existing collision files, and no cursor mutation until all backup members are durable.

5. **Canonical UUID/timestamp envelope is strict**
   - Generation IDs must be lowercase canonical UUID v4 only.
   - Reject nil UUID, v1/v3/v5, uppercase, braces, whitespace, and noncanonical forms.
   - Use one canonical UTC timestamp envelope, e.g. `YYYY-MM-DDTHH:MM:SS[.ffffff]Z`.
   - Reject spaces, week dates, missing timezone, non-UTC offsets, offset-without-colon, excessive fractions, and alternate ISO forms.
   - Writer-generated timestamps must use the same accepted format.

## Evidence packet shape

```text
HEAD=<exact candidate sha>
TREE=<exact tree sha>
MATERIAL_PROBES=<replacement-after-fetch|claim|linear|spawn|vacuum; cursor-lock process contention; tampered plan; fsync/cleanup; strict format>
RESULT=<CLEAN|REPAIR>
LOG=<path>
AD_HOC_OR_CANONICAL=ad-hoc adversarial + focused/canonical as applicable
NOT_CLAIMING=<PR/CI/merge/deploy/live cursor repair unless separately proven>
```

## Pitfalls

- Green focused/canonical tests can still miss semantic side-effect windows.
- A read-only fetch followed by unbound write connections is not a generation gate.
- A logical SQLite backup is not byte-exact WAL rollback proof.
- A successful repair dry-run is not an authenticated apply plan.
- Broad `datetime.fromisoformat()` acceptance usually exceeds a documented canonical envelope.
