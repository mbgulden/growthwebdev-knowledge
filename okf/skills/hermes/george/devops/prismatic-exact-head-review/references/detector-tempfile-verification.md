# Detector tempfile verification pattern

Use this reference when a Prismatic code/test/handoff edit triggers a detector warning that no canonical test/lint/build command was detected.

## Durable lesson

The detector is looking for a fresh, tool-visible verification action, not a prose explanation. A prior good log may be useful context, but after a detector warning the safest response is usually to run a new bounded proof that matches the requested shape.

## Required shape

- Create a temporary verifier under `/tmp` using Python `tempfile` with filename prefix `hermes-verify-`.
- Run it against the changed behavior and exact head.
- Run literal focused commands around it: pytest, lint, format check, compile, diff check, and exact `HEAD` / tree checks.
- Clean up the verifier and prove cleanup.
- Report the result as `ad-hoc targeted` proof, not canonical full-suite green.

## Skeleton

```bash
set -euo pipefail
WT=/path/to/worktree
BASE=<base-commit>
HEAD_EXPECTED=<head>
TREE_EXPECTED=<tree>
VERIFY=$(python3 - <<'PY'
import tempfile
f = tempfile.NamedTemporaryFile(prefix='hermes-verify-', suffix='.py', dir='/tmp', delete=False)
print(f.name)
f.close()
PY
)
LOG=/tmp/<bounded-log-name>.log
trap 'rm -f "$VERIFY"' EXIT
python3 - "$VERIFY" <<'PY'
from pathlib import Path
import sys
Path(sys.argv[1]).write_text(r'''
# import product APIs here
# assert handoff markers / exact behavior here
print("CHANGED_BEHAVIOR=PASS")
''')
PY
{
  cd "$WT"
  python -m pytest -q <focused-tests>
  python -m pytest -q <bounded-regression-tests>
  ruff check <changed-files>
  ruff format --check <changed-files>
  python -m compileall -q <changed-python-files>
  git diff --check "$BASE"..HEAD
  test "$(git rev-parse HEAD)" = "$HEAD_EXPECTED"
  test "$(git rev-parse HEAD^{tree})" = "$TREE_EXPECTED"
  test -z "$(git status --porcelain=v1 --untracked-files=no)"
  PYTHONPATH="$WT" python3 "$VERIFY"
  echo RESULT=PASS
  echo AD_HOC_OR_CANONICAL=ad-hoc targeted exact-head detector verification
  echo NOT_CLAIMING=canonical full-suite green, independent acceptance, PR, merge, deployment, or live migration
} >"$LOG" 2>&1
sha256sum "$LOG"
rm -f "$VERIFY"; trap - EXIT
test ! -e "$VERIFY"; echo TEMP_VERIFIER_REMOVED=true
```

## Sanitization pitfall

If exact handoff lines contain masked or sanitizer-sensitive substrings, a generated verifier can become syntactically invalid. Prefer safe substring assertions for the sensitive parts, e.g. assert the review id fragment, short head, and status separately. If a verifier syntax error occurs after literal product commands passed, read the log and rerun with corrected verifier syntax; do not mutate the product candidate for a verifier bug.

## Reporting block

```text
COMMAND=<tempfile verifier + focused commands>
RESULT=PASS|FAIL|BLOCKED
LOG=<path>
LOG_SHA256=<sha256>
SCOPE=<exact changed paths and head>
AD_HOC_OR_CANONICAL=ad-hoc targeted exact-head detector verification
NOT_CLAIMING=canonical full-suite green, independent acceptance, PR, merge, deployment, or live migration
MARKER=<stable marker>
```
