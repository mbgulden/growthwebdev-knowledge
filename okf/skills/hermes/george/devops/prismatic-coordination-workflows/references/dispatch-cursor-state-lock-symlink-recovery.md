# Dispatch cursor state lock, symlink, and recovery addendum

Use this addendum when reviewing or repairing Prismatic dispatch cursor/generation code after a locally green candidate still receives an independent `REPAIR` verdict around cursor state durability or target validation.

## Session-derived trigger

A candidate can pass focused, canonical, Ruff/format, package build, and adversarial proof yet still be unsafe if the exact loop allows stale cursor writes or unsafe target aliasing. In the referenced session, exact head `8779db2…` was rejected by independent review for:

- `set_state()` generation validation occurring before the shared cursor lock, leaving a TOCTOU window before durable state write.
- `repair_apply()` accepting a symlinked cursor-state path after canonicalizing it, thereby mutating the symlink destination.
- Failure after cursor replacement but before completion/receipt being able to leave cursor state changed while cleanup deletes recovery backups.

## Review requirements

1. **Generation-bound critical section**
   - Acquire the restrictive no-follow cursor lock before reading/validating DB identity/generation.
   - Hold the same lock through the durable cursor write and final validation.
   - Bind validation to stable DB identity, not only generation string: compare canonical no-symlink path plus `lstat`/device/inode before and after relevant phases.
   - Revalidate immediately before and after the write. If post-write validation fails, restore exact prior cursor bytes or remove the newly created cursor before returning failure.

2. **No symlink or alias acceptance**
   - Inspect the caller-supplied state path before `resolve()`/canonicalization.
   - Reject final-component symlinks, parent-symlink aliases, non-regular existing targets, unsafe traversal, and noncanonical aliases before lock/backup/temp creation.
   - Do not transform a caller symlink into an accepted canonical target.

3. **Post-write recovery semantics**
   - Split repair into explicit phases with a `cursor_write_started`/`cursor_committed` boundary.
   - Compute fallible receipt material before cursor replacement when possible.
   - After cursor replacement may have happened, never use a broad failure handler that deletes all backups.
   - Prefer exact rollback while locks are held; if exact rollback cannot be proven, preserve verified backups and return/raise explicit recovery-required partial-state information with paths and hashes.
   - Never delete pre-existing collision files.

## Adversarial probes to add or run

- Same-path DB replacement after identity read and before lock acquisition.
- Same-path DB replacement after lock acquisition/generation read.
- Same-path DB replacement immediately after cursor write.
- Symlink final component for inspect, dry-run, apply, and direct write helpers; prove destination is untouched and no lock/backup/temp artifacts are created.
- Parent-symlink alias and noncanonical alias rejection.
- Injected failures immediately after `os.replace`, cursor parent `fsync`, post-write checksum, receipt construction, DB rollback/close, and cursor-lock release.
- Each injected failure must prove either exact original cursor restoration or retained verified backups with explicit recovery-required outcome, with DB/WAL/events/processed rows unchanged.

## Proof boundary

Local green proof is not promotion after a new repair commit. Require a fresh independent exact-head review and bind the review to the exact `HEAD` and tree. If independent review returns `REPAIR`, prior local proof and prior clean review/CI evidence are invalid for promotion until the same task is repaired and reviewed again.
