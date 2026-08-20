# Production SQLite writer fencing for Prismatic migrations

Use this when a production SQLite migration must run while Prismatic services normally write to the same DB/WAL/SHM files.

## Durable lesson

Stopping known systemd units plus `lsof`/`fuser` checks is **observational**, not exclusive. It can prove there are no handles at a moment, but it cannot prevent an unlisted/manual/cron/detached process from opening the SQLite DB after the check.

For production DB mutations, require a reviewed mandatory writer fence before any mutation.

## Acceptable fence pattern

1. Precondition the normal gateway state if rollback instructions depend on it; e.g. require the old gateway initially `active/running`, or make restoration explicitly conditional on prior-active state.
2. Stop known writer units/timers as a risk reducer, but do not treat that as the fence.
3. Snapshot exact metadata for the bus directory and DB: owner, group, mode, device, inode, link count; require DB is a regular non-symlink file with link count 1.
4. Acquire a kernel-enforced fence before freezing prestate:
   - revoke non-root traversal first, e.g. `chmod 000` on the bus directory;
   - make the bus directory root-owned and root-traversable only, e.g. `root:root` mode `0500`;
   - make the DB root-owned/writeable only by root, e.g. `root:root` mode `0600`.
5. After the fence is active, prove there are no open DB/WAL/SHM handles. This is evidence that no pre-existing writer survived the fence, not the exclusion mechanism itself.
6. Run backup/migration/proofs only through the authorized root executor and bound release venv/interpreter.
7. Hold the fence continuously through backup, migration call(s), idempotence checks, final preactivation proof, and drop-in/load verification.
8. Release the fence only at the activation boundary:
   - close root SQLite connections;
   - verify no open DB/WAL/SHM handles;
   - restore WAL/SHM metadata if present;
   - restore DB metadata;
   - restore directory metadata last;
   - immediately start the gateway and perform live proof.
9. After release, compare only the migrated/authority state that should remain invariant; allow unrelated event/log tables to advance once writers resume.

## Pitfalls

- WAL mode can create transient `-wal`/`-shm` files during read-only inspection. Snapshot/fence WAL/SHM after quiescence and treat their presence as dynamic.
- `lstat -> hash -> unlink` is not an atomic rollback proof. Prefer no-clobber higher-order override publication and avoid deletion-based rollback.
- Advisory locks only work if every writer path is proven to use the same lock. If coverage is not proven, treat the lock as insufficient.
- Do not restore/start units that were inactive before quiescence unless the contract explicitly preconditions that unit as active/running.

## Proof language

Use explicit boundaries in reports:

```text
WRITER_EXCLUSION=kernel-enforced root-only path/DB fence
OBSERVATION_ONLY=lsof/fuser/repeated projections
AUTHORIZED_WRITER=*** migration executor only
FENCE_HELD_THROUGH=backup,call1,proof,call2,final_preactivation_proof
FENCE_RELEASE=activation_boundary
NOT_CLAIMING=full DB immutability after writer resume; authority-state invariant only
```
