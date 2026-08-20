# GRO-3676 — plugin-lane tests and ad-hoc verification detector gap

Session learning from the PWP token compiler task.

## What happened

- Implementation started with coverage in `tests/test_pwp_design_tokens.py`.
- The Prismatic pre-push lane guard rejected the branch for Ned because top-level `tests/` is outside Ned's write lane.
- Coverage was moved into `plugins/pwp/tests/test_compiler_determinism.py`, which is inside the `plugins/` lane and passes the pre-push guard.
- After finalization, an external verifier still reported "No canonical test/lint/build command was detected" even though focused pytest had been run in the shell.
- On a later redispatch, the issue was already `In Review`, branch `ned/GRO-3676` was pushed, and `/home/ubuntu/work/prismatic-engine` was on another branch with unrelated dirty files. A verification-refresh pass used a clean temporary worktree for `ned/GRO-3676` rather than allowing finalize to stage the shared checkout.

## Durable pattern

For Ned implementation work under `plugins/<plugin>/...`:

1. Keep new/modified tests inside the plugin lane when possible, e.g. `plugins/pwp/tests/`, not top-level `tests/`.
2. If the post-run verifier says no canonical command was detected, create a temporary script with Python `tempfile.NamedTemporaryFile(prefix="hermes-verify-", dir="/tmp", suffix=".py", delete=False)`.
3. The verifier script should import the changed code, assert the changed behavior directly, optionally run the focused in-lane pytest file, print a clear `AD_HOC_VERIFY_OK ...` marker, and then be deleted in a `finally` block or shell cleanup.
4. Report this as **ad-hoc focused verification**, not full-suite green.
5. For redispatch/verification-refresh passes on already-pushed branches, inspect the active checkout first. If it contains unrelated changes, create a clean worktree from the task branch and run verification there:

   ```bash
   git -C /home/ubuntu/work/prismatic-engine worktree add /tmp/prismatic-groXXXX-refresh ned/GRO-XXXX
   pytest plugins/<plugin>/tests/<focused_test>.py -v --tb=short
   ```

6. If finalize is still required, point it at the clean worktree and narrow the unlock scope so it does not stage or unlock unrelated lanes:

   ```bash
   PRISMATIC_REPO_ROOT=/tmp/prismatic-groXXXX-refresh \
   FINALIZE_LOCK_FILES='plugins/<plugin>' \
   bash ~/.hermes/profiles/ned/scripts/finalize_task.sh GRO-XXXX ned/GRO-XXXX ned
   ```

7. Verify Linear state/comments after finalize because the script is intentionally best-effort and exits 0 even when substeps warn.

## Example ad-hoc verifier shape

```python
with tempfile.NamedTemporaryFile("w", prefix="hermes-verify-gro3676-", suffix=".py", dir="/tmp", delete=False) as handle:
    path = Path(handle.name)
    handle.write(script)
try:
    result = subprocess.run(["python3", str(path)], cwd=repo, text=True, capture_output=True)
finally:
    path.unlink(missing_ok=True)
```

The value is not the specific GRO issue; it is the class pattern: **lane-local plugin tests + `/tmp/hermes-verify-*` ad-hoc verifier when the canonical detector misses real evidence + clean-worktree finalization when the shared checkout is dirty**.
