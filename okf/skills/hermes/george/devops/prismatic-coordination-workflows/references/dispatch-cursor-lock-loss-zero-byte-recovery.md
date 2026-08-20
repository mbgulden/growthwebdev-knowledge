# Dispatch cursor lock-loss and zero-byte recovery addendum

Use this reference when reviewing or repairing Prismatic dispatch cursor/generation code that mutates cursor state under `CursorLock`, especially after post-write failures or release/unlock/close exceptions.

## Session-derived failure pattern

A candidate can pass focused/canonical/static/build proof and still be unsafe if recovery runs after lock ownership has already been lost:

- `CursorLock.release()` may perform the real `LOCK_UN` or close the fd, then raise.
- If rollback restores old cursor bytes after that point without reacquiring the same strict cursor lock, a later writer can acquire the lock and commit a valid advancement.
- The rollback can then overwrite the later serialized writer and falsely report exact restoration.

Another subtle defect: treating prior cursor existence as `exists && size > 0` deletes a valid existing zero-byte cursor during rollback. Existence and contents are separate facts.

## Required implementation rules

1. **No unlocked rollback.** After release/unlock/close failure, assume lock ownership is absent or uncertain. Do not restore cursor bytes until a new strict `CursorLock` is acquired.
2. **Use nonblocking reacquire when ownership is uncertain.** If a release failure might mean the original fd is still locked, rollback recovery must not block forever trying to reacquire a lock it still owns. Use a nonblocking reacquire/try-lock path and fail closed promptly when lock state is uncertain.
3. **Distinguish close-before-effect from close-then-error.** A mocked or real `os.close()` can raise before the fd is closed, or after the fd is closed. Probe/record closure state (for example by checking `EBADF` on the fd) before deciding whether rollback may safely reacquire and compare. Do not infer unlock from “close was called.”
4. **Compare before restore.** After reacquiring, compare the current cursor state with the exact bytes/hash this operation wrote. Restore prior state only if current still equals this operation's output.
5. **Preserve later writers.** If current cursor differs after reacquire, treat it as a later serialized writer. Do not overwrite it. Retain verified backups and emit explicit recovery/fail-closed detail.
6. **Fail closed if reacquire/compare is unsafe.** If the lock cannot be reacquired without blocking, current output cannot be verified, or fd closure state is unknown, mutate nothing further and report `RECOVERY_REQUIRED` with precomputed safe metadata/backups.
7. **Zero-byte cursor is real state.** Capture `prior_existed=True` and `prior_bytes=b""` for an existing valid regular `0600` zero-byte cursor. Backup, rollback, and dry-run plans must preserve exact existence plus bytes, not delete it.
8. **Snapshot setup is protected.** Put all post-lock-acquire stat/read/snapshot setup inside protected `try/finally` release handling. Do not swallow `getsize`, `stat/lstat`, or read failures and reinterpret an unreadable existing cursor as absent.
9. **Primary plus release failures are structured.** If body and release both fail, preserve the primary mutation/snapshot error and include release failure detail via structured chaining/`ExceptionGroup` rather than a generic post-mutation error.

## Mandatory adversarial probes

Run these against each mutation API (`repair_apply`, `set_state`, and `write_cursor_state`) when applicable:

1. **Real-unlock contender race:** monkeypatch/inject release so it performs the real unlock/close, coordinates a separate thread or process that acquires `CursorLock` and writes a distinct valid cursor, then raises. Assert recovery never overwrites the contender output.
2. **Close-before-effect liveness:** inject close/release failure before the fd is actually closed while the original lock remains held. Assert rollback recovery returns promptly, mutates nothing, and reports fail-closed/recovery-required rather than deadlocking in a blocking reacquire.
3. **Close-then-error ownership proof:** inject a close that really closes the fd and then raises. Assert implementation proves closure (for example `EBADF` on that fd) before setting any “released/closed” marker used by recovery; release error must still surface structurally.
4. **Zero-byte prior cursor:** start with an existing regular `0600` zero-byte cursor and inject post-write release failure. With no contender, rollback must restore the file as existing `b""` with safe mode and durable parent fsync.
5. **Backup planning for empty cursor:** dry-run/apply must include the zero-byte cursor as an explicit backup member with size `0` and the exact SHA-256 for empty bytes.
6. **Snapshot failures after acquire:** inject `getsize`, `lstat/stat`, and prior-read failures after lock acquisition. Assert no cursor mutation occurs, lock can immediately be acquired by a separate process, and body+release failures are structured.
7. **Harness recursion guard:** if the contender is triggered from a monkeypatched release path, disarm the trigger before the contender performs its own lock release; otherwise the test recursively spawns contenders and can hang, hiding the product verdict.
8. **Boundary preservation:** keep prior WAL/process/generation/symlink/fsync/cleanup/package regressions in the focused suite; local green proof is not promotion without fresh independent exact-head review.

## Proof packet fields

```text
HEAD=<exact candidate sha>
TREE=<exact tree sha>
REAL_UNLOCK_CONTENDER=<PASS|FAIL> LOG=<path> SHA256=<digest>
ZERO_BYTE_CURSOR_RESTORE=<PASS|FAIL> LOG=<path> SHA256=<digest>
SNAPSHOT_FAILURE_FAIL_CLOSED=<PASS|FAIL> LOG=<path> SHA256=<digest>
AD_HOC_OR_CANONICAL=<ad-hoc targeted|canonical suite>
NOT_CLAIMING=<no merge/deploy/live cursor mutation/cap increase>
```
