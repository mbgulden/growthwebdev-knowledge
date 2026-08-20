# AGY producer result validation and verifier-environment hygiene

Use this when a Prismatic AGY/helper producer reports completion after an event-admitted or cap-1 run, especially when the process exited unexpectedly or a candidate must advance to review.

See also: `references/event-consumer-runtime-convergence.md` for event-driven consumer containment, strict doctor/runtime-inventory checks, installed-wheel config overrides, and fresh exact-head rereview boundaries.

## Durable lesson

A producer `PASS` is not acceptance evidence by itself. Treat it as an untrusted report until bound to immutable source state and independently verified.

## Required validation sequence

1. Capture the producer exit state and result metadata.
   - Record exit code/signal, duration, `cancel_requested`, `automatic_kill`, and runtime deadline fields when available.
   - If exit is signal/timeout/cancel, report an exception even if the result JSON says `PASS`.
2. Verify candidate materiality before review.
   - `HEAD` and tree must reflect the claimed implementation, not just an uncommitted working tree.
   - Reject undeclared untracked files such as task markers unless the frozen contract explicitly allowed them.
   - Confirm changed paths are inside the frozen task contract.
3. Do only same-task mechanical repair before immutable review.
   - Formatting-only repair is acceptable when source behavior is already green and the path is allowed.
   - Any semantic repair invalidates prior review and requires a new exact-head review.
4. Commit the verified candidate before independent review.
   - Bind review to exact commit and tree.
   - Do not let reviewers validate a mutable working tree.
5. Run scoped behavior checks first, then canonical local suite.
   - Keep verbose output in logs and report compact proof packets.

## Verifier-environment hygiene

Hermes sessions may inherit an unrelated `VIRTUAL_ENV` from the agent runtime. For Prismatic wheel/build/clean-room verification, explicitly remove interpreter-path contamination instead of trusting shell state:

```bash
env -u VIRTUAL_ENV -u PYTHONPATH <pytest-capable-python> -m pytest -q tests/
```

For installed-wheel proof:

```bash
env -u VIRTUAL_ENV -u PYTHONPATH <pytest-capable-python> -m build --wheel --outdir "$DIST"
env -u VIRTUAL_ENV -u PYTHONPATH <pytest-capable-python> -m venv --system-site-packages "$ROOT/venv"
env -u VIRTUAL_ENV -u PYTHONPATH "$ROOT/venv/bin/python" -m pip install --no-deps "$WHEEL"
```

If `/usr/bin/python3` lacks pytest/build, that is verifier setup, not product evidence. Use a pytest-capable interpreter while still unsetting `VIRTUAL_ENV` and `PYTHONPATH`, then rerun the failed slice and the canonical suite before claiming green.

## Proof packet shape

```text
COMMAND=<exact env -u VIRTUAL_ENV -u PYTHONPATH command>
RESULT=<PASS|FAIL|BLOCKED>
LOG=<path>
LOG_SHA256=<sha256>
SCOPE=<scoped/canonical/installed-wheel>
AD_HOC_OR_CANONICAL=<ad-hoc targeted|canonical suite|clean-room installed-wheel>
NOT_CLAIMING=<review/PR/merge/deploy if not done>
MARKER=<stable marker>
```
