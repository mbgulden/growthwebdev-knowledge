# Dispatch cursor descriptor/no-follow boundary addendum

Use this reference when reviewing or repairing Prismatic dispatch cursor/generation code that snapshots cursor files or coordinates cursor locks.

## Trigger

A candidate may pass focused/canonical tests but still be `REPAIR` if cursor snapshot or lock acquisition performs a path check and then reopens or mutates the path without binding the descriptor identity. Treat this as a material security/durability defect, not a coverage nit.

## Cursor snapshot rule

`_snapshot_cursor_file()`-style helpers must not do `lstat()/islink()` followed by ordinary `open(path)`. That creates a symlink/regular-file exchange window where rollback bytes, backup hashes, or repair provenance can be taken from the wrong object.

Required pattern:

1. Pre-check the path with `lstat` when present; reject symlink and non-regular objects.
2. Open with `os.open(..., O_RDONLY | O_NOFOLLOW | O_CLOEXEC where available)`.
3. `fstat()` the descriptor and require a regular, safe cursor object.
4. If a pre-open stat was retained, compare descriptor `(st_dev, st_ino)` to the pre-open object; reject identity drift.
5. Reject hard-linked cursor files by default (`st_nlink != 1`) unless a documented contract explicitly allows them.
6. Read from the exact descriptor (`os.read` loop or descriptor-bound file object), not by reopening the path.
7. Close on every path and propagate close/read errors structurally. `FileNotFoundError` is the only clean `prior_existed=False` case.

Mandatory probe: deterministically swap the cursor path to a symlink between the pre-open checks and the open. The helper must reject and must not return target bytes such as `SECRET-FOLLOWED`. Also swap to a different regular inode and require identity-mismatch rejection.

## Cursor lock object rule

`CursorLock.acquire()`-style helpers must validate a strict regular private lock object before `fchmod`, `flock`, or any mutation. Rejecting symlinks alone is insufficient.

Required pattern:

1. For existing lock paths, `lstat` before open and reject symlink, FIFO, socket, directory, device, and hard link.
2. Open with `O_RDWR | O_CREAT | O_NOFOLLOW | O_CLOEXEC`.
3. Immediately `fstat()` and require regular file, `st_nlink == 1`, owner equals effective UID, and descriptor identity matches pre-open object when it existed.
4. Only after those checks may permissions be restricted to `0600` and flock attempted.
5. If absence raced into an unsafe object at open, descriptor validation still rejects it.
6. On rejection/failure, close the fd, clear internal fd state, do not chmod/flock/mutate the unsafe target, and propagate a fail-closed error.
7. Preserve existing blocking/nonblocking semantics and release/rollback reporting.

Mandatory probes: precreate `<cursor>.lock` as FIFO, Unix socket, directory, symlink, and hard-linked regular file. Both blocking and nonblocking acquire paths must reject without chmod/flock or target mutation. Keep a valid private regular lock coordination test so the repair does not break ordinary cross-process coordination.

## Reporting boundary

If these descriptor-boundary probes are added after a producer candidate, the candidate requires a fresh exact-head review after the repair. Prior local canonical/focused green evidence remains useful history but is invalid for promotion.
