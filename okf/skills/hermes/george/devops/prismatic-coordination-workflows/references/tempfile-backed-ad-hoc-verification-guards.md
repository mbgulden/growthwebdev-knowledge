# Tempfile-backed ad-hoc verification guards

Use this when a Prismatic post-edit/system guard says verification is unrecognized and specifically asks for a focused temporary script under `/tmp` with a `hermes-verify-` prefix.

## Durable lesson

A fixed, hand-picked path like `/tmp/hermes-verify-topic.py` can pass technically but still fail the guard's "OS-safe tempfile" requirement. Allocate the script path through the OS tempfile API, run it, preserve a separate durable log, and remove only the temporary script.

## Pattern

```python
import os
import tempfile

fd, path = tempfile.mkstemp(prefix="hermes-verify-", suffix=".sh", dir="/tmp", text=True)
with os.fdopen(fd, "w") as f:
    f.write(script_body)
os.chmod(path, 0o700)
print(path)
```

Then:

```bash
LOG=/tmp/hermes-verify-<topic>-v1.log
"$TEMP_SCRIPT" 2>&1 | tee "$LOG"
sha256sum "$LOG"
rm -f -- "$TEMP_SCRIPT"
test ! -e "$TEMP_SCRIPT"
```

## Reporting contract

Report it as targeted proof unless it truly ran the canonical suite:

```text
RESULT=PASS|FAIL|BLOCKED
LOG=/tmp/hermes-verify-<topic>-vN.log
LOG_SHA256=<sha256>
TEMP_SCRIPT=<random tempfile path>
TEMP_SCRIPT_CLEANED=true|false
AD_HOC_OR_CANONICAL=ad-hoc targeted
NOT_CLAIMING=canonical full-suite green, deployment, public unblock
MARKER=<stable marker>
```

## Pitfall

Do not delete the durable `/tmp/hermes-verify-*.log` proof. It is acceptable to delete the temporary script created only to satisfy the guard, but preserve the log and any screenshot/artifact evidence referenced by the report.
