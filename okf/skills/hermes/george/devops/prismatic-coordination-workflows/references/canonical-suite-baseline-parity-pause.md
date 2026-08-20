# Canonical suite baseline-parity pause pattern

Use this when a Prismatic candidate finishes local reproduction cleanly, but the canonical full suite reports failures that may predate the candidate.

## Trigger

- A bounded canonical command (for example `python3 -m pytest -q tests`) returns nonzero.
- The failing tests appear outside the candidate's touched path/scope, or share a common audit/smoke dependency.
- You need to reach a safe pause point without overclaiming full-suite green or candidate acceptance.

## Required classification sequence

1. **Preserve the candidate suite log first.** Record command, exit status, summary line, log path, and log sha256.
2. **Extract exact failure roots, not only test names.** For coupled failures, identify the shared root (for example a public-security audit finding invoked directly and through wheel smoke).
3. **Bind candidate vs production-base bytes.** For any flagged source/test fixture, compare Git blobs between immutable production base and candidate head:
   - `git rev-parse <base>:<path>`
   - `git rev-parse <candidate>:<path>`
4. **Reproduce from a disposable immutable-base checkout/archive.** Run the focused failing tests from the base tree, with logs written outside the disposable checkout. Ensure the command actually runs with `cwd` set to the extracted base tree; a missing `cd` only proves harness error, not baseline parity.
5. **Classify narrowly.** If the same focused failures reproduce and flagged blobs match, record:
   - `BASELINE_PARITY_PASS_CANDIDATE_NOT_REGRESSED`
   - `CANONICAL_FULL_SUITE_GREEN=false`
6. **Freeze a receipt.** Include candidate head/tree, production base, candidate full-suite summary, baseline focused summary, log paths, sha256s, unchanged blob IDs, and explicit nonclaims.
7. **Update handoff/hot state.** State that exact-head review or other review gates remain pending; do not convert baseline parity into acceptance.

## Nonclaims to keep explicit

- Do **not** claim canonical full-suite green.
- Do **not** claim candidate acceptance until exact-head reviews are clean.
- Do **not** push, PR, merge, deploy, or mutate Linear from a parity finding alone.
- Do **not** hide the failures; say they are baseline-parity failures and provide the proof receipt.

## Useful proof block

```text
COMMAND=<canonical command>
RESULT=<candidate summary>
LOG=<candidate log>
LOG_SHA256=<sha256>
BASELINE=<immutable base commit>
BASELINE_FOCUSED_RESULT=<same failures|different failures|blocked>
BASELINE_LOG=<baseline log>
BASELINE_LOG_SHA256=<sha256>
FLAGGED_PATH=<path:line>
FLAGGED_BLOB_BASE=<blob>
FLAGGED_BLOB_CANDIDATE=<blob>
CLASSIFICATION=BASELINE_PARITY_PASS_CANDIDATE_NOT_REGRESSED
CANONICAL_FULL_SUITE_GREEN=false
NOT_CLAIMING=acceptance,canonical_full_suite_green,PR,push,merge,deployment,Linear_mutation
```

## Pitfall from session

A disposable `git archive` baseline run can accidentally execute from the parent directory if you forget to `cd`/set `cwd` to the extracted base. Treat `file or directory not found` or `no tests ran` as invalid baseline evidence; rerun from the base tree before classifying.
