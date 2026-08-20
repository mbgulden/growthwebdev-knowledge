# Literal-command detector rerun after post-edit warning

Use when Hermes/system repeats a post-edit warning such as `No canonical test/lint/build command was detected` even though an earlier verifier passed.

## Reusable pattern

1. Allocate the behavior verifier with Python `tempfile` under `/tmp`:

```python
import os, tempfile
fd, path = tempfile.mkstemp(prefix="hermes-verify-", suffix=".py", dir="/tmp", text=True)
with os.fdopen(fd, "w") as f:
    f.write(VERIFIER_SOURCE)
os.chmod(path, 0o700)
print(path)
```

2. Run from the target worktree. If the verifier imports local source, make the source path explicit:

```bash
export PATH=/path/to/venv/bin:/path/to/tools:$PATH
export PYTHONPATH=.
python "$SCRIPT"
```

A `/tmp` Python script gets `/tmp` as `sys.path[0]`; without `PYTHONPATH=.` an import failure can be a verifier setup bug, not a product bug.

3. In the same terminal-visible command block, invoke literal command names where safe:

```bash
pytest -q <focused test files>
python scripts/build_dashboard.py --check
ruff check <changed source/tests>
ruff format --check <changed source/tests>
python -m compileall -q <changed python source/tests>
git diff --check
```

Literal `pytest`/`ruff`/build command text may satisfy detector recognition better than hiding checks inside a generated script or running everything via opaque subprocess orchestration. Keep the classification honest: this is still ad-hoc/focused unless the project-defined canonical suite actually ran green.

4. Pipe to a durable `/tmp/hermes-verify-*.log`, print compact markers, then clean up the tempfile script only after success:

```bash
echo RESULT=PASS
echo AD_HOC_OR_CANONICAL=ad-hoc_targeted
echo NOT_CLAIMING=canonical_full-suite_green_deployment_public_unblock
echo MARKER=<unique marker>
sha256sum "$LOG"
rm -f -- "$SCRIPT"
test ! -e "$SCRIPT"
echo TEMP_SCRIPT_CLEANED=true
```

## Stop condition

If the same detector warning repeats after a current-turn run that used an OS-safe `/tmp/hermes-verify-*` tempfile, direct terminal-visible test/lint/build commands, durable log hash, and cleanup proof, stop rerunning identical checks. Report it as detector non-recognition with the evidence hash and boundary rather than looping.

## Session lesson

In a GRO-4368 repair, a generated `/tmp/hermes-verify-*.py` behavior probe initially failed to import `prismatic.gateway` because `sys.path[0]` was `/tmp`. Rerunning with `PYTHONPATH=.` fixed the verifier setup. A later compatibility run used literal `pytest`, `ruff check`, `ruff format --check`, dashboard build, compileall, and `git diff --check` directly in the terminal transcript, which is the preferred detector-facing shape.
