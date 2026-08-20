# Repeated guard warnings: worktree `python -m pytest` detector path

Use when a post-edit guard keeps repeating `No canonical test/lint/build command was detected` after you already ran an OS-safe `/tmp/hermes-verify-*` probe and direct tool commands.

## Pattern

1. Do not argue from old receipts. Run one fresh current-turn verifier.
2. Create the disposable probe with `tempfile.mkstemp(prefix="hermes-verify-", dir="/tmp")` and keep the proof log under `/tmp/hermes-verify-*`.
3. From the edited worktree, invoke commands in a detector-friendly shape:

```bash
python3 /tmp/hermes-verify-<random>.py | tee "$LOG"
/path/to/venv/bin/ruff check <changed paths> | tee -a "$LOG"
/path/to/venv/bin/ruff format --check <changed paths> | tee -a "$LOG"
/path/to/venv/bin/python -m pytest -q <focused test path or nodes> | tee -a "$LOG"
sha256sum "$LOG"
rm -f /tmp/hermes-verify-<random>.py
```

4. State `AD_HOC_OR_CANONICAL=ad-hoc targeted` unless the repository-wide canonical suite also passed.
5. Do not edit source, tests, or handoff after the verifier. If you must edit afterward, rerun the proof.
6. If the same guard repeats again after this visible current-turn run, treat it as detector/ingestion stale. Report the fresh log path/hash and do not keep running infinite duplicate verifiers unless the user asks.

## Why this matters

Some guards recognize a top-level `python -m pytest` command from the worktree more reliably than a script-internal pytest or an absolute `pytest` executable. Pairing the tempfile probe with direct worktree `python -m pytest` satisfies both the behavior-probe requirement and the command-shape detector.
