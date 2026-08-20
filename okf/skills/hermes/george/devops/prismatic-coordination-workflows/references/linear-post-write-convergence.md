# Linear Post-Write Convergence and Stale-Read Recovery

Session-derived pattern for Prismatic Linear executable packet writers.

## Problem class

Linear mutations can apply successfully while the immediate follow-up read still returns a stale projection, especially through embedded rows such as a parent's child list or a child's parent-title field. If the writer treats that first stale read as definitive failure, it can start rollback even though the intended write is already present or about to become observable.

## Durable fix pattern

- Persist mutation intent before the GraphQL call.
- Execute the mutation under a hard wall-clock request deadline.
- If the response succeeds **or** raises a transport/timeout error after the call may have been applied, enter bounded convergence instead of immediately advancing or rolling back.
- Poll exact live state until either:
  - the issue full snapshot and every affected embedded projection match the expected post-mutation state; or
  - the convergence deadline expires.
- Only mark `response_confirmed` / advance expected in-memory state after exact convergence.
- If exact convergence fails:
  - exact intended state visible -> classify applied and include in rollback/final verification;
  - exact intended state absent and all tracked endpoints still match pre-intent state -> classify no-apply rollback path;
  - any unowned drift -> fail closed as manual intervention.

## Projection scope checklist

Convergence must cover the full mutation lifecycle, not only ordinary `mutate_issue` updates. Treat a reviewer finding of “post-write convergence only covers updates” as a valid blocker until each write class below has exact post-write projection proof.

Forward writes:

- **Issue update:** the edited issue's full snapshot, parent embedded child rows when title/description/parent linkage changes, and child embedded parent-title rows when parent title changes.
- **Issue creation:** deterministic created issue identity/full snapshot plus the parent child row when created under a parent.
- **Reparent/update of parent links:** edited issue plus old-parent and new-parent child sets, and affected children's parent-title projections.
- **Relation creation:** deterministic relation identity/direction plus both endpoint snapshots/relations.

Rollback writes:

- **Relation deletion:** exact relation absence plus both endpoint snapshots/relations.
- **New issue deletion:** exact issue absence plus parent child-row removal.
- **Content/state restoration:** restored issue snapshot plus parent child row and child parent-title projections.
- **Parent restoration:** restored issue plus old/new parent topology.
- **Quarantine restoration:** complete issue snapshot and final label/state set.

During post-write convergence, compare exact domain fields and affected projections. Do not require `updatedAt` equality after writes or rollback writes when projections have legitimately changed; timestamp lag/drift can be orthogonal to domain-state convergence. Keep immutable identity, content hashes, state, labels, parent/child topology, relations, assignment/project, and owned endpoint snapshots exact.

## Deadline rule

Use a process-level alarm/deadline around every GraphQL request, not only the socket timeout. The deadline must cover connect, headers, and complete capped body read. During convergence, each request's deadline must be `min(default_request_deadline, remaining_convergence_budget)`.

## Required fixture

Add a fake-client scenario where an update:

1. applies successfully;
2. raises a simulated transport timeout;
3. returns the old snapshot for one or more reads;
4. then returns the exact new snapshot and projections.

The writer should pass only after bounded convergence reaches the exact expected state.
