# Verification Detector Temporary Script Pattern

Use this when the workspace detector says code/files were edited but no canonical command was detected, especially when it explicitly requests a `/tmp` verifier.

## Pattern

1. Treat the detector request as a verification requirement, not as user noise.
2. Create a temporary script with Python `tempfile.mkstemp(prefix="hermes-verify-", suffix=".py", dir="/tmp")` or equivalent OS-safe tempfile API. Do not hand-roll predictable filenames.
3. Have the script assert the changed behavior and the artifact binding that matters for the slice:
   - exact `git rev-parse HEAD` and `HEAD^{tree}` when reviewing exact candidates;
   - key code guard strings or behavior-level checks;
   - regression-test presence for the fixed bypass/finding;
   - report/handoff/checkpoint/PR-body alignment when those files changed;
   - queue/deploy/admission boundaries that must remain false.
4. In the wrapper command, run any focused checks that are safe and scoped: `py_compile`, targeted `pytest`, scoped lint/format, build check, security audit, `git diff --check`, then `python "$VERIFY"`.
5. Redirect output to a stable `/tmp/...-adhoc.log`, print the log path, result, head/tree, and log sha256.
6. Remove the temporary verifier with `rm -f "$VERIFY"` when possible; report cleanup explicitly.
7. In chat, label the result `AD_HOC_OR_CANONICAL=ad-hoc targeted`. Do not call it suite green unless a canonical suite actually ran and passed.
8. If the same detector warning repeats after a successful compliant run, summarize as detector nonrecognition and cite the exact log/hash rather than rerunning indefinitely.

## Minimal shell skeleton

```bash
set -euo pipefail
WT=/path/to/worktree
VERIFY=$(python -c 'import tempfile,os; fd,p=tempfile.mkstemp(prefix="hermes-verify-",suffix=".py",dir="/tmp"); os.close(fd); print(p)')
python - "$VERIFY" <<'PY'
from pathlib import Path
import sys
Path(sys.argv[1]).write_text('''# assertions go here\nprint("HERMES_AD_HOC_VERIFIER=PASS")\n''')
PY
LOG=/tmp/george-slice-adhoc.log
{
  cd "$WT"
  python -m py_compile path/to/changed.py
  python -m pytest tests/test_changed.py -q
  git diff --check
  python "$VERIFY"
} >"$LOG" 2>&1
rm -f "$VERIFY"
printf 'RESULT=PASS\nLOG=%s\nAD_HOC_OR_CANONICAL=ad-hoc targeted\nVERIFIER_CLEANUP=PASS\n' "$LOG"
sha256sum "$LOG"
```

## Pitfalls

- Do not claim canonical verification from this pattern.
- Do not leave a predictable script path in `/tmp`.
- Do not use detector nonrecognition as the first response; first perform the requested verification once.
- Do not let report/checkpoint edits go unverified just because code tests passed.
