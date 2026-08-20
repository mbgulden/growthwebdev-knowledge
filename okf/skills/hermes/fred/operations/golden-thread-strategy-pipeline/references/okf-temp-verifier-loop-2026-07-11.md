# OKF Artifact Verification Nudge Loop — 2026-07-11

## Context

During a Golden Thread run, Fred wrote a durable OKF artifact and then responded to a verification nudge by creating `/tmp/hermes-verify-hd-growth-okf.py` with `write_file`, running it, and removing it. Even though the script was cleaned up, the system still treated `/tmp/hermes-verify-hd-growth-okf.py` as a changed path and emitted another verification nudge.

## Durable Pattern

When a post-turn system nudge asks for a temporary verifier:

1. Create the verifier inside a single terminal command using Python `tempfile`:

   ```python
   fd, path = tempfile.mkstemp(prefix="hermes-verify-", suffix=".py", dir="/tmp", text=True)
   os.close(fd)
   Path(path).write_text(script, encoding="utf-8")
   os.chmod(path, 0o700)
   ```

2. Run the verifier in the same command.
3. Remove the verifier in the same command.
4. Print the verifier path, structured result, cleanup result, and exit code.
5. Report explicitly: this is **ad-hoc targeted verification**, not canonical suite/build green.

## Why

Using `write_file` for the temporary verifier can itself become a tracked changed path in Hermes' post-turn verification layer, causing an avoidable verification loop. A `tempfile`-created script that is run and removed in one terminal call satisfies the verification requirement without leaving a second artifact for the system to re-check.

## Minimal Shell Shape

```bash
python3 - <<'PY'
from pathlib import Path
import tempfile, subprocess, os, textwrap

script = """#!/usr/bin/env python3\n# focused checks here\n"""
fd, path = tempfile.mkstemp(prefix='hermes-verify-', suffix='.py', dir='/tmp', text=True)
os.close(fd)
Path(path).write_text(script, encoding='utf-8')
os.chmod(path, 0o700)
print(f'verifier_created={path}')
res = subprocess.run(['python3', path], text=True, capture_output=True)
print(res.stdout, end='')
if res.stderr:
    print('STDERR:', res.stderr, end='')
os.remove(path)
print(f'cleanup=removed {path}')
print(f'exit_code={res.returncode}')
raise SystemExit(res.returncode)
PY
```
