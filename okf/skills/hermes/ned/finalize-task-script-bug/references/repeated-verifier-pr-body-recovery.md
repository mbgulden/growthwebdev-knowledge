# Repeated verifier prompt with PR-body + temp-worktree changed paths

Use this when the post-turn verifier repeats `Verification status: unverified` after a task has already been finalized/pushed/PR-created, and the surfaced changed paths include a mix of:

- `/tmp/<issue>-pr-body.md` or other PR-body/evidence artifacts
- a temporary worktree path such as `/tmp/prismatic-<issue>/...`
- committed source/backend/test/report files

## Required response pattern

1. Create a brand-new temporary Python verifier with `tempfile.mkstemp()` or `NamedTemporaryFile()` under `/tmp`, with prefix `hermes-verify-` and suffix `.py`.
2. The verifier must explicitly cover **every path listed in the repeated prompt**, not just the durable committed files.
3. For a PR-body artifact, assert it exists and contains the exact review/verification needles, e.g. `Self-Review PASSED`, PR/branch context, `npm run build`, and the targeted pytest command.
4. For UI source files, assert the visible-control needles and behavior wiring are present (for recovery controls: `Recovery Controls`, `Restart`, `Retry`, `Replay`, `runRecoveryControl`, endpoint path, visible success/status copy).
5. For backend files, assert the route/handler/state-file needles (for recovery controls: `_RECOVERY_CONTROL_ACTIONS`, `dashboard_recovery_control`, `dashboard_recovery_controls.json`, `response_model=None`, event name prefix).
6. For tests, assert both success-path and rejection-path test functions plus key action names.
7. For reports, assert issue ID, evidence strings, and the ad-hoc-verifier proof string if the report claims it.
8. Re-run the smallest targeted behavior command inside the verifier when possible (for GRO-3529 shape: `python3 -m pytest prismatic/tests/test_gateway_recovery_controls.py -q`). Do not label this a full suite unless it is one.
9. Assert `git show --name-only --format=%H%n%s HEAD` contains the expected commit subject and deliverable paths; assert `git status --short` is clean; assert no stale Ned locks remain if locks were involved.
10. Remove the verifier in a `finally` block and summarize the fresh `created ...`, `AD-HOC VERIFICATION PASSED ...`, `removed ...` evidence.

## Pitfalls

### Do not rely on prior verification

Do not reply that verification already happened. The platform is asking for a new ledger entry covering its exact changed-path list. Re-run a fresh verifier and keep the final answer short: ad-hoc verification, changed paths covered, targeted command result, cleanup path.

### Nested verifier-source quoting pitfall

When generating a `/tmp/hermes-verify-*.py` verifier from `execute_code`, avoid embedding a large raw triple-quoted verifier string that itself contains triple-quoted fixture/plugin source. The outer script can become syntactically invalid (`IndentationError: unexpected indent` or `SyntaxError: invalid syntax`) before the verifier even runs, especially when fixture snippets start with indented imports such as `from fastapi import APIRouter`.

Safer pattern for repeated verifier prompts:

1. Create the verifier path with `tempfile.mkstemp(prefix="hermes-verify-", suffix=".py", dir="/tmp")`.
2. Build verifier source as a `lines = []` list and append one line at a time, or keep fixture/module snippets in separate Python variables and insert them with `{snippet!r}` so Python handles escaping.
3. Write the joined source to the verifier file.
4. Run `subprocess.check_call(['python3', verifier], cwd=repo)`.
5. Remove the exact verifier path in `finally` and print both `created ...` and `removed ...`.

This pattern is especially useful when the verifier needs to create temporary plugin modules, FastAPI route fixtures, JSON bodies, markdown strings, or any source containing nested quotes/newlines. The lesson is not that the first failed verifier matters; fix the verifier generator and rerun a brand-new `hermes-verify-*` path, then summarize only the fresh passing run.
