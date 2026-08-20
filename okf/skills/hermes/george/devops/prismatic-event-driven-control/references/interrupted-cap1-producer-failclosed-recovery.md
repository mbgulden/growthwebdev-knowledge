# Interrupted cap-1 producer fail-closed recovery

Use when an admitted cap-1 Prismatic producer terminates before `RESULT.md` / candidate commit, especially after SIGTERM or stale `running` evidence.

## Durable classification

Do not infer the signal source unless there is explicit evidence. Report the conservative tuple:

```text
PRODUCER_STATUS=failed
PRODUCER_STATE=review_pending
PROCESS_EXIT=-15
SIGNAL=SIGTERM
SIGNAL_SOURCE=unknown
AUTOMATIC_KILL=<true|false from runtime evidence>
RUNTIME_DEADLINE=<deadline|null>
RESULT_MD_EXISTS=false
PRODUCER_COMPLETED=false
```

If runtime evidence says `automatic_kill=false` and deadline is null, say exactly that. Do **not** blame the Prismatic supervisor, provider, user, passive waiter, or timeout path without a receipt proving it.

## Required preservation steps

1. Read runtime manifest/process result/activity/stderr/stdout enough to classify termination and cleanup.
2. Prove whether the producer process tree is gone and whether any active slot is stale.
3. Invoke the canonical harness/status reconciliation path when it is fail-closed and releases only the exact run-bound active slot after cleanup proof.
4. Preserve the dirty worktree unchanged. Do not reset, clean, commit, or continue implementation before triage.
5. Save an operator-labeled patch checkpoint outside the worktree (include tracked diff plus important untracked implementation files) and hash it.
6. Record `EVENT_COUNT=1` / `SECOND_EVENT=false`; local wrapper failures or terminalization do not authorize repost.
7. Dispatch read-only independent triage bound to the exact run ID, base/tree, task SHA, dirty paths, and checkpoint SHA.
8. Stop at the recovery-authorization gate. Same-worktree continuation, second producer, reset/cleanup, PR, merge, deploy, cron/timer mutation, and Linear writes need separate authorization.

## Compact proof skeleton

```text
RESULT=BLOCKED
PRODUCER_STATUS=failed
PRODUCER_STATE=review_pending
EXIT=<exit code>
SIGTERM_SOURCE=unknown
AUTOMATIC_KILL=<true|false>
RUNTIME_DEADLINE=<deadline|null>
PROCESS_TREE_CLEANUP=<true|false>
RESULT_MD=false
COMMITS_FROM_BASE=0
WORKTREE_DIRTY_PRESERVED=true
ACTIVE_SLOT_COUNT=0
EVENT_COUNT=1
SECOND_EVENT=false
CHECKPOINT_SHA256=<sha256>
TRIAGE=<delegation id>:pending|done
AD_HOC_OR_CANONICAL=ad-hoc targeted fail-closed terminal checkpoint
NOT_CLAIMING=implementation correctness, salvageability, producer completion, candidate commit, tests, acceptance, PR, merge, deployment, cron/timer mutation, Linear write, or known signal source
MARKER=<TASK>_INTERRUPTED_FAILED_PRESERVED_OK
```

## Pitfalls

- A process notification that says completed normally for a passive watcher can coexist with a failed producer; verify the producer's own process result.
- A stale `harness-run.json` `running` field is not authoritative after `process-result.json` exists. Use the harness reconciliation/status path if available.
- Releasing a cap slot is cleanup, not implementation progress. It must be exact-run-bound and after process-tree cleanup proof.
- A useful partial diff is not a candidate. It needs triage, completion, tests, commit/tree binding, and independent exact-head review before any acceptance claim.
