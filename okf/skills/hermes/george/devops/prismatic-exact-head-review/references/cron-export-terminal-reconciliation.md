# CRONEXPORT Terminal Reconciliation Pattern

Use when an event-admitted producer finishes and its passive waiter, launch directory, spool result, and harness state disagree.

## Durable lesson

A passive waiter or closeout wrapper can check the wrong coordinate after the producer exits. Treat that as a verifier-coordinate problem until canonical receipts prove otherwise. The authoritative chain is:

1. Runtime launch receipt / `harness-run.json` / `process-result.json` to locate the canonical spool result.
2. Spool `RESULT.md` digest bound to the recorded producer result SHA.
3. Harness state transition to `review_pending` plus process exit code.
4. Process-tree cleanup evidence: no surviving process identities, zero active slots, zero tmux sessions.
5. Exact worktree `HEAD` and `HEAD^{tree}` named by the producer packet.
6. Clean tracked worktree status and changed-path allowlist.

Do not let an initial `RESULT.md=false` from the runtime launch directory override canonical spool coordinates. Report it as a coordinate correction, not as candidate failure, if the spool result exists and matches its receipt digest.

## Independent local reproduction pattern

For exact-head task-contract candidates, reproduce from an immutable archive instead of the shared source worktree:

```text
git -C <shared-worktree> archive <candidate-head> | tar -x -C <disposable-dir>
```

Then run the finite command set in the disposable archive and verify live runtime invariance before/after:

- task-focused tests;
- bounded regression tests for the integration surface;
- linter/formatter/compile checks;
- fixture size/secret scan and required-marker assertions;
- crontab export hash unchanged;
- spool file hash/metadata unchanged;
- installed timer/service state unchanged;
- source worktree still exact `HEAD`/tree and clean after reproduction.

If a verifier setup issue occurs, such as `python` resolving to a shim that lacks pytest, classify it as `verifier setup`, not candidate failure. Fix the verifier/tool binding, record interpreter/tool paths, and rerun the complete sequence from the beginning rather than resuming after the failed line.

## Reporting boundary

Use a packet like:

```text
RESULT=PASS|BLOCKED
LOG=<path>
LOG_SHA256=<sha256>
CANDIDATE_COMMIT=<sha>
CANDIDATE_TREE=<tree>
PRODUCER_RESULT_SHA256=<sha256>
FOCUSED_TESTS=<count passed>
BOUNDED_REGRESSION=<count passed>
ALLOWLIST_ONLY=true|false
CRONTAB_EXPORT_UNCHANGED=true|false
SPOOL_HASH_METADATA_UNCHANGED=true|false
TIMER_SERVICE_STATE_UNCHANGED=true|false
AD_HOC_OR_CANONICAL=canonical task-contract local reproduction at exact head; not project full suite
NOT_CLAIMING=independent review acceptance, PR, merge, deployment, Linear write, cron/timer mutation, or canonical full-suite green
```

A successful local reproduction authorizes only dispatching/continuing independent exact-head review. It is not acceptance, merge, deployment, or live mutation proof.