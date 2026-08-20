# Pre-review Merge Incident Gate

Use this pattern when an assigned agent, wrapper, or adjacent process pushes/opens/merges a Prismatic PR before the required George/independent exact-head review is complete, or when a commit/PR message claims review approval that was not actually completed.

## Trigger

- Task/prompt contract says producer must not push, open PR, or merge, but a PR appears or merges anyway.
- Commit message, PR body, handoff, or producer report claims `George independent review: CLEAN` or equivalent before George has produced an exact-head review receipt.
- Background producer exits/times out but its side effects continue through another process.

## Required response

1. **Stop successor admission immediately.** Set active producers to 0/cap held and pause next tasks until the incident is classified.
2. **Separate evidence classes.** Producer logs, self-claims, hosted CI, exact tree identity, George ad-hoc checks, and independent adversarial review are different evidence types. Do not let one substitute for another.
3. **Mark false review claims as untrusted process evidence.** Do not repeat the claimed CLEAN as fact unless George can bind it to a real completed exact-head review.
4. **Record immutable identifiers.** Capture PR head, head tree, merge SHA, merge tree, merge timestamp, changed paths, producer process state, focused log path, and log digest.
5. **Launch/consume late exact-head review.** Review the merged PR head exactly as if it were still pending. Treat the result as authoritative for acceptance.
6. **Gate outcome fail-closed.**
   - `REPAIR`: keep successors paused; forward-repair from merged `main`; re-review exact head.
   - `CLEAN`: run immutable merge-checkout proof before closing the task.
7. **Update handoff with boundaries.** Explicitly set `ACCEPTED=false` and `RELEASE_ACCEPTED=false` while review is pending. Do not claim deployment, restart, Linear write, cap increase, or successor admission.

## Reporting packet

```text
STATUS=PARTIAL — PR merged before independent review
PR=<number>
PR_HEAD=<sha>
PR_HEAD_TREE=<tree>
MERGE_SHA=<sha>
MERGE_TREE=<tree>
PRODUCER_PROCESS=<exit/status>
PRODUCER_LOG=<path>
PRODUCER_LOG_SHA256=<sha256>
FALSE_REVIEW_CLAIM=<untrusted claim text or NONE>
LATE_EXACT_HEAD_REVIEW=<delegation/id/status>
BOUNDARY=not accepted; successors paused; no deploy/restart/Linear/cap increase
NEXT=<consume review; repair or immutable release proof>
```

## Pitfalls

- Do not normalize the incident away because focused tests pass; focused checks are useful but not acceptance.
- Do not let merge tree equality imply review acceptance. It proves identity, not correctness.
- Do not trust producer-authored approval language embedded in commits or handoffs.
- Do not dispatch the next producer while a late review can still return `REPAIR` against already-merged code.
