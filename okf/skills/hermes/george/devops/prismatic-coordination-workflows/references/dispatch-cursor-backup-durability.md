# Dispatch cursor backup durability review addendum

Use this reference when a Prismatic dispatch-cursor/generation candidate implements repair backups, WAL rollback, cursor repair apply, or any copy-and-restore safety guarantee.

## Session-derived lesson

A candidate can pass focused tests, canonical tests, Ruff, format, WAL restore, and process-contention tests yet still be `REPAIR` if the backup copy primitive is not durable and failure-atomic. The review must inject filesystem failure modes around backup creation, not only prove happy-path bytes match.

## Required review probes

1. **Mandatory directory fsync:** Inject failure in the containing-directory `fsync()` after backup creation. The function must propagate the failure, remove the newly created destination, fsync the parent after removal, and leave source bytes unchanged. Swallowing directory `fsync()` is a durability blocker.
2. **Mandatory file fsync and partial cleanup:** Inject file `fsync()` failure after `O_CREAT|O_EXCL` destination creation. The function must propagate the original failure and leave no partial destination behind. If an outer apply layer tracks artifacts only after successful copy, the copy primitive itself must clean failed destinations.
3. **Symlink and TOCTOU boundary:** Open the source with descriptor-based no-follow behavior where available (`O_NOFOLLOW`), `fstat()` the descriptor, require a regular file, and bind/cross-check device/inode if any pre-open metadata is used. A pre-open `lstat()` followed by path-level `open()` leaves a swap boundary.
4. **Backup-set rollback failure path:** If DB backup succeeds and later WAL/cursor backup fails, `repair_apply()` must remove every newly created earlier backup member, never remove a pre-existing collision file, leave cursor bytes original, and leave DB/WAL/event state unchanged.
5. **No cursor mutation on backup failure:** Cursor repair state must not be written until every backup member is durably copied and verified.

## Minimal reproduction shape

Use a temporary fixture; do not touch live DB/cursor files.

```python
real_fsync = module.os.fsync

def dir_fsync_fail(fd):
    if stat.S_ISDIR(os.fstat(fd).st_mode):
        raise OSError("injected directory fsync failure")
    return real_fsync(fd)

module.os.fsync = dir_fsync_fail
# _copy_file_raw_atomic(src, dst) must raise and dst must not exist.

module.os.fsync = lambda fd: (_ for _ in ()).throw(OSError("injected file fsync failure"))
# _copy_file_raw_atomic(src, dst) must raise and dst must not exist.
```

## Acceptance packet

```text
COPY_SOURCE_OPEN=<descriptor no-follow + regular-file fstat proof>
FILE_FSYNC_FAILURE=<raises + no destination + source unchanged>
DIR_FSYNC_FAILURE=<raises + no destination + source unchanged>
SYMLINK_SOURCE=<rejected + no destination>
LATER_MEMBER_FAILURE=<earlier new backups cleaned + collisions preserved + cursor unchanged>
WAL_BACKUP_SET=<main|-wal|-shm policy + writer exclusion>
FOCUSED=<dispatch cursor focused tests>
CANONICAL=<canonical suite>
STATIC=<ruff check + format check>
VERDICT=<CLEAN|REPAIR|BLOCKED>
NOT_CLAIMING=<live DB/cursor mutation|dispatch resume|PR/merge/deploy|cap increase>
```
