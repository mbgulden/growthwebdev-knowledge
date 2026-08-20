# Dispatch cursor/generation WAL repair review pattern

Use this reference when a Prismatic dispatch consumer/cursor-generation repair touches SQLite rollback, repair-target handling, cursor inspection, or long-running AGY producer recovery.

## Session-derived lessons

- Treat timeout/SIGTERM-after-edits as an **untrusted candidate snapshot**, not producer completion. Preserve exact `HEAD`, tree, allowed changed paths, file hashes, and a reconstructable binary patch before testing or repair.
- If a retained patch is captured from truncated tool output, do not rely on it. Re-create it from direct `git diff --binary` output and verify reconstruction against exact file hashes before committing a preservation snapshot.
- A candidate can be functionally green but still `REPAIR` if static formatting fails or semantic rollback proof fails. Keep focused/canonical proof separate from static and adversarial semantic proof.
- For production-like SQLite databases using WAL, byte-exact rollback proof must account for the coherent raw backup set: main DB plus any existing `-wal`/`-shm`, under writer exclusion. A logical SQLite backup that restores rows but changes the main DB hash is insufficient when the contract claims source-hash restoration.
- For dispatch cursor/generation changes, include adversarial probes for same-path DB replacement while the consumer loop is running, read-only `--inspect-cursor` behavior, deterministic `--repair-dry-run`, invalid/nonexistent repair-target rejection, and process-based generation initialization contention. Thread-only contention proof is weaker and should not satisfy process-concurrency acceptance by itself.
- For repair-backup code, inject filesystem failure modes around the copy primitive, not only happy-path WAL restore. File `fsync()` failure, parent-directory `fsync()` failure, symlink/TOCTOU source swaps, and later-member backup-set failure must propagate, remove only newly created partial artifacts, preserve pre-existing collision files, and avoid cursor mutation until all backup members are durable.
- When an AGY repair launch fails before edits because of a generic agent execution error, first prove the worktree is exact and clean, run a small authenticated AGY smoke under the documented child auth `HOME`, and only then relaunch the same exact hashed repair contract as the single replacement producer. Do not raise cap or advance to another task.
- Durable state must replace stale process bindings rather than add parallel producers. After every transition, bind process session, PID, candidate SHA/tree, repair contract hash, prior failed attempt summary, and unchanged live cursor/DB non-mutation proof.
- For live dispatch DB/cursor readbacks, do **not** freeze `max(rowid)` as an invariant when the bus can naturally grow while generic dispatch is paused. The durable invariant is usually DB identity + cursor non-mutation + cursor still ahead of the current live max + no replay/mutation side effects. If a final state verifier fails only because `max(rowid)` advanced, inspect the traceback, read current max/unprocessed counts, update the handoff read-model values, and rerun with `cursor > current_max` rather than relaunching or changing product code.
- After handoff/control-state edits made after product proof, run a final compact state verifier that binds exact candidate head/tree, clean worktree, review-pending/clean status, process binding, live cursor invariant, and non-claim markers. If it passes, stop editing proof artifacts in that turn so the final verifier remains the terminal evidence.

## Compact proof packet

```text
CANDIDATE_HEAD=<sha>
CANDIDATE_TREE=<tree>
PATCH=<path>
PATCH_SHA256=<sha256>
RECONSTRUCTION=<PASS|FAIL>
FOCUSED=<result/log>
CANONICAL=<result/log>
STATIC=<PASS|FAIL/log>
ADVERSARIAL=<same-path-replacement|read-only-inspect|dry-run-determinism|invalid-target|process-contention>
ROLLBACK_BACKUP_SET=<main|-wal|-shm + writer exclusion proof>
LIVE_DB_CURSOR_UNCHANGED=<cursor,max(rowid),db identity>
STATUS=<CLEAN|REPAIR|BLOCKED>
NOT_CLAIMING=<merge|deploy|Linear|generic dispatch|cap increase>
```
