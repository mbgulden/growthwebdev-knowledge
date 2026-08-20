# Stale Producer Checkpoint Reconciliation

Use this when a Prismatic handoff says a producer/event is still running but live process/log/receipt evidence suggests the run is terminal, timed out, or incomplete.

## Trigger

- Handoff/status file says `running`, `in_progress`, or equivalent.
- Original producer PID is gone, `RESULT.md` or terminal receipt is absent, or stderr/logs show a timeout.
- The worktree contains dirty candidate edits from the producer.

## Rule

Do not treat dirty worktree edits as producer success, and do not repost/relaunch to paper over a stale checkpoint. First reconcile durable event/claim/run truth.

## Required sequence

1. Compare the handoff claim with live process state, producer logs, durable event/claim records, receipt files, and any run ledger.
2. If no valid receipt-bound terminal result exists, classify the attempt as terminal failed/incomplete or BLOCKED. Say the previous `running` state is stale.
3. Preserve the dirty worktree and logs as evidence. Do not reset, amend, or overwrite before archiving enough state for review.
4. Reproduce the bounded candidate in an isolated exact-head/archive checkpoint if it appears useful.
5. If repair-worthy, freeze a new versioned artifact rather than reusing stale review bytes.
6. Run post-edit `/tmp/hermes-verify-*` proof and capture verbose logs to files.
7. Require fresh independent exact-hash/exact-head review. Stale async reviews do not count.
8. Stop before PR, merge, deploy/restart, cron/timer mutation, Linear mutation, event POST, producer relaunch, or cap increase unless Michael separately authorized that exact action.

## Report shape

```text
PROBLEM=handoff says running but producer evidence is terminal/stale
CHANGED=reconciled authoritative event/receipt/process/worktree state
WHY_IT_MATTERS=prevents laundering dirty edits into PASS or double-launching producers
STATE=<PASS|PARTIAL|BLOCKED with exact reason>
NEXT_MOVE=<archive/reproduce/freeze/review or ask for exact authorization>
IDS_HASHES_LOGS=<event id, run dir, pid, log paths, commit/tree/digest>
```

## Pitfalls

- Do not infer completion from uncommitted code changes.
- Do not launch a replacement producer until the stale attempt is classified and preserved.
- Do not let a handoff file remain the sole authority when live/durable evidence contradicts it.
- Do not collapse `producer timed out`, `candidate useful`, and `task accepted` into one status.
