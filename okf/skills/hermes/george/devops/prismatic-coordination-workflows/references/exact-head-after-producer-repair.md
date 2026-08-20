# Exact-head discipline after producer repair commits

Use this when reviewing Prismatic assigned-agent/AGY/Fred/Ned results where a producer reports SUCCESS but the branch receives later repair commits.

## Durable lesson
A producer result packet is bound to the exact commit/tree it names. If any follow-up commit lands after the producer result, do **not** carry the producer PASS forward to the newer head. Treat the newer head as a repaired candidate that needs fresh exact-head verification and independent review.

## Active review sequence
1. Compare the result packet's `COMMIT`/`TREE` against the worktree's current `HEAD`/tree.
2. If they differ, state the boundary plainly: producer SUCCESS applies only to the recorded commit.
3. Inspect the commit range from the result commit/base to current head and confirm the changed paths are still within authorized scope.
4. Require a fresh frozen-head review for the current head before PR/open/merge/deploy claims.
5. Keep throughput moving by preparing the next bounded slice while the current head is reviewed, but do not admit/run the successor until the cap-1 acceptance boundary is reached.

## Proof packet fields to include
```text
RESULT_COMMIT=<commit named by producer result>
RESULT_TREE=<tree named by producer result>
CURRENT_HEAD=<current branch head>
CURRENT_TREE=<current tree>
POST_RESULT_COMMITS=<count/list or none>
CHANGED_PATHS=<path list>
BOUNDARY=producer PASS applies only to RESULT_COMMIT; CURRENT_HEAD requires fresh exact-head review
NOT_CLAIMING=merge/deploy/current-head acceptance/successor admission unless independently proven
```

## Pitfalls
- Do not call a branch accepted just because the worktree is clean and the producer exited 0.
- Do not treat post-result documentation-only repairs as exempt from exact-head proof; they can alter the reviewed contract.
- Do not rely on a stale handoff when runtime receipts, PR state, and production systemd checkout disagree. Prefer live control-plane evidence and mark the handoff stale.
