# Executable Linear Packet Writer Pattern

Use this when Michael approves a frozen Prismatic planning/executable Linear packet and asks George to prepare or execute the exact mutation packet.

For bounded retries after a failed/rolled-back packet, use `references/linear-recovery-execution-retry.md` in addition to this reference; recovery retry writers require a separate exact SHA, recovery-only authority, hash-bound baselines/source receipts, and fresh CLEAN review before any live mutation.

## Durable pattern

1. **Freeze and bind artifacts first**
   - Record exact SHA256 for the approved bundle and each component/export/guard file.
   - Writer scripts must verify every frozen artifact hash and restrictive file mode before any Linear call that can mutate.
   - Bind execution authority explicitly: writer, mode, approved bundle SHA, rollback flags, and non-authorized operations.

2. **Default to read-only dry-run**
   - The executable must default to dry-run and require an explicit `--execute` plus exact authorization flags for mutation.
   - Dry-run must run the same parsing, hash, guard, duplicate, relation-baseline, pagination, and state preflight checks as execution.
   - Report `LINEAR_MUTATED=false` only when the script itself proves no mutation path was entered.

3. **Use live guards, not stale packet trust**
   - Re-read all guarded Linear issues immediately before execution.
   - Verify immutable identity, team, `updatedAt`, title hash, description hash, labels, state, parent, assignee/project, comments/children pagination, and exact zero baseline relations where required.
   - Include any out-of-packet issue whose embedded projection can change because of the packet, even when that issue is not itself being edited (for example, a parent whose child list will change). Treat those as read-only tracked projection guards.
   - Fail closed on any drift instead of trying to adapt the packet mid-execution.

4. **Model Linear projection side effects**
   - A child title/description update changes the parent issue's embedded child projection.
   - A parent title update changes each child's embedded parent-title projection.
   - Reparenting changes both old and new parent child sets, including out-of-packet parents that are only touched through projections.
   - The writer should update its in-memory expected snapshots and verify these projections after each mutation, otherwise later evolving-state checks can falsely fail after legitimate writes.
   - Treat Linear Markdown as a canonicalized storage format in postconditions: prove expected descriptions through live-stored/canonical equivalence where Linear rewrites harmless Markdown markers (for example `-` list bullets to `*`) and may insert a blank line before the first contiguous list after a non-list paragraph/header. Use `references/linear-markdown-canonicalization.md` for the exact modeling pattern; do not loosen comparisons beyond known canonicalization.
   - If Linear has already proven it rewrites the raw Markdown form during an authorized attempt, the next retry should submit the deterministic fixed-point canonical form derived from the frozen raw payload, not keep submitting a raw form that will drift again. Receipts must preserve raw and submitted/canonical hashes separately, and reviewers should see an idempotence proof over every payload description.

5. **Relation direction must be explicit and fully verified**
   - For Linear relation type `blocks`, set `issueId` to the prerequisite/source issue and `relatedIssueId` to the blocked/dependent issue.
   - When deterministic relation UUIDs are used, preflight exact lookup for every approved UUID and require absence before mutation; do not merely require no matching source/target row.
   - Store returned relation IDs and verify endpoint relation-set deltas after each create. If a deterministic ID was supplied, the returned ID must equal it.
   - Keep the approved edge ledger exact; do not add transitive convenience edges.
   - Ambiguous relation reconciliation must query the exact intended relation UUID. Never adopt a same-direction relation under a different ID, and never infer success from endpoint row candidates alone.
   - A reconciled relation counts as applied only when exact lookup confirms UUID, type, source/prerequisite, target/blocked, and both endpoint projections contain exactly one canonical row with no unrelated full-snapshot drift.
   - If the exact relation UUID is absent during reconciliation, classify it as no-op only when both endpoint full snapshots still match expected state; any drift is a manual-intervention blocker.
   - Final verification must use the exact relation IDs returned/reconciled by Linear and the exact desired edge set. Do not derive final edges from identifier maps that can omit aliases or newly created issues.

