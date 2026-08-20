# Single-issue Linear state transition after exact-head acceptance

Use this reference only when all of the following are true:

- Michael has explicitly authorized the specific Linear write, or standing authorization in the active Prismatic lane covers `mark <issue> Done after exact-head CLEAN/PASS`.
- The implementation candidate has an independently accepted exact head (`CLEAN/PASS`) and the issue transition is the final bookkeeping action for that accepted slice.
- The intended mutation is exactly one issue state field, e.g. `Todo` -> canonical `Done`.
- No labels, descriptions, assignees, relations, parent/child topology, comments, projects, or other issues need mutation.

If any condition is false, fall back to the normal fail-closed Linear writer packet workflow.

## Safe bounded pattern

1. **Bind source and authorization**
   - Record the accepted commit/tree and independent review handle.
   - Confirm the worktree exact head matches the accepted head and tracked status is clean.
   - State the mutation scope in one sentence: `one issue stateId only; no topology/prose/labels/comments`.

2. **Live baseline read**
   - Query only the target issue by identifier.
   - Capture: issue id, identifier, `updatedAt`, `completedAt`, current state id/name/type, team id/key, and available completed states.
   - Select the canonical completed state by exact id/name/type (`Done`, `completed`) rather than guessing from display order.

3. **Guard before write**
   - Fail closed if the issue id, identifier, prior state, prior `updatedAt`, or prior `completedAt` differs from the live baseline.
   - Fail closed if the canonical target state is missing or ambiguous.
   - Fail closed if the local candidate head/tree no longer matches the independently reviewed exact head.

4. **Durable intent before mutation**
   - Append a JSONL receipt line before the mutation with: timestamp, target issue id/identifier, expected-before state/timestamp, intended target state, candidate commit/tree, and non-claims.
   - Use a restricted temp or profile-local path; never include credentials.

5. **One mutation**
   - Execute a single `issueUpdate(id, input:{stateId:<Done>})`.
   - Do not retry by reposting the mutation if the transport result is ambiguous. Reconcile by readback first.

6. **Immediate reconciliation**
   - Read the same issue back through the read-only broker when possible.
   - Accept only if state id/name/type match the canonical completed state and `completedAt` is non-null.
   - Append a result receipt line with status, after-state, updatedAt, completedAt, and any redacted mutation error class.
   - Hash the receipt and report compactly.

## Reporting packet

```text
RESULT=<PASS|BLOCKED>
ISSUE=<TEAM-N>
MUTATION_SCOPE=stateId-only
BEFORE=<state name/id updatedAt completedAt>
AFTER=<state name/id updatedAt completedAt>
CANDIDATE_HEAD=<sha>
REVIEW=<handle:CLEAN/PASS>
RECEIPT=<path>
RECEIPT_SHA256=<sha256>
NOT_CLAIMING=push,PR,merge,deployment,cron/timer mutation,production DB mutation,or downstream issue start
```

## Pitfalls

- Do not create a fresh precontract, blocker document, or broad writer review merely to move one already-accepted issue to `Done` when the scope is exactly one state field and authorization is already present.
- Do not use session history as current Linear proof; always take a live baseline and a readback.
- Do not mutate `Done - Doc Pending` unless the active request specifically asks for that state; bind the exact canonical target.
- Do not start the next Linear issue in the same mutation/report unless Michael explicitly asked for it. Advance the pointer only.
