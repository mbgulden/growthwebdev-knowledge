# Concurrency/race repair tempfile proof

Use this when a post-edit guard follows a fix to atomic file creation, descriptor ownership, lock/loser reuse, process cleanup, or other race-sensitive code.

## Pattern

1. Create the verifier path with `tempfile.mkstemp(prefix="hermes-verify-<topic>-", suffix=".py", dir="/tmp")`; close the fd.
2. Write a tiny pytest that binds the exact candidate (`git rev-parse HEAD`, and tree if useful) and asserts the worktree is clean.
3. Exercise both winner and loser paths:
   - use `ThreadPoolExecutor`/process parallelism at a high enough count to force contention;
   - repeat rounds when the defect was intermittent;
   - assert exactly one first creator/winner when applicable;
   - assert every loser returns a valid receipt/reuse result;
   - assert all digests/content identifiers match;
   - assert no `.tmp`/partial artifacts leak;
   - assert stale prior `/tmp/hermes-verify-*.py` paths are absent if a guard listed them.
4. Run the temp pytest directly at top level with `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python -m pytest -p no:cacheprovider -q /tmp/hermes-verify-*.py`.
5. In the same visible transcript, run direct focused project tests/lint/format/build commands so command detectors see real project commands rather than only script internals.
6. Remove the disposable temp pytest; keep only a `/tmp/hermes-verify-*.log` receipt and report its SHA-256.
7. Classify as `AD_HOC_OR_CANONICAL=ad-hoc targeted` unless the actual canonical suite passed.

## Proof packet fields

```text
TEMPORARY_CONCURRENCY_PROBE=<N> passed
CONCURRENT_CALLS=<threads * rounds>
WINNER_COUNT_ASSERTION=PASS
LOSER_REUSE_ASSERTION=PASS
CONTENT_DIGEST_MATCH=PASS
TEMP_LEAKS=0
STALE_TEMP_ABSENT=true
FOCUSED_PROJECT_TESTS=<N> passed
RUFF_CHECK=PASS
RUFF_FORMAT_CHECK=PASS
BUILD=PASS
WORKTREE_STATUS=clean
TEMP_SCRIPT_CLEANED=true
LOG=/tmp/hermes-verify-<topic>.log
LOG_SHA256=<sha256>
AD_HOC_OR_CANONICAL=ad-hoc targeted
NOT_CLAIMING=canonical suite green
```

## Pitfall

Do not use `write_file()` for the disposable `/tmp` pytest if the guard is already treating temp scripts as changed paths. Prefer creating, writing, running, and deleting the temp file inside one `terminal` transcript. If `write_file()` was used and the guard lists the temp path, the next proof must explicitly `test ! -e <stale path>` after cleanup.