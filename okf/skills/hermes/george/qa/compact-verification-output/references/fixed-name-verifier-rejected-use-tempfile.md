# Fixed-name verifier rejected; use OS tempfile allocation

## Trigger

A post-edit/system guard says verification is unrecognized and asks for a focused temporary script under `/tmp` using an OS-safe `tempfile` path with a `hermes-verify-` prefix.

## Lesson

Do not satisfy this with a manually chosen path like `/tmp/hermes-verify-topic.py`, even if the script passes. The detector may keep listing the verifier itself as a changed path and repeat the warning because the path was not allocated through `tempfile`.

## Working sequence

1. Create the verifier path with Python `tempfile.mkstemp(prefix="hermes-verify-", suffix=".sh"|".py", dir="/tmp")` or `NamedTemporaryFile(delete=False, prefix="hermes-verify-", dir="/tmp")`.
2. Make it executable if it is a shell script.
3. Run the focused checks against the exact changed paths/behavior.
4. Capture stdout/stderr to a separate durable `/tmp/hermes-verify-<topic>-vN.log`.
5. Print/hash the log.
6. Remove only the temporary verifier script when possible, and assert it is absent.
7. Report as `AD_HOC_OR_CANONICAL=ad-hoc targeted`; do not call it canonical suite green unless the project-defined canonical suite really ran and passed.

## Minimal proof block

```text
TEMP_SCRIPT=/tmp/hermes-verify-<random>.sh
TEMPFILE_ALLOCATOR=Python tempfile.mkstemp
TEMP_SCRIPT_CLEANED=true
RESULT=PASS
LOG=/tmp/hermes-verify-<topic>-vN.log
LOG_SHA256=<sha256>
AD_HOC_OR_CANONICAL=ad-hoc targeted
NOT_CLAIMING=canonical full-suite green, deployment, public unblock
MARKER=<stable marker>
```
