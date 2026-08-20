# Better-than-North-Star autonomy and review-race patterns

## Trigger

Michael explicitly says to keep going / YOLO on an already-authorized Prismatic self-build runway and does not want to babysit gate transitions.

## Durable lesson

Treat that as permission to keep moving through bounded, already-authorized coordination transitions, not as permission to weaken evidence or safety gates.

Allowed autonomous transitions:

- preserve exact candidate artifacts and verify bundle/ref/tree identity;
- rerun configured local proof and classify environment-shaped canonical failures separately from product failures;
- launch or consume read-only exact-head reviews;
- stop the line on any valid `REPAIR`;
- prepare focused PR gates and use standing reviewed-source merge authority where applicable;
- tighten durable executor cadence when the goal is reducing babysitting latency and the run budget remains bounded.

Still explicit-only:

- production deploy or service restart;
- Linear writes;
- bulk dispatch or writer-cap increase;
- PR close/delete;
- secrets exposure or unsafe state mutation.

## Review-race reconciliation

If a manual continuation and a durable ordered executor both launch read-only exact-head reviews for the same candidate:

1. Do not treat duplicate read-only reviews as a writer conflict.
2. Record all active review IDs in queue/control/handoff.
3. Bind all evidence to the exact head/tree/bundle digest.
4. Any valid `REPAIR` stops the line and supersedes `CLEAN` optimism.
5. Only valid exact-head `CLEAN` evidence can contribute to PR/merge readiness.

## Idle read-only next-slice preload

While the writer gate is waiting on exact-head review, the coordinator may use a spare read-only lane to draft the next slice architecture contract. Mark it clearly:

```text
READ_ONLY_ANALYSIS_ACTIVE
IMPLEMENTATION_NOT_ADMITTED
SUCCESSOR_DISPATCHED=false
```

This preserves sequencing while avoiding idle time.
