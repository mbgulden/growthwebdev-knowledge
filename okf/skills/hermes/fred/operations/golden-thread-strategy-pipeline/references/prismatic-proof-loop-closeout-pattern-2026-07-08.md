# Prismatic Proof Loop Closeout Pattern — 2026-07-08

Use when executing Prismatic Proof Loop epics where `Done` means exit-criterion completion with evidence, not code merge.

## Core pattern

1. Resolve the parent epic and children from Linear first.
2. Confirm the explicit parent and child exit criteria.
3. Verify current `origin/main`, not just a local branch or prior PR claim.
4. For each child, produce or reuse evidence that specifically satisfies that child’s exit criterion.
5. Post evidence to the exact child task before moving it.
6. Move only the exact child whose exit criterion is evidenced.
7. Move the parent epic only after every child is verified completed and the parent exit criterion is independently satisfied.

## Linear API closeout detail

The helper path can fail on state/comment operations if identifier resolution or workflow-state loading mismatches the Linear schema. When that happens, use schema-correct GraphQL directly:

```graphql
query($id: String!) {
  issue(id: $id) {
    id identifier title state { name type }
    team { states(first: 50) { nodes { id name type } } }
    children(first: 20) { nodes { identifier title state { name type } } }
  }
}
```

Then select the workflow state where `type == "completed"` (or name is `Done`) and update the exact issue:

```graphql
mutation($id: String!, $stateId: String!) {
  issueUpdate(id: $id, input: {stateId: $stateId}) {
    success
    issue { identifier state { name type } }
  }
}
```

Post evidence with `commentCreate` before changing state.

## Evidence formatting

Every closeout comment should include:

- issue/child identifier and exit criterion
- verification scope label (`ad hoc targeted verification`, not canonical/full-suite green unless actually true)
- exact commands or verifier path
- summarized PASS result
- cleanup status
- remaining blockers or `none`
- merge/PR evidence when code/docs changed

## Parent closeout rule

Before closing an epic:

1. Query the parent and all children.
2. Verify every child state has `type: completed`.
3. Post parent-level evidence tying the parent exit criterion to the child evidence.
4. Move the parent only after that read confirms all children are completed.

## Distribution Readiness example

For Epic 1, child tasks were closed in this order:

1. readiness smoke test
2. metadata/license/package data
3. fresh-clone install and CLI entrypoint path
4. Docker/systemd smoke/docs gate
5. release-blocker checklist
6. parent epic after all five children completed

The release-blocker checklist was not considered complete until a real doc artifact existed with P0/P1 blockers, owners, evidence, and go/no-go status.
