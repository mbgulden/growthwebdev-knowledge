# Hermes post-edit ad-hoc verification prompt pattern

Related Prismatic gate reference: `references/agy-completed-work-canonical-packet-gate.md` covers fail-closed canonical JSON/provenance completed-work ingestion and review adversarial cases.

Related runtime inventory reference: `references/public-safe-runtime-inventory.md` covers public-safe doctor/runtime declarations, private launcher coordinate boundaries, public-security scans, and installed-wheel probes.

Related cron authority reference: `references/cron-runtime-authority-inventory.md` covers cron/systemd runtime authority inventory, privileged crontab spool vs portable export rollback identity, referenced executable binding, blocked-head preservation, and immutable-archive repair verification.

## Trigger

When Hermes/system guard reports that code or coordination files were edited but fresh detected verification is missing, do not argue from earlier proof. Create and run a focused temporary verification script under `/tmp` using an OS-safe `tempfile` path whose basename begins with `hermes-verify-`.

## Pattern

1. Create the temporary script with Python `tempfile.mkstemp(prefix="hermes-verify-", suffix=".py", dir="/tmp")` or equivalent OS-safe tempfile API.
2. Make the script exercise the changed behavior directly, not merely import files. If the guard lists multiple changed worktrees/paths, either verify each changed behavior explicitly or state the exact subset verified. When the list spans a preserved blocked checkpoint and a repaired candidate, verify both identities/clean states and label their different boundaries: the old worktree remains a BLOCKED checkpoint; only the repaired worktree must pass the new behavior probes.
3. If a coordination/handoff file was edited after the last code proof, rerun one fresh `hermes-verify-*` script that covers both the code behavior and the handoff binding. Do not rely on the earlier code proof alone; the detector is correctly asking for evidence after the latest mutation.
4. If a detector-listed path was edited and then restored/excluded, include an explicit identity proof such as `git diff HEAD^ HEAD -- <path> == ""` or a digest comparison to the parent; do not simply omit the restored path from the verifier.
5. If the detector repeats the same warning after a successful verifier and no files changed afterward, report a detector exception with the exact log/hash/cleanup proof instead of rerunning identical checks. This is only acceptable when you can state no post-verifier mutation occurred.
6. If executing from `/tmp`, explicitly set repo import context, e.g. `PYTHONPATH=.` with `workdir` at the repo root. A temporary script outside the repo may otherwise fail to import local packages.
7. Prefer a self-contained script that runs focused probes/tests and `py_compile` for the touched Python modules when the guard only asks for ad-hoc evidence. This satisfies the post-edit guard without overclaiming canonical suite green.
8. When the guard explicitly says “run it against the changed behavior,” include direct assertions on the changed return values, not only a broad pytest invocation. Example: construct the edge-case receipt in the temp script, call the validator and merge-eligibility function, print the exact tuples/reasons, and assert the expected fail-closed result.
9. Avoid embedding secret-like literals or authorization-token-looking strings in generated verifier source. Construct redacted/high-entropy test payloads from safe fragments at runtime, and keep handoff assertions to non-sensitive key/value bindings.
10. After generating the verifier, treat script syntax/runtime failure as unverified product behavior. Read the verifier log, fix the verifier defect, and rerun; do not claim the product checks passed unless the product checks actually executed. If the failure is a stale verifier assertion (for example a placeholder or old reviewer id in a handoff readback), verify the live file binding, update the assertion to the actual non-secret value or a safe pattern, and rerun; do not classify the candidate as failed from the verifier bug alone.
11. For exact-head repair/review cycles, make the verifier prove the immutable identity before behavior assertions: `git rev-parse HEAD`, `git rev-parse HEAD^{tree}`, and `git status --porcelain --untracked-files=all == ""`. This prevents detector-facing proof from drifting away from the candidate under review.
12. Include the reviewer’s reproduced adversarial matrix directly in the temp verifier, not just the unit test file that was patched. Example: assert each known bypass/counterfeit input fails closed and the intended canonical input passes.
13. If the system detector repeats “no canonical test/lint/build command was detected” after a successful standalone script, rerun the same focused assertions through a temporary pytest file under an OS-safe `/tmp/hermes-verify-*` directory. This gives the detector a recognizable test-run signal while still reporting `AD_HOC_OR_CANONICAL=ad-hoc targeted`, not suite green.
14. Keep the pytest wrapper tiny: two or three direct tests that assert restored controls, frozen task identity, event/runtime/dashboard binding, exact changed-path scope, and handoff consistency. Do not broaden into the canonical suite unless the user/task explicitly asks for suite green.
15. Run it and capture the exact output and exit code. Preserve the log and hash, but remove the temporary test directory/template when possible; explicitly print `TEMP_ARTIFACTS_REMOVED=true` or name any remaining artifact the detector may still list.
16. Prefer creating, running, and deleting the verifier inside one shell process with `mktemp -d /tmp/hermes-verify-*` (or Python `tempfile`) rather than first writing a durable `/tmp/*template*` file. A separate `write_file` template or non-prefixed `/tmp` source can itself become a detector-listed changed path; if you must use one, delete it before the final response and verify absence. Best pattern: generate the verifier content inside the same Python/shell process that creates the `hermes-verify-` tempfile, so no extra `/tmp/gro...` source ever appears.
17. Treat detector-listed `/tmp` paths as first-class changed artifacts. Repo cleanliness (`git status`) is not enough: if a stale `/tmp/*source*` or template was listed, include an explicit `[ ! -e /tmp/... ]` / cleanup proof alongside the repo exact-head proof before finalizing.
18. If the detector specifically says “No canonical test/lint/build command was detected,” run the smallest real recognizable command that fits the edited surface when feasible (for example `python3 -m pytest -q tests/<focused_file>.py`, `python3 -m build`, and/or `git diff --check BASE HEAD`) and capture logs/hashes. Still report the result with its true scope: focused/ad-hoc test or package proof, not full suite green unless the canonical suite was actually run.
19. If the detector repeats and lists temp verifier files that were already removed, first prove absence plus the preserved log markers/hash. Do not rerun identical verification a third time unless there was a post-verifier mutation or a missing marker. Report this as detector non-recognition with `POST_VERIFIER_MUTATION=none`, `TEMP_SCRIPTS_REMOVED=true`, and the exact ad-hoc log hash.
20. If the detector repeats after a successful tempfile verifier but complains that no canonical command was detected, run at most one final fresh pass with literal, recognizable command lines for the edited surface (`python -m pytest`, `ruff check`, `ruff format --check`, `python -m compileall`, `git diff --check`, etc.) plus the same direct behavior verifier. Preserve the log/hash and then stop the loop if the head/tree/status are unchanged.
21. Report it as `AD_HOC_OR_CANONICAL=ad-hoc targeted`; do **not** convert it into canonical suite proof. Include `POST_VERIFIER_MUTATION=none` when the detector has already repeated once and you are reporting non-recognition rather than rerunning again.

## Prismatic example

For receipt lifecycle containment, probe all three boundaries:

```text
PRE_RECEIPT_COMMAND -> expected command_outside_receipt_interval
POST_RECEIPT_COMMAND -> expected command_outside_receipt_interval
CONTAINED_COMMAND -> expected eligible / no reason
```

## Pitfall

A first failed run caused by missing `PYTHONPATH` is not itself a durable environment lesson. The reusable lesson is: `/tmp/hermes-verify-*` scripts that import in-repo modules need explicit repository import context.
