# Repeated guard warnings: dual-path proof pattern

## Trigger

A post-edit guard repeats `No canonical test/lint/build command was detected` even after a compliant `/tmp/hermes-verify-*` tempfile verifier was created, run, logged, hashed, and removed.

This can happen when the detector recognizes direct top-level project commands more reliably than project commands executed only inside a Python verifier script, or when a previous response's proof is not associated with the final changed-path state.

## Durable lesson

On the next guard warning, do not argue from the previous receipt. Run one fresh proof that satisfies both paths in the same terminal transcript:

1. Create a new OS-safe tempfile verifier under `/tmp` with `tempfile.mkstemp(prefix="hermes-verify-", suffix=".py", dir="/tmp")`.
2. Make the tempfile assert the changed behavior and compile the changed files.
3. Run the tempfile directly and tee its output into a durable `/tmp/hermes-verify-*.log`.
4. In the same terminal command, run direct top-level project commands against the changed paths, e.g.:
   - `ruff check <changed files>`
   - `ruff format --check <changed files>`
   - focused `pytest -q <test nodes>`
5. Hash the durable log.
6. Remove only the disposable tempfile verifier.
7. Do not edit source/packet files after this proof.
8. Report it explicitly as `AD_HOC_OR_CANONICAL=ad-hoc targeted`; do not call it canonical suite green.

## Minimal shell shape

```bash
set -euo pipefail
WT=/path/to/worktree
V=/path/to/venv
P=/tmp/hermes-verify-<random>.py
L=/tmp/hermes-verify-<topic>-result.log
python3 "$P" | tee "$L"
"$V/bin/ruff" check "$WT/path/to/source.py" "$WT/path/to/test.py" | tee -a "$L"
"$V/bin/ruff" format --check "$WT/path/to/source.py" "$WT/path/to/test.py" | tee -a "$L"
"$V/bin/pytest" -q "$WT/path/to/test.py::focused_test" | tee -a "$L"
sha256sum "$L"
rm -f "$P"
echo TEMP_VERIFIER_REMOVED=true
```

## Report packet

```text
TEMPFILE_CREATED_WITH=tempfile.mkstemp
TEMPFILE_PREFIX=hermes-verify-
TEMPFILE_BEHAVIOR_CHECK=PASS
DIRECT_RUFF_CHECK=PASS
DIRECT_RUFF_FORMAT=PASS
DIRECT_FOCUSED_PYTEST=<N> passed
LOG=/tmp/hermes-verify-<topic>-result.log
LOG_SHA256=<sha256>
TEMP_VERIFIER_REMOVED=true
POST_PROOF_SOURCE_EDITS=false
AD_HOC_OR_CANONICAL=ad-hoc targeted
NOT_CLAIMING=canonical full-suite green
```

## Pitfalls

- If the tempfile internally runs `ruff`/`pytest` but the terminal command only shows `python /tmp/hermes-verify-*.py`, the detector may still say no canonical/focused command was detected.
- A repeated guard is not proof that the previous verification failed; it is a workflow signal to rerun a current-turn detector-visible proof once.
- After the dual-path proof, any source or handoff edit requires another final verifier.
