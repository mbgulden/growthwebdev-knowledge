# Post-commit outbox/report edits and repeated detector closeout

Use this when a session commits source/test changes, then edits non-repo coordination artifacts such as `prismatic-agent-bus/outbox/.../RESULT.md` or `~/.hermes/.../prismatic-reports/*.md`, and Hermes later reports those paths as still unverified.

## Durable lesson

A clean git worktree and prior suite logs are not enough after a later proof-packet/outbox edit. The closeout verifier must bind **both**:

1. the exact repository artifact (`HEAD`, `HEAD^{tree}`, clean status, relevant source/test paths); and
2. the out-of-repo coordination artifact contents (`COMMIT=...`, `TREE=...`, prior review ID/decision, active review ID, log paths/digests, markers).

If the detector repeats a warning after that, perform one current-turn rerun with a `/tmp/hermes-verify-*` script created by Python `tempfile` and literal terminal-visible command classes. After the compliant rerun is visible, do not enter an infinite loop; report detector non-recognition as the boundary.

## Minimal pattern

```bash
set -o pipefail
VERIFY=$(python - <<'PY'
import tempfile, os
fd, p = tempfile.mkstemp(prefix="hermes-verify-", suffix=".py", dir="/tmp")
os.close(fd)
print(p)
PY
)
BUILD_DIR=$(python - <<'PY'
import tempfile
print(tempfile.mkdtemp(prefix="hermes-verify-build-", dir="/tmp"))
PY
)

python - <<'PY'
from pathlib import Path
import os
Path(os.environ["VERIFY"]).write_text("""
import subprocess
from pathlib import Path
root = Path('/path/to/worktree')
def git(*args):
    return subprocess.check_output(['git', *args], cwd=root, text=True).strip()
assert git('rev-parse', 'HEAD') == '<expected_commit>'
assert git('rev-parse', 'HEAD^{tree}') == '<expected_tree>'
assert not git('status', '--porcelain')
outbox = Path('/path/to/outbox/RESULT.md').read_text()
for marker in (
    'COMMIT=<expected_commit>',
    'TREE=<expected_tree>',
    'PRIOR_REVIEW=<id> CHANGES_REQUIRED',
    'INDEPENDENT_REVIEW=<active_id>',
):
    assert marker in outbox
print('EXACT_READBACK_OK')
""")
PY

LOG=/tmp/<issue>-detector-rerun.log
{
  PYTHONPATH=. python "$VERIFY"
  ruff check <changed source/test paths>
  ruff format --check <changed source/test paths>
  python -m pytest -q <focused permanent regression tests>
  python -m build --wheel --outdir "$BUILD_DIR" .
  git diff --check HEAD^ HEAD
} >"$LOG" 2>&1
rc=$?
rm -f "$VERIFY"
rm -rf "$BUILD_DIR"
```

## Required summary language

```text
RESULT=<PASS|FAIL>
LOG=<path>
LOG_SHA256=<sha256>
TEMP_CLEANUP=<PASS|FAIL>
SCOPE=exact repair head, changed behavior, distribution/lint/build, outbox/report binding
AD_HOC_OR_CANONICAL=ad-hoc targeted closeout
NOT_CLAIMING=canonical suite, independent CLEAN, hosted CI, PR, merge, deployment, or Linear update
```

## Pitfalls

- Do not call the rerun canonical just because it includes `python -m build` or scoped `pytest`; it is a detector-visible ad-hoc closeout unless the full project-defined canonical suite ran.
- Do not answer only from an earlier receipt when the warning arrives as a fresh user/system message. Run a same-turn verifier once.
- Do not keep rerunning identical checks forever. After a compliant same-turn rerun with cleanup and digest is visible, the useful boundary is detector non-recognition.
- Do not forget out-of-repo artifacts. They are often the actual changed paths that triggered the guard after source verification was already valid.
