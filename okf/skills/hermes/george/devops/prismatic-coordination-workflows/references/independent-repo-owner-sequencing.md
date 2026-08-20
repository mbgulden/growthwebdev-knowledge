# Independent repository owner sequencing

Use this reference when George coordinates a Prismatic-adjacent independent repository such as `prismatic-web-publisher`, where another agent (for example Ned) owns the implementation lane and follows assigned linear tasks.

## Durable lesson

A course-correction or exact-head candidate review can tempt George to become a backup producer. Do not do that when Michael has assigned the repository to another implementation owner. George's durable role is coordination, candidate preservation, exact-head review, CI/merge gating, and sequence control.

## Required workflow

1. **Bind ownership explicitly.** Record the implementation owner, George role, active candidate SHA/task, and non-overlap rule in the current handoff/control state.
2. **Preserve the one-candidate invariant.** If a local candidate exists, keep it as review material or queued source, not a competing implementation lane.
3. **Allow the owner to continue non-overlapping linear tasks.** Do not freeze the owner unnecessarily. If their task overlaps the active candidate, require exact task/head/path reporting and sequence it.
4. **Do not overclaim chat delivery.** If a Telegram/group nudge is attempted, verify delivery from scheduler/gateway logs. A generated cron output is not delivery proof. Report `DELIVERED=false` when logs show `Chat not found` or another delivery failure.
5. **Use durable state, not repeated nudges, as the coordination source of truth.** If direct delivery is unavailable, record the boundary in George's handoff/control state and wait for a trusted route or visible owner artifact before claiming the owner has received direction.
6. **Review owner output as untrusted exact artifacts.** Require exact head, path allowlist, local proof, independent review, GitHub CI, and merge-SHA release proof as applicable before promotion.

## Proof packet fields

```text
IMPLEMENTATION_OWNER=<agent/person>
GEORGE_ROLE=coordination_review_and_sequence_guard
ACTIVE_TASK=<task id>
ACTIVE_CANDIDATE=<sha or none>
OWNER_CAN_CONTINUE=<non-overlap condition>
OVERLAP_RULE=<exact task/head/path report and hold>
DELIVERY_ATTEMPTED=<true|false>
DELIVERED=<true|false|not_attempted>
DELIVERY_EVIDENCE=<gateway/scheduler log or direct artifact>
NOT_CLAIMING=<receipt by owner, merge, deploy, cap increase unless proven>
```
