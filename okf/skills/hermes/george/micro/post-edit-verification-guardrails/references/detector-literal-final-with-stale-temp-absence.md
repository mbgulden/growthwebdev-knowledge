# Detector-shaped literal final proof with stale-temp absence

Session pattern: a post-edit guard repeated even after valid verification and listed both a stale PR-body temp file and a stale disposable verifier as changed paths. The successful closeout was not to argue from the prior receipt, but to run one more small, detector-shaped proof and explicitly prove stale paths absent.

## Reusable recipe

1. Allocate a fresh OS-safe probe path:

   ```bash
   python3 -c 'import os,tempfile; fd,p=tempfile.mkstemp(prefix="hermes-verify-<topic>-", suffix=".py", dir="/tmp"); os.close(fd); print(p)'
   ```

2. Write a tiny pytest probe that binds:
   - exact `HEAD` and `HEAD^{tree}`;
   - `git status --porcelain=v1 == ""`;
   - any stale temp paths named by the guard are absent;
   - the changed behavior/contract still holds.

3. Run a single visible transcript from the worktree with the intended environment activated:

   ```bash
   set -euo pipefail
   source <project-venv>/bin/activate
   LOG=/tmp/hermes-verify-<topic>-final.log
   : > "$LOG"
   command -v python | tee -a "$LOG"
   command -v pytest | tee -a "$LOG"
   command -v ruff | tee -a "$LOG"
   command -v uv | tee -a "$LOG"
   PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python -m pytest -p no:cacheprovider -q /tmp/hermes-verify-<topic>-*.py | tee -a "$LOG"
   PYTHONDONTWRITEBYTECODE=1 python -m pytest -p no:cacheprovider -q <focused tests> | tee -a "$LOG"
   ruff check <changed dirs/tests> | tee -a "$LOG"
   ruff format --check <changed dirs/tests> | tee -a "$LOG"
   D=$(mktemp -d /tmp/hermes-verify-<topic>-wheel-XXXXXX)
   git archive <exact-head> | tar -x -C "$D"
   uv build --wheel --out-dir "$D/dist" "$D" >> "$LOG" 2>&1
   test -n "$(/usr/bin/find "$D/dist" -maxdepth 1 -name '*.whl' -print -quit)"
   git diff --check <base>..<head>
   test -z "$(git status --porcelain=v1)"
   rm -f /tmp/hermes-verify-<topic>-*.py
   test ! -e /tmp/hermes-verify-<topic>-*.py
   test ! -e <stale path named by guard>
   printf 'RESULT=PASS\nTEMP_SCRIPT_CLEANED=true\nSTALE_PATHS_ABSENT=true\nAD_HOC_OR_CANONICAL=ad-hoc targeted\nNOT_CLAIMING=canonical full-suite green,...\nMARKER=<marker>\n' | tee -a "$LOG"
   sha256sum "$LOG"
   ```

4. Hash the log **after** appending the final marker. If you hash before appending, recompute and report the final hash.

## Classification

This is an ad-hoc targeted guard closeout, not canonical full-suite green. It is valid for detector/guard satisfaction because it includes the OS-safe temp probe, direct top-level test/lint/build commands, exact byte/head binding, cleanup, stale-path absence, and proof-log hash.
