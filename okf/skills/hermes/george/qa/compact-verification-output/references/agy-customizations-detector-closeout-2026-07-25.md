# AGY customizations repeated detector closeout — 2026-07-25

## When to use

Use this pattern when Hermes reports edited Prismatic source/report/control paths as unverified after you already ran canonical proof and then made final proof-packet or report edits.

## Durable lesson

A final report/checkpoint edit is itself a changed artifact. Do one post-write verifier that asserts both behavior and the exact readback contents of the report/checkpoint. If the same detector warning repeats after a compliant terminal-visible rerun, rerun once more with the verifier created and removed inside the terminal command, then stop the loop as detector non-recognition unless new edits occurred.

## Minimum assertions

The `/tmp/hermes-verify-*` verifier should assert:

- exact `git rev-parse HEAD` and `HEAD^{tree}`;
- remote branch head equals local head when the PR has been pushed/rebound;
- clean worktree for the PR/worktree being reported;
- prior temporary verifier path is absent if it appeared in the detector manifest;
- packaged-resource bundle parity with the workspace source copy;
- managed lifecycle behavior, at least dry-run/no-mutation, install/status, and uninstall cleanup;
- user-facing docs/templates contain the new behavior/platform markers;
- durable report/checkpoint contains the final head/tree, log paths, log digests, non-claims, and review gate wording;
- PR body or public proof packet contains the same final evidence markers if it was edited after verification;
- every logged digest in the checkpoint/PR body matches the current bytes on disk for the referenced log files.

The same terminal transcript should also show literal command classes, not only hidden Python subprocesses:

```bash
python3 "$VERIFY"
python3 -m py_compile <changed python files/tests>
ruff check <changed python files/tests>
ruff format --check <changed python files/tests>
python3 -m pytest -q <focused tests>
python3 -m build --sdist --wheel --outdir "$BUILD_DIR"
git diff --check <base>..HEAD
```

## Cleanup and reporting

Create the verifier with Python `tempfile.mkstemp(prefix="hermes-verify-", suffix=".py", dir="/tmp")` inside the terminal command when possible. Remove both the verifier and build directory before the final packet, and report `VERIFIER_CLEANUP=PASS` and `BUILD_CLEANUP=PASS`.

Label the receipt as:

```text
AD_HOC_OR_CANONICAL=ad-hoc targeted closeout
NOT_CLAIMING=canonical suite rerun in this detector response; GitHub CI green; production/deployment; independent review completion
```

Do not call the detector rerun canonical green just because it includes focused pytest/build/lint commands. Keep the prior canonical suite result separate.
