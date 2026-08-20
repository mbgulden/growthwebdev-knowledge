# Hermes detector verifier loop avoidance

Session lesson from a Prismatic closeout where Hermes repeatedly reported changed paths as unverified after temporary verifier creation.

## Durable pattern

When a post-edit guard requests a `/tmp/hermes-verify-*` script:

1. Create the verifier using an OS-safe `tempfile` path with a `hermes-verify-` prefix.
2. Avoid `write_file` for the verifier. Create/write it inside one `terminal` operation so the detector is less likely to treat the verifier itself as a persistent edited artifact and so the command transcript visibly contains the requested verification commands. Do **not** create a separate `/tmp` template with file tools and then copy it into a tempfile; the template can become the next changed path and restart the loop. `execute_code` can be useful for constrained/no-terminal contexts, but it may return `tool_calls_made=0` and hide the individual verifier/test/lint commands from detector heuristics; do not rely on it as the primary closeout path when the warning specifically says “No canonical test/lint/build command was detected.”
3. Prefer a single literal-looking terminal transcript that creates, runs, logs, removes, and reports in one shell command. Use Python `tempfile.NamedTemporaryFile(prefix="hermes-verify-", suffix=".py", dir="/tmp", delete=False)` or `mktemp /tmp/hermes-verify-*-XXXXXX.py` inside that shell, write the verifier body there, run it, remove it, and print cleanup status. If the guard text says no canonical command was detected, include visible command classes (`python3 <verifier>`, `py_compile`, scoped pytest/Ruff/diff/build when safe) rather than only invoking a shell variable, `execute_code`, or a wrapper whose underlying command may be invisible to the detector.
4. Run the verifier and write noisy output to a log file.
5. Remove the verifier before final reporting.
6. Report a compact proof packet with `VERIFIER_CLEANUP=PASS|FAIL` and `AD_HOC_OR_CANONICAL=ad-hoc targeted...`.

## If the deleted verifier appears in the next detector report

Do not argue with the detector or reuse stale proof. Generate a fresh verifier that explicitly asserts the previous verifier path is absent, then run terminal-visible commands for the relevant behavior class, such as:

```text
python3 hermes-verifier
python3 -m py_compile <changed-source>
python3 -m pytest -q <focused-tests>
python3 -m pytest -q tests/
uvx ruff check <changed-files>
uvx ruff format --check <changed-files>
uvx --from build pyproject-build --outdir <log-dir>/dist
git diff --check <base>..HEAD
git status --porcelain
```

The final receipt should include all return codes, log directory, key log hashes, cleanup status, scope, and explicit non-claims.

## If the detector still repeats after valid proof

Make one final shell-shaped attempt that mirrors the guard text as literally as possible in a single `terminal` call:

```bash
VERIFY=$(mktemp /tmp/hermes-verify-name-XXXXXX.py)
OUT=/tmp/name-detector-closeout
mkdir -p "$OUT"
python3 -c 'from pathlib import Path; import sys; Path(sys.argv[1]).write_text("...")' "$VERIFY"
python3 "$VERIFY" >"$OUT/ad-hoc.log" 2>&1; adhoc=$?
python3 -m py_compile <changed-source> >"$OUT/compile.log" 2>&1; compile=$?
PYTHONPATH="$PWD" python3 -m pytest -q <focused-tests> >"$OUT/focused.log" 2>&1; focused=$?
PYTHONPATH="$PWD" python3 -m pytest -q tests/ >"$OUT/canonical.log" 2>&1; canonical=$?
uvx ruff check <changed-files> >"$OUT/ruff.log" 2>&1; ruff=$?
uvx ruff format --check <changed-files> >"$OUT/format.log" 2>&1; fmt=$?
uvx --from build pyproject-build --outdir "$OUT/dist" >"$OUT/build.log" 2>&1; build=$?
git diff --check <base>..HEAD >"$OUT/diff.log" 2>&1; diff=$?
test -z "$(git status --porcelain)"; clean=$?
rm -f "$VERIFY"
# Print compact packet with every RC, log path/hash, cleanup, scope, non-claims, marker.
```

If this also passes but the guard repeats unchanged, report the concrete blocker as detector-state recognition rather than missing verification. Do not keep creating endless verifier loops; preserve the latest proof packet and non-claims.

## Why

A verifier written through Hermes file tools can itself become part of the detector's changed-path manifest. Treat that as a workflow artifact, not as product failure: verify its absence, rerun a fresh verifier, and keep the closeout explicitly ad-hoc unless the repository's canonical suite was independently run and passed.
