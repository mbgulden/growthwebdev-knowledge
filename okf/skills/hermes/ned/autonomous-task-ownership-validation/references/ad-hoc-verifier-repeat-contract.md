# Ad-hoc verifier repeat contract

When the system says `Verification status: unverified` after a code-editing turn, do not argue from prior pytest/ruff output or a previous ad-hoc verifier. The detector is asking for fresh evidence in the current turn shape.

Required response pattern:

1. Create a temporary verifier with Python `tempfile.mkstemp(prefix="hermes-verify-", suffix=".py", dir="/tmp")`.
2. Write direct assertions against the changed behavior, not a broad suite wrapper.
3. Run it from the repository root and print:
   - `created_verifier=<path>`
   - `exit_code=<code>`
   - stdout/stderr, if any
   - cleanup status
4. Delete the verifier in a `finally` block when possible.
5. Summarize as **ad-hoc targeted verification**, not full suite green.
6. If the same verifier prompt repeats, run a fresh verifier again with a new `/tmp/hermes-verify-*` path. Prior evidence may be human-readable but is not enough for the detector.

Useful skeleton:

```python
from __future__ import annotations
import os, subprocess, sys, tempfile
from pathlib import Path

repo = Path('/home/ubuntu/work/prismatic-engine')
fd, verifier_name = tempfile.mkstemp(prefix='hermes-verify-', suffix='.py', dir='/tmp')
os.close(fd)
verifier = Path(verifier_name)
verifier.write_text('''\
# direct assertions for the changed behavior go here
print('ad-hoc verifier assertions passed')
''')
print(f'created_verifier={verifier}')
try:
    proc = subprocess.run([sys.executable, str(verifier)], cwd=repo, text=True, capture_output=True, timeout=30)
    print(f'exit_code={proc.returncode}')
    if proc.stdout:
        print('stdout:')
        print(proc.stdout.rstrip())
    if proc.stderr:
        print('stderr:')
        print(proc.stderr.rstrip())
    raise SystemExit(proc.returncode)
finally:
    try:
        verifier.unlink()
        print(f'cleanup=deleted {verifier}')
    except FileNotFoundError:
        print(f'cleanup=already_missing {verifier}')
    except Exception as exc:
        print(f'cleanup=failed {verifier}: {exc}')
```
