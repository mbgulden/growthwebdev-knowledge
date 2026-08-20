# Failed Producer Retry Gate

Use this reference when a supervised Prismatic producer/AGY launcher attempt reaches a terminal failed state but leaves partial work or proof behind.

## Core rule

A failed producer attempt is not automatically retryable and is never an accepted candidate. Treat it as a reconciliation gate:

1. Freeze and classify the first attempt before changing ledger state.
2. Prove no producer/child process remains alive.
3. Capture ledger state, outbox/consumer claim state, receipt fields, attempt count, child identity, exit code, and any preserved proof logs.
4. Classify partial artifacts explicitly as `PARTIAL`, `NOT_ACCEPTED`, and `NOT_CANDIDATE` unless a clean committed result with required receipts exists.
5. Repair launcher/supervisor tooling only if the failure exposed a reusable control weakness.
6. Independently review the exact revised launcher/supervisor hashes before any retry.
7. Ask Michael for explicit authorization before reconciling a failed ledger row or starting same-event attempt 2.

## Retry safety checklist

Before asking for retry authorization, verify and report:

```text
EVENT_ID=<task-admission:...>
LAUNCHER_STATE=failed|retryable_failed
ATTEMPT_COUNT=<n>
ACTIVE_PRODUCERS=0
CHILD_EXIT_CODE=<code>
LAUNCH_RECEIPT=<present|null>
CANDIDATE_SHA=<sha|null>
CANDIDATE_TREE=<tree|null>
DIRTY_PATHS=<exact scope or none>
PARTIAL_PROOF_LOG=<path>
RETRY_LAUNCHER_SHA256=<sha256>
RETRY_SUPERVISOR_SHA256=<sha256>
INDEPENDENT_REVIEW=<delegation id + CLEAN_TO_RETRY|REPAIR>
NOT_CLAIMING=retry authorization, candidate acceptance, merge, deploy, Linear mutation, or cap increase
```

## Partial proof handling

If a producer dies while spawned shell proof continues, preserve the logs but do not overclaim. The proof may be useful evidence for repair, but without the producer alive to repair lint/format/diff failures, commit, and write the required result/receipt, it is not a valid completed candidate.

## Timeout flag lesson

When AGY/CLI timeout behavior matters, prefer a single equals-form timeout argument when supported, e.g. `--print-timeout=30m`, and pair it with an outer supervisor timeout that exceeds it with a clear safety margin. Verify the literal command string and timeout values in the launcher artifact.

## Dirty worktree preflight lesson

If a retry must continue from preserved partial work, do not require a globally clean worktree if that would discard useful work. Instead, allow only an exact path allowlist tied to the task and fail closed on any unexpected porcelain path. Implement path parsing from `git status --porcelain --untracked-files=all` and review it independently.

## Reporting shape

Lead with the operational exception, then separate:

- **Attempt state** — what failed and current process/ledger state.
- **Partial artifact** — useful evidence that is not accepted.
- **Retry tooling** — exact hashes and changed controls.
- **Authorization point** — what is still not authorized.

Never mutate the failed row, retry, dispatch, merge, deploy, or update Linear while the retry review is still active.
