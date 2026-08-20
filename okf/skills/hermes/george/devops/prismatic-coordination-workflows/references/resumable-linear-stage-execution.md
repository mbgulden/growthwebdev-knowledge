# Resumable Linear Stage Execution

Use this when a Prismatic Linear mutation packet is partly applied and the user wants forward progress, not another open-ended review loop.

## Durable lesson

When a stage has been verified live, preserve it as a checkpoint and resume from the next stage. Do **not** keep rolling the whole packet back to zero unless the verified stage itself is invalid.

This is especially important after user frustration that the workflow will never be approved. Treat that as a workflow signal: tighten the acceptance contract and run the next finite, observable stage.

## Recommended stage boundaries

1. `content` — update existing issue body/title/labels/state fields.
2. `create` — create new issue(s), verify parent/child projection.
3. `topology_state` — reparent/order/state/assignee/project transitions.
4. `relations` — dependency/relation edges.
5. `final_proof` — compact receipt, hashes, and explicit non-claims.

Each stage should write:

```text
RESULT=<PASS|BLOCKED>
RECEIPT=<public receipt path>
CHECKPOINT=<private checkpoint path if needed>
CHECKPOINT_SHA256=<sha256>
RESUME_FROM=<next stage>
ROLLBACK=<true|false>
NOT_CLAIMING=<what remains>
```

## Linear ID terrain

Linear can keep soft-deleted entity UUIDs reserved. If create returns a conflict such as “Entity Issue with id ... already exists” after a prior rollback/delete, do not infer that the old deleted object is still usable. Roll the frozen ID ledger forward with fresh UUIDv4 IDs and preserve the verified content checkpoint.

## Pitfalls

- Avoid adversarial review drift: a stale async reviewer can be useful, but do not let each finding restart approval from zero if the affected stage is already proven.
- Avoid monolithic replay: if content is live and verified, create a content checkpoint and resume from `create` rather than undoing and redoing the content stage.
- Avoid overclaiming: a stage checkpoint is not canonical full completion. State the exact `RESUME_FROM` boundary.
- Avoid treating GraphQL return/error as the only truth. Reconcile against live issue snapshots; a returned mutation can still need convergence, and an errored mutation can still have partially applied.

## When to update the main packet script

If the packet writer hard-codes issue/relation UUIDs, rolling the ledger forward requires both:

1. patching the executable’s frozen UUID constants; and
2. writing a new checkpoint that records the old checkpoint hash as source plus the new frozen ID ledger.

This preserves auditability without replaying already verified mutation stages.
