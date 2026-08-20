# Failed producer with RESULT.md but lint-blocked candidate

Use when an admitted cap-1 producer terminates non-successfully, leaves a `RESULT.md`, and commits a candidate that partly reproduces but fails an acceptance-quality gate such as Ruff.

## Session pattern captured

- One authorized event was admitted and consumed exactly once.
- The harness terminated with `producer_completed=false`, `exit_code=-15`, `automatic_kill=false`, `runtime_deadline=null`, `process_tree_cleanup_verified=true`, and no surviving processes.
- `RESULT.md` existed and claimed successful focused/archive verification.
- Immutable `git archive <candidate-head>` reproduction passed focused tests, compile, and `git diff --check`, but Ruff found unused imports.
- Therefore the producer remained failed and the candidate was blocked despite useful committed work.

## Required classification

```text
PRODUCER_STATUS=failed
PRODUCER_COMPLETED=false
RESULT_EXISTS=true
CANDIDATE_STATUS=blocked|review_pending
PRODUCER_RESULT_OVERCLAIMED=true when RESULT.md omits/contradicts the failing gate
```

Do not convert `RESULT_EXISTS=true` or passing focused tests into producer success. Candidate review is separate from producer completion.

## Minimal recovery workflow

1. Reconcile canonical receipts first: `harness-run.json`, `process-result.json`, spool `RESULT.md`, active-slot count, process liveness, SQLite event/claim/outbox state.
2. Preserve the signal/deadline facts exactly; use `signal_source=unknown` unless receipt evidence proves otherwise.
3. Bind the candidate to `HEAD`, tree, parent/base, and tracked status.
4. Reproduce from `git archive <candidate-head>` in a disposable directory, not from the mutable worktree.
5. Run at minimum:
   - `git diff --check <base> <head>`
   - compileall for changed packages/tests
   - focused task tests
   - Ruff check and format check for changed Python files
6. If a quality gate fails, mark candidate `BLOCKED` even when tests pass. Dispatch independent exact-head review for confirmation, but do not claim acceptance.
7. Update handoff/proof with both facts:
   - failed-producer provenance is preserved;
   - candidate salvage is possible only after a bounded repair/re-review gate.
8. Do not repost, start a second producer, mutate source, open PR, merge, deploy, or write Linear without explicit next authorization.

## Proof packet fields

```text
EVENT_COUNT=1
REPOSTED=false
CLAIM_ATTEMPT=1
PRODUCER_COMPLETED=false
EXIT_CODE=<signal/status>
AUTOMATIC_KILL=<true|false>
RUNTIME_DEADLINE=<value|null>
RESULT_EXISTS=<true|false>
RESULT_SHA256=<sha>
PROCESS_TREE_CLEANUP=<true|false>
ACTIVE_SLOT_COUNT=0
CANDIDATE_HEAD=<commit>
CANDIDATE_TREE=<tree>
LOCAL_ARCHIVE_TESTS=<pass/fail>
LOCAL_ARCHIVE_RUFF=<pass/fail>
CANDIDATE_REVIEW=<delegation|pending|clean|blocked>
NOT_CLAIMING=producer completion, candidate acceptance, PR, merge, deployment, cron/timer mutation, Linear write
```
