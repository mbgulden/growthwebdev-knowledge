# Post-edit guard verifier: import path + escaping pitfalls — 2026-07-19

Use this when Hermes asks for a fresh `/tmp/hermes-verify-*` script after code edits and the first verifier attempt fails before real checks run.

## What happened

A generated temp verifier failed twice before producing evidence:

1. Nested Python script generation used normal triple-quoted strings, so embedded `\n` collapsed into a literal newline inside `packet_text = '\n'.join(...)`, creating a syntax error.
2. The verifier imported `prismatic.agy_completed_work` from an installed/stable checkout instead of the edited repo, because the repo root was not first in `sys.path`.

Neither failure counted as verification evidence. The valid rerun used a new temp verifier, inserted the repo root into `sys.path`, ran behavior assertions, ran py_compile/pytest/ruff, then deleted the verifier.

## Reusable pattern

```python
from pathlib import Path
import sys

ROOT = Path('/path/to/edited/repo')
sys.path.insert(0, str(ROOT))
```

When generating a Python verifier from another Python process, prefer a raw outer script string:

```python
script = r'''#!/usr/bin/env python3
packet_text = "\n".join([
    'RESULT=PASS',
    'MARKER=EXPECTED_OK',
])
'''
```

## Reporting rule

If a temp verifier has a syntax/quoting/import-path failure, do not report it as evidence. Fix the generator, create a fresh `/tmp/hermes-verify-*` script, rerun, clean it up, and report only the passing rerun as `AD_HOC_OR_CANONICAL=ad-hoc targeted`.
