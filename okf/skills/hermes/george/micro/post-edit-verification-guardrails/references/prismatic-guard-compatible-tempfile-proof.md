# Guard-compatible Prismatic post-edit verification pattern

This reference condenses the reusable lesson from a Prismatic session where source/test/packet bytes changed after multiple exact-byte review packets.

## What worked

- Create a random probe with `tempfile.mkstemp(prefix="hermes-verify-", suffix=".py", dir="/tmp")`.
- Put the changed behavior into a real pytest test, not a bare Python script.
- Run `pytest -q /tmp/hermes-verify-<random>.py` with `PYTHONPATH=<worktree>` when the probe imports project modules.
- Run project-focused verification commands directly in the same top-level command group:
  - `pytest -q <changed/focused tests>`
  - build/check command, e.g. dashboard generated-file check
  - `ruff check ...`
  - `ruff format --check ...`
  - `python -m compileall -q ...`
  - `git diff --check`
- Assert the final packet/manifest/source hashes after the last edit.
- Tee durable output to `/tmp/hermes-verify-<topic>.log`, hash that log, and clean the temporary probe file.

## Why it matters

Some verification guards only detect visible top-level test/lint/build invocations. A shell script that internally runs tests can be technically valid but still fail ingestion. The safer pattern is: random tempfile probe + direct `pytest` invocation + direct project commands + durable log/hash + explicit ad-hoc classification.

## Report wording

Use language like:

```text
RESULT=PASS
TEMPFILE_PYTEST=1 passed
PROJECT_FOCUSED=61 passed
BUILD_LINT_FORMAT_COMPILE_DIFF=PASS
TEMP_SCRIPT_CLEANED=true
LOG=/tmp/hermes-verify-<topic>.log
LOG_SHA256=<sha256>
AD_HOC_OR_CANONICAL=ad-hoc targeted
NOT_CLAIMING=canonical full-suite green
```

If a detector still reports `unverified` after this pattern, classify it as a guard-ingestion blocker and include the exact log/hash, but do not overclaim canonical green.
