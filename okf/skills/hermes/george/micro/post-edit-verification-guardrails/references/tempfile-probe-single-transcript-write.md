# Tempfile probe single-transcript write pattern

Use this when a post-edit detector asks for an OS-safe `/tmp/hermes-verify-*` temporary verification script and is sensitive to changed paths.

## Lesson

Creating the temp path with `tempfile.mkstemp()` and then writing it with the `write_file` tool can leave the disposable `/tmp/hermes-verify-*.py` itself in the detector's changed-path list. A follow-up guard may then claim the workspace still has an unverified changed path even after the probe was deleted.

## Preferred pattern

When normal shell tools are allowed, create, write, run, and delete the disposable probe in one `terminal` transcript. Keep the durable receipt/log as a separate `/tmp/hermes-verify-*.log` file and hash it after appending the final marker.

```bash
set -euo pipefail
cd /path/to/worktree
LOG=/tmp/hermes-verify-<topic>-guard.log
TMP=$(python3 - <<'PY'
import os, tempfile
fd, path = tempfile.mkstemp(prefix="hermes-verify-<topic>-", suffix=".py", dir="/tmp")
os.close(fd)
print(path)
PY
)
python3 - "$TMP" <<'PY'
from pathlib import Path
import sys
Path(sys.argv[1]).write_text('''
# pytest probe content here
''')
PY
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python -m pytest -p no:cacheprovider -q "$TMP" | tee "$LOG"
# Run visible direct project commands here: pytest/ruff/build/git checks.
rm -f "$TMP"
test ! -e "$TMP"
printf 'RESULT=PASS\nAD_HOC_OR_CANONICAL=ad-hoc targeted\nNOT_CLAIMING=canonical suite green\n' | tee -a "$LOG"
sha256sum "$LOG"
```

## Reporting boundary

Report this as ad-hoc targeted verification unless the repository canonical suite also ran and passed. If a subsequent guard lists an older temp path, assert `test ! -e <old path>` in the current transcript before classifying repeated warnings as detector ingestion stale.
