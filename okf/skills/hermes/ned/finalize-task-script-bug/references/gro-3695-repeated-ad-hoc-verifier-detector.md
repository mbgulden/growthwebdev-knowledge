# GRO-3695 repeated ad-hoc verifier detector loop

Date: 2026-07-09

## Context

After finishing and finalizing a plugin-lane PWP implementation, the cron detector twice returned:

> Verification status: unverified
> No canonical test/lint/build command was detected. Create a focused temporary verification script under `/tmp` using an OS-safe `tempfile` path with a `hermes-verify-` filename prefix...

The branch was already pushed and Linear was already `In Review`. Prior pytest output and a prior ad-hoc verifier were true, but the detector wanted a fresh, newly-observed `/tmp/hermes-verify-*` run for that specific prompt.

## Correct response pattern

When the repeated detector prompt appears:

1. Do **not** argue from earlier pytest/ruff output.
2. Do **not** re-finalize just to satisfy the verifier.
3. Create a fresh temp verifier using `tempfile.mkstemp(prefix="hermes-verify-", suffix=".py", dir="/tmp")`.
4. The verifier should print, at minimum:
   - `verifier_script=<path>`
   - `tested_command=<command under test>`
   - command exit code(s)
   - `assertion_summary=<behavior asserted>`
   - `verification_exit=0`
   - cleanup status for both the verifier and any temp workdir
5. Exercise changed behavior directly, not the whole suite if the detector asked for ad-hoc evidence.
6. Clean up the verifier and temp workdir when possible.
7. Summarize it explicitly as **ad-hoc targeted verification, not suite green**.
8. If the issue is already `In Review`, post a Linear verification-refresh comment with the fresh ad-hoc evidence; no state transition is needed.

## Minimal shell/Python wrapper shape

```bash
cd /tmp/prismatic-gro3695 && python3 - <<'PY'
from pathlib import Path
import os, sys, tempfile, subprocess

repo = Path('/tmp/prismatic-gro3695')
fd, verifier = tempfile.mkstemp(prefix='hermes-verify-', suffix='.py', dir='/tmp')
os.close(fd)
Path(verifier).write_text('''
from pathlib import Path
print(f"verifier_script={Path(__file__).resolve()}")
print("tested_command=<exact changed behavior command>")
# run command, assert changed behavior, clean temp workdir
print("assertion_summary=<what passed>")
print("verification_exit=0")
''')
try:
    res = subprocess.run([sys.executable, verifier], cwd=repo, text=True, capture_output=True, check=False)
    print(res.stdout, end='')
    if res.stderr:
        print(res.stderr, end='', file=sys.stderr)
    print(f'runner_exit={res.returncode}')
finally:
    try:
        Path(verifier).unlink()
        print(f'verifier_cleanup=True path={verifier}')
    except Exception as exc:
        print(f'verifier_cleanup=False path={verifier} error={exc}')
sys.exit(res.returncode)
PY
```

## GRO-3695 concrete assertion

For `scripts/pwp theme install`, the useful focused assertions were:

- install command exits `0` for the valid theme fixture,
- JSON payload has `ok: true`, `themeId: pwp.theme.trust-light`, and requested tenant,
- expected tenant-scoped PWP/Astro files exist under the temp target,
- install manifest includes `sha256:` token/module/content-schema hashes,
- second install without `--force` exits `1` and includes `Refusing to overwrite`.
