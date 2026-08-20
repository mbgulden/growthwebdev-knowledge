# GRO-4144 ad-hoc verifier after detector prompt

## Trigger

A post-response verifier says code was edited but no fresh canonical command was detected, and asks for a temporary `/tmp/hermes-verify-*` script. This can happen even when pytest/GitHub checks were already run; satisfy the detector with a fresh focused ad-hoc verifier instead of arguing from prior suite output.

## Pattern

1. Create the verifier with an OS-safe tempfile path:

   ```python
   fd, path = tempfile.mkstemp(prefix="hermes-verify-", suffix=".py", dir="/tmp", text=True)
   os.close(fd)
   Path(path).write_text(script, encoding="utf-8")
   ```

2. Run it from the repo root with the changed package import path available.
3. Print the created path, command, exit code, assertion lines, and cleanup result.
4. Remove the temporary verifier and confirm it is absent.
5. Record the ad-hoc evidence in `/tmp/issue-batches/<ISSUE>_RESULT.md` when the task uses a local result file.

## Pitfall from GRO-4144

The first verifier can be false-red if it does not reproduce the exact race harness from the focused tests. For CursorLock, the raced-at-open public lock path requires monkeypatching `consumer.os.lstat` to raise `FileNotFoundError` for the lock path before `CursorLock.acquire()` opens the already-existing mode-0644 lock file. Simply creating a public lock and calling `acquire()` exercises the pre-existing-lock path again, not the raced-at-open path.

Durable assertion contract for this class:

- pre-existing public-mode lock is rejected in both blocking and nonblocking modes;
- raced-at-open public-mode lock is rejected via descriptor validation;
- error messages include the expected stable substring (`permissions are unsafe`);
- `_fd` remains `None` after rejection;
- lock mode/content/inode are not mutated;
- temp verifier is removed after execution.

Do not summarize this as suite green. Label it explicitly as ad-hoc detector verification.