6. **Rollback is part of the executable contract**
   - Persist a private before snapshot and a public receipt before mutation.
   - Persist durable intent immediately before every mutating call, not just before the first write; transport timeouts can occur after Linear applied the call.
   - Do not mark a mutation intent `response_confirmed` until the response shape, exact endpoint postconditions, and the writer's in-memory expected-state update have all succeeded. A timeout or postcondition failure after the API call must remain reconcilable/rollback-owned.
   - After an issue update, converge for a bounded window against the exact expected issue snapshot **and** all projections the write can affect (parent embedded child row, child embedded parent title, relation endpoint rows). A single immediate stale read after a successful write is not enough evidence to rollback; poll until exact convergence or timeout, then classify using exact live state.
   - Bound every Linear GraphQL request with a process-level wall-clock deadline that covers connection, headers, and the complete capped response-body read. During convergence, the per-request deadline must never exceed the remaining convergence budget, otherwise a hung read can defeat the recovery/rollback deadline.
   - On failure, reconcile ambiguous outcomes by exact live reread/convergence: if the intended update/create/relation exists after the error, record it as applied and include it in rollback; if exact proof is absent but tracked endpoints drifted, fail closed for manual intervention.
   - Delete only packet-created relations by returned or reconciled exact IDs.
   - Restore fields/parent/state from the before snapshot when authorized, but preserve quarantine labels when that is the fail-safe policy.
   - Before rollback writes, compare the live issue to the writer's expected post-mutation state; if it no longer matches, stop with a manual-intervention status rather than overwriting an external edit.
   - Roll back in dependency-aware order: remove relations first, detach/delete created issues only after zero relation/child/comment checks, restore parent/state/fields in an order that keeps Linear constraints satisfiable.
   - Delete a packet-created issue only if its title/marker still match and it has no relations, children, or comments.
   - Verify post-rollback state for every touched issue and every read-only projection guard, not only the issue that failed.
   - If rollback leaves a bounded manual-intervention residual, any recovery helper must hash-bind every restoration input before use: pin the private before-snapshot SHA, verify the live file hash, and cross-check it against the failed source receipt's recorded `preflight.before_snapshot_sha256` before any mutation.
   - After the recovery helper returns `PASS`, freeze a fresh retry baseline from the recovered live state and hash-bind that baseline to both the original before snapshot and the recovery receipt. Do not prepare a subsequent retry from a stale pre-recovery baseline.
   - Never restore dispatch/implementation labels unless explicitly authorized.

7. **Failure-injection is required before live writes**
   - Build a local in-memory Linear client simulation for the writer and run at least these paths before asking for live execution: success, applied update timeout, applied update timeout with stale post-write reads before convergence, mid-sequence update timeout/no-apply, reparent timeout/no-apply, cancellation/state timeout/no-apply, applied create timeout, create no-apply timeout, applied relation timeout, and relation no-apply timeout.
   - Each failure path should prove `FAILED_ROLLED_BACK_QUARANTINED` or an explicit partial/manual-intervention status, baseline content/state/parent restoration, quarantine labels retained, created relations removed, and packet-created issues absent or safely quarantined.
   - Include a stale-read convergence fixture: the fake client should apply an update, throw/timeout, return the old snapshot for one or more reads, and only then expose the new exact snapshot. The writer should pass only when bounded convergence reaches the exact expected state and projections.
   - Treat a clean dry-run plus one success simulation as insufficient; the important bugs are usually applied-then-timeout, stale-read convergence, and rollback-order bugs.

8. **Review before live writes**
   - After dry-run and failure-injection pass, send the exact writer script SHA and frozen bundle SHA for independent review before live mutation.
   - Ask reviewers to check payload parsing, hash binding, guard coverage including out-of-packet projections, race controls, relation direction, deterministic relation/issue UUID handling, projection handling, durable intent before every mutation, ambiguous outcome reconciliation, rollback ordering, final relation ledger, and secret/log leakage.
   - Treat async review findings by exact script hash. If a review targets a stale SHA, port valid findings into a new frozen/versioned artifact, prove it locally, and re-review the new SHA; do not let stale `BLOCKED`/`CLEAN` verdicts apply to a changed writer.
   - If any current-SHA review returns `BLOCKED`, repair into a new exact script SHA and re-review that SHA before executing; prior authorization does not make a changed writer safe.
   - If Michael says “try again” after a failed execution/recovery, treat it as authorization to prepare and review the next safe revision, not live mutation authority for an unknown future SHA. Ask for exact-SHA execution authorization only after the revised artifact has local proof and current-SHA CLEAN review.

## Reporting proof block

```text
COMMAND=<dry-run or execute command>
RESULT=<PASS|FAIL|BLOCKED>
SCRIPT_SHA256=<writer script sha>
BUNDLE_SHA256=<approved packet sha>
RECEIPT=<receipt path>
FAILURE_INJECTION=<PASS|NOT_RUN|FAIL>
LINEAR_MUTATED=<true|false>
SCOPE=<dry-run preflight|live execution|rollback>
NOT_CLAIMING=<e.g. no Linear mutation yet, no dispatch restoration>
```
