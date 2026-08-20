# Repeated detector warning: exact `tempfile` compliance after post-edit proof artifacts

## Trigger

Hermes/user repeats a post-edit guard warning after source and out-of-repo proof-packet edits, especially wording like:

```text
No canonical test/lint/build command was detected. Create a focused temporary verification script under /tmp using an OS-safe tempfile path with a hermes-verify- filename prefix...
```

## Lesson

Do not answer from the previous receipt, and do not use shell `mktemp` when the warning explicitly asks for an OS-safe `tempfile` path. Run one fresh same-turn verifier whose transcript visibly shows Python `tempfile.NamedTemporaryFile(...)` or `tempfile.mkstemp(...)` creating `/tmp/hermes-verify-*.py`, then compile/run/cleanup that exact file.

If the changed path list includes both git-tracked source and out-of-repo receipts/handoff Markdown, verify both classes in the same verifier/readback cycle:

- exact repo `HEAD` and tree;
- clean worktree and exact changed source path from base;
- `git diff --check <base> HEAD`;
- changed behavior markers in the contract/source;
- receipt/handoff artifact exists and contains candidate commit/tree, non-claims, review gate, log path/digest, and marker;
- verifier cleanup status.

## Minimal detector-visible shape

```bash
python3 - <<'PY'
import tempfile, pathlib, textwrap
with tempfile.NamedTemporaryFile('w', prefix='hermes-verify-', suffix='.py', dir='/tmp', delete=False) as f:
    verify = f.name
    f.write(textwrap.dedent('''
        from pathlib import Path
        import subprocess
        # exact assertions here
        print("AD_HOC_VERIFICATION=PASS")
    '''))
print(f"TEMPFILE={verify}")
PY
python3 -m py_compile "$VERIFY"
python3 "$VERIFY"
rm -f "$VERIFY"
printf 'TEMPFILE_CLEANED=%s\n' "$([ ! -e "$VERIFY" ] && echo true || echo false)"
```

Adapt the wrapper so the `VERIFY` variable is exported from the Python creation step, or create the file with a small Python command that prints the path into a shell variable. Keep `python3 -m py_compile`, `python3 "$VERIFY"`, `git diff --check`, and the cleanup line terminal-visible. Label the result `AD_HOC_OR_CANONICAL=ad-hoc targeted`, never suite green.

## Stop condition

After a current-turn transcript visibly satisfies the exact tempfile/prefix/compile/run/cleanup requirements and asserts every named changed path class, repeated identical warnings can be reported as detector non-recognition. Before that point, rerun once rather than arguing from the prior log.
