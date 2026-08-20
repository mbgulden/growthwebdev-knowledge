# Special-file races and one-shot cleanup proof

Session-derived pattern for Prismatic health/plugin repairs where a post-edit guard requires a fresh `/tmp/hermes-verify-*` verifier after editing code.

## When to use

Use this when the changed behavior involves either:

- filesystem race safety around SQLite/state DB inspection, especially regular-file → FIFO/socket/directory/symlink swaps; or
- process-runner cleanup safety, especially timeout/output-limit/success paths that can double-clean or signal an unpinned process group.

## Probe requirements

Create the disposable verifier with an OS-safe tempfile path:

```bash
python3 -c 'import os,tempfile; fd,p=tempfile.mkstemp(prefix="hermes-verify-<task>-",suffix=".py",dir="/tmp"); os.close(fd); print(p)'
```

Prefer creating/writing/running/deleting the disposable probe inside one shell transcript. If `write_file` was used and the detector later lists the `/tmp/hermes-verify-*.py` script as a changed path, rerun with a fresh temp path and assert both fresh and stale scripts are absent before reporting.

## Behavior assertions to include

For special-file/race fixes:

- exact candidate HEAD and clean worktree;
- pre-existing FIFO is rejected without blocking;
- regular-file → FIFO race is rejected without blocking;
- descriptor-bound inspection remains no-follow and validates with `fstat()` after open, not `Path.is_file()` before open.

For one-shot cleanup fixes:

- timeout path calls process-group cleanup exactly once;
- output-limit path calls process-group cleanup exactly once;
- success-path cleanup is adversarial when descendants can outlive a successful leader;
- `ChildProcessError` / lost child ownership does not call `killpg()` on an unpinned numeric PGID.

## Direct commands in the same transcript

Append direct, top-level commands after the temp probe so the detector sees real project evidence:

```bash
set -euo pipefail
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. <venv>/bin/python -m pytest -p no:cacheprovider -q /tmp/hermes-verify-*.py <focused persistent tests> | tee "$LOG"
ruff check <changed-src> <changed-tests> | tee -a "$LOG"
ruff format --check <changed-src> <changed-tests> | tee -a "$LOG"
git archive HEAD | tar -x -C "$D"
uv build --wheel --out-dir "$D/dist" "$D" >>"$LOG" 2>&1
test -n "$(/usr/bin/find "$D/dist" -maxdepth 1 -name '*.whl' -print -quit)"
rm -f /tmp/hermes-verify-*.py
test ! -e /tmp/hermes-verify-*.py
```

## Report shape

```text
RESULT=PASS
AD_HOC_OR_CANONICAL=ad-hoc targeted
NOT_CLAIMING=canonical suite green,independent acceptance,push,PR,merge,release,or deploy
TEMP_SCRIPT_CLEANED=true
STALE_TEMP_ABSENT=true  # include when relevant
LOG=/tmp/hermes-verify-<task>.log
LOG_SHA256=<sha256>
```

Do not call this canonical-suite green unless the canonical suite actually ran and passed.
