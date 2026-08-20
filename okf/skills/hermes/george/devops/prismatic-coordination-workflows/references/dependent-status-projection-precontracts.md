# Dependent status and side-effect projection precontracts

Use this when a downstream Prismatic task asks for status, dashboard, projection, next-run, read-model behavior, or downstream side-effect projection from accepted outcomes, but its upstream canonical authority is not merged yet.

## Trigger

- Linear says the downstream issue `depends_on` or is blocked by an upstream issue still `Todo`, `blocked`, or only contract-reviewed.
- Current merged topology has mutable/sample/provisional fields that look useful (`last_run_at`, `last_status`, simulated `next_run_at`, dashboard fixtures, local output/status files), but the task contract says to derive truth from canonical durable authority.
- The downstream task would project accepted canonical outcomes into a side-effecting surface such as Linear comments or labels, but the merged base has no accepted outcome envelope, immutable target identity, projection state store, or separately authorized writer policy.
- The upstream task is supposed to define a shared runner/query/bucket/receipt model and that API is not present in the exact merged base.

## Pattern

1. Re-read bounded Linear metadata and relation graph for the downstream issue and bind hashes for the export, exact description, and extracted issue row.
2. Audit exact merged topology for both canonical surfaces and disqualified temptations. Name the disqualified surfaces explicitly.
3. If the upstream authority is not merged, freeze a **precontract blocker**, not an implementation contract.
4. In the precontract, define the future finite boundary and adversarial matrix, but mark implementation/admission as blocked until the upstream read/query/outcome model exists.
5. For side-effect projections, require immutable provider-native target identity (`linked_issue_id` or equivalent), deterministic idempotency keys, durable intent/attempt/ack/quarantine/retry/DLQ records, timeout-after-write reconciliation, identity-preserving replay, and a separate live-mutation gate.
6. Dispatch independent exact-hash review of the precontract blocker.
7. Update handoff with: issue state, relation, base/tree, artifact SHA, event count zero, worktree created false, review id pending, and non-claims.
8. Stop before task copy, worktree, event, producer, PR, merge, deploy, or Linear write unless separately authorized after the blocker clears.

## Required wording

```text
STATUS=FROZEN_PRECONTRACT_BLOCKED
RELATION=<upstream> <state> --blocks--> <downstream> <state>
TOPOLOGY=<canonical gaps plus disqualified mutable/sample surfaces>
STATE=<DOWNSTREAM>_PRECONTRACT_BLOCKED_ON_<UPSTREAM>_CANONICAL_READ_MODEL
EVENT_COUNT=0
WORKTREE_CREATED=false
NOT_CLAIMING=implementation contract freeze, admission readiness, event, producer, implementation, candidate, tests, PR, merge, deployment, cron/timer mutation, credentials, network, or Linear write
```

For side-effecting projection tasks, also record:

```text
PROJECTION_AUTHORITY_GAPS=no_accepted_outcome_envelope;no_immutable_target_identity;no_projection_intent_attempt_ack_quarantine_retry_dlq
LINEAR_WRITE_COUNT=0
LIVE_MUTATION_GATE=separate_exact_authorization_required
```

## Pitfalls

- Do not implement status/read projections against mutable transport fields just because they exist.
- Do not add a second scheduler, cron parser, bucket calculator, receipt identity, database, or cache to unblock a downstream task.
- Do not use dashboard/sample adapters as live truth. If fixtures are mentioned, they belong only in adversarial tests proving they have zero effect.
- Do not treat a generic provider/client method as safe projection authority. For Linear labels, full-set replacement APIs are disqualified unless the contract proves owned-label deltas preserve unrelated labels.
- Do not let implementation/test approval imply live mutation approval. Comments, labels, credentials, writer identity, allowlists, rate/concurrency limits, and rollback need a separate exact live gate.
- A `CLEAN/PASS` review of an earlier broader blocker does not review a later narrower contract. Triage reviews by exact artifact SHA.
- `wrap up then move on` means complete safe steering/review gates; it is not implicit authorization to admit events or launch producers.

## Examples

### GRO-4318 status projection

GRO-4318 status projection depended on GRO-4317. Current base exposed mutable `native_crons.last_run_at/last_status`, simulated `schedules.next_run_at`, no canonical runner inbox/query API, no shared schedule-bucket calculator, and no `pe crons status` CLI. Correct action was to freeze a read-only precontract blocker defining the future status semantics and adversarial matrix, then dispatch exact-hash review while preserving zero events/worktrees.

### GRO-4336 Linear projection

GRO-4336 required projecting accepted cron outcomes to Linear idempotently, but current base had no merged accepted runner outcome envelope, no immutable `linked_issue_id` in aggregate/receipt authority, and no cron-specific projection intent/attempt/ack/quarantine/retry/DLQ store. Correct action was to freeze a blocked precontract defining target identity, deterministic idempotency, timeout-after-write reconciliation, identity-preserving replay, owned-label/comment limits, zero-network tests, and a separate live Linear mutation gate while preserving zero events/worktrees/writes.