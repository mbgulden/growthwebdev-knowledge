# Failed producer recovery on a live Linear critical path

Use this when a Prismatic cap-1 producer dies or times out after creating useful dirty code, and Michael redirects George back to the foundational Linear critical path.

## Trigger

- User says to get back on the foundational/Linear critical path.
- A producer/agent was launched through an already-authorized one-event/one-consumer/cap-1 lane.
- The producer exits without `RESULT`/commit, but leaves a dirty checkpoint.
- Downstream Linear items remain held behind the current issue.

## Required sequence

1. **Pull live Linear graph first.** Verify the current issue state and downstream holds from live Linear before more workflow design.
2. **Do not create adjacent precontracts or blocker docs** unless a newly observed fact truly changes admission. Preserve the latest valid checkpoint and use standing authorization.
3. **Reconcile runtime receipts before code claims.** Bind event status, consumer attempt, cap slot, PID/exit, and whether the producer completed vs failed.
4. **Preserve failed producer truth.** Report `PRODUCER_STATUS=failed` / no `RESULT` separately from any later candidate success.
5. **Inspect the dirty checkpoint exactly.** Determine changed paths and whether the code is syntactically meaningful before deciding repair-in-place vs discard.
6. **Run focused acceptance against dirty bytes.** Use the contract’s focused tests to identify exact defects; repair only those defects unless broader evidence requires more.
7. **Commit one normal descendant only after focused/static proof.** Keep task metadata uncommitted. Bind commit/tree/parent/changed paths/status.
8. **Run canonical exact-head proof and classify boundaries.** Separate candidate defects from out-of-scope/pre-existing canonical failures. Do not overclaim canonical suite green when failures remain.
9. **Require independent exact-head acceptance before Linear mutation.** On `CLEAN/PASS`, perform the already-authorized state transition. Keep downstream tasks held until then.

## Reporting shape

```text
PRODUCER_STATUS=<failed|completed>
PRODUCER_COMPLETED=<true|false>
EVENT_STATUS=<accepted/processed/replayed/...>
CAP=<n>
CANDIDATE_COMMIT=<sha>
CANDIDATE_TREE=<sha>
PARENT=<sha>
CHANGED_PATHS=<exact count/list>
FOCUSED=<result>
STATIC=<result>
CANONICAL=<result or boundary>
CANONICAL_FAILURE_ROOT=<candidate defect|pre-existing/out-of-scope|unknown>
INDEPENDENT_REVIEW=<deleg_id:running|CLEAN/PASS|BLOCKED>
LINEAR_ACTION=<held|mark issue Done after acceptance>
NOT_CLAIMING=<producer success, canonical green, push, PR, merge, deploy, downstream start>
```

## Pitfalls

- Do not treat a killed producer as successful just because the repaired checkpoint later passes tests.
- Do not repost the event or launch a second producer while reconciling receipts; repair the preserved checkpoint unless evidence requires discard.
- Do not let stale/invalid delegated reviews create new blockers. If a review ignores the exact task, classify it invalid and continue with the minimum valid gate.
- Do not mark Linear done before exact-head independent acceptance, even if focused and canonical-boundary proof look good.
