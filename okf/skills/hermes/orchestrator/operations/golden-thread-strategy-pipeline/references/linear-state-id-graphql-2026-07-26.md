---
type: Reference
title: Linear GraphQL — stateId UUID, not state name
description: Linear issueCreate / issueUpdate require stateId (UUID), not state (name). Query workflowStates first, capture UUID, reuse across the parent/epic/task tree.
resource: operations/golden-thread-strategy-pipeline/references/linear-state-id-graphql-2026-07-26.md
git_path: operations/golden-thread-strategy-pipeline/references/linear-state-id-graphql-2026-07-26.md
tags: [linear, graphql, state, api, epic, parent, child]
timestamp: 2026-07-26
linear_issue: pending
git_repo: growthwebdev-knowledge
last_verified: 2026-07-26
verified_by: fred (ad hoc targeted verification, not suite green)
status: active
---

# Linear GraphQL — `stateId` UUID, Not `state` Name

## The gotcha

Linear's `issueCreate` and `issueUpdate` mutations accept `stateId` (UUID), not `state` (human-readable name like "Todo" or "In Progress"). Passing the name returns HTTP 400 with no body detail.

```python
# WRONG — 400 Bad Request, no usable error body
res = gql("""
  mutation($input: IssueUpdateInput!) {
    issue: issueUpdate(id: $id, input: $input) {
      success issue { id identifier }
    }
  }
""", {"id": parent_id, "input": {"state": "Todo"}})

# RIGHT — UUID from workflowStates query
res = gql("""
  mutation($input: IssueUpdateInput!) {
    issue: issueUpdate(id: $id, input: $input) {
      success issue { id identifier }
    }
  }
""", {"id": parent_id, "input": {"stateId": "3d29ebe3-00cf-428b-b52a-bfecb5ae4410"}})
```

## The fix — query workflowStates first

Before any mutation that needs a state, fetch the team's workflow states:

```graphql
query {
  workflowStates(filter: { team: { id: { eq: "<TEAM_ID>" } } }) {
    nodes { id name type position }
  }
}
```

Build a `{name: id}` map. Capture the UUID for "Todo" (or whichever state you want). Reuse that single UUID across the parent epic, every child epic, and every child task — they all start in the same state.

```python
todo_state_id = None
states = gql(workflow_states_query, {"teamId": TEAM_ID})
for s in states["data"]["workflowStates"]["nodes"]:
    if s["name"] == "Todo":
        todo_state_id = s["id"]
        break
assert todo_state_id, "Todo state not found in team workflow"
```

For the GRO team in the canonical instance:

| Name | Type | UUID |
|---|---|---|
| Backlog | backlog | `e5544f55-...` |
| Todo | unstarted | `3d29ebe3-00cf-428b-b52a-bfecb5ae4410` |
| In Progress | started | `734901ee-...` |
| In Review | started | `6a5050ad-...` |
| Done | completed | `bbf71b3e-...` |
| Done - Doc Pending | completed | `d4e1207b-...` |
| Canceled | canceled | `a19484ec-...` |
| Duplicate | duplicate | `8a67aa62-...` |

## Use `stateId` on issueCreate too

```python
inp = {
    "teamId": TEAM_ID,
    "title": full_title,
    "description": desc,
    "parentId": epic_id,
    "stateId": todo_state_id,   # not "state": "Todo"
    "priority": 2,
}
```

## Why not `state`?

Linear's GraphQL schema for `IssueUpdateInput` and `IssueCreateInput` does not have a `state` field that accepts the name string. It has `stateId` (ID!). Other Linear UIs (the web app, the SDKs that wrap the API) translate names → UUIDs internally; raw GraphQL callers must do it themselves.

## When 400 returns with no body — debugging

A 400 from Linear without a useful error message is almost always a schema-validation failure. The most common causes in order of frequency:

1. `state` instead of `stateId` — name string against a non-existent field.
2. Wrong ID type — passing a label/team/cycle name where the field wants a UUID.
3. Field that requires `ID!` but the variable is `String!`.
4. A field that does not exist on the active input type (Linear sometimes adds new fields).

For each, log the request body, then walk the mutation input spec at https://developers.linear.app/docs/graphql/working-with-the-graphql-api.

## Pitfalls

- **Do not assume the GRO team's UUIDs are stable.** They may change if Michael restructures the workflow. Always re-query `workflowStates` per session rather than hard-coding.
- **Do not paste 400 errors silently.** If a mutation returns 400 with no body, log the full request and walk the schema.
- **Do not use the `state` field on input objects.** It does not exist; the field is `stateId`.

## Verification boundary

Ad hoc targeted verification only — not full docs-suite green. Validated by 2026-07-26 Journal PE Integration session, where 47 issues were created across 1 parent + 7 epics + 39 tasks after switching from `state` to `stateId`.