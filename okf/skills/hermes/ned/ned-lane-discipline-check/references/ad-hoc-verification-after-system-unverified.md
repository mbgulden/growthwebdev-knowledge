# Ad-hoc verification after Hermes reports `verification status: unverified`

When the post-turn verifier says code was edited but no canonical test/lint/build command was detected, do not argue with the detector and do not repeat a prose summary. Produce fresh evidence in the exact shape it asks for.

Validated pattern from GRO-3571 (2026-07-07):

1. Create a temporary verifier script under `/tmp` using Python `tempfile.mkstemp(prefix="hermes-verify-", suffix=".py", dir="/tmp")`.
2. The verifier should check every changed path exists and is non-empty.
3. Run the focused canonical commands inside that verifier, not just directly in the shell. For Python script changes, include:
   - targeted `pytest` for the changed test file;
   - `python3 -m ruff check <changed .py files>`;
   - `python3 -m ruff format --check <changed .py files>`.
4. Add one or two behavior probes that exercise the changed code path. Example from GRO-3571:
   - live dry-run parses `jules remote list --session` and reports candidate counts;
   - synthetic fake CLI without `remote delete` verifies the script fails closed.
5. Print compact machine-readable markers: `pytest_exit=0`, `ruff_check_exit=0`, `live_dry_run_summary=...`, `AD_HOC_VERIFICATION_OK`.
6. Remove the verifier script and print `verifier_removed=true`.
7. In the final response, label the evidence exactly as **targeted ad-hoc verification, not a full suite-green claim**.

## If the verifier warning repeats

A follow-up `verification status: unverified` can repeat even after you produced a good-looking verifier transcript if the platform did not classify the prior run as canonical. Do not argue with it and do not only summarize the previous evidence. Re-run the same pattern in a **fresh direct `terminal()` call** (not nested through `execute_code`) so the tool transcript contains an obvious shell command plus `verifier_path=/tmp/hermes-verify-...`, per-command `_exit=0` markers, `AD_HOC_VERIFICATION_OK`, and `verifier_removed=true` in one stdout stream.

When a changed path was intentionally removed as part of the fix (example: a root `RESULT.md` rejected by a lane gate and amended out), encode that as a positive assertion in the verifier rather than treating the path as a missing artifact:

```python
expected_removed = Path('/tmp/prismatic-gro3274/RESULT.md')
assert not expected_removed.exists(), 'tmp root RESULT.md should remain removed after lane-gate amend'
print('expected_removed_tmp_root_result=true')
```

This keeps the verifier aligned with the final workspace state instead of chasing a stale changed-path list.

This pattern is especially useful for cron follow-up system messages where the user is not present and the only task is to satisfy the verification gate with fresh, reproducible evidence.

## Observer/telemetry repair refinement (GRO-3617, 2026-07-08)

When the repeated `unverified` nudge lists a local issue-batch `RESULT.md` plus a temporary worktree implementation (`/tmp/prismatic-<issue>/...`), make the verifier cover both artifact evidence and changed behavior:

1. Assert every surfaced path exists and is non-empty, including the issue-batch `RESULT.md`.
2. Grep the artifact for task-specific evidence markers (PR URL, verification commands, non-backfill/non-synthesis note, acceptance result).
3. Grep implementation files for behavior markers (for dispatcher observer work: `register_proc_for_observation`, `_observer_loop`, `collector.update_agent_run`, and the `subprocess.Popen` registration site).
4. Run focused canonical commands from inside the verifier:
   - targeted pytest for the changed test file;
   - ruff check for changed Python files;
   - compileall for changed Python files.
5. Add a **narrow behavior probe** that directly exercises the repair path, not just the broad test module. For observer wiring, rerun only `test_observer_writes_end_time_to_sqlite` and assert the output contains `1 passed`.
6. If the issue’s parent acceptance depends on deploy/live traffic, re-query the live DB inside the verifier and explicitly print the current pending state (e.g. `live_acceptance_count=0`, DB summary) so the response distinguishes “implementation behavior verified” from “production acceptance not yet satisfied.” This is not a failure when the task contract says a real post-deploy cycle is required.
7. Use a fresh `/tmp/hermes-verify-*.py` for each repeated nudge and print a stable repeat marker such as `AD_HOC_VERIFICATION_OK_REPEAT`; delete it and print `verifier_removed=true`.

Do not call the result “fully verified” when live acceptance is intentionally pending. The correct wording is: **targeted ad-hoc verification passed; live acceptance remains pending pre-deploy / pre-real-cycle.**