---
type: Reference
title: Linear API gotchas hit during reconciliation packets
description: Concrete GraphQL mutation shapes, label-lookup pattern, and project-name lookup pattern that bit during the 2026-07-27 HDE packet. Applies to any reconciliation or bulk-issue work.
tags: [linear, graphql, mutations, reconciliation]
timestamp: 2026-07-27T22:46:00Z
source_session: HDE reconciliation packet (2026-07-27)
related_skills: [linear-api-operations, multi-source-reconciliation-packet]
---

# Linear API gotchas hit during reconciliation packets

## Symptom

GraphQL validation error during reconciliation packet creation:

```text
"errors": [
  { "message": "Unknown argument \"issueId\" on field \"Mutation.commentCreate\".", ... },
  { "message": "Unknown argument \"body\" on field \"Mutation.commentCreate\".", ... },
  { "message": "Field \"commentCreate\" argument \"input\" of type \"CommentCreateInput!\" is required, but it was not provided.", ... }
]
```

## Cause

Linear's mutation API does not accept flat arguments. `issueCreate`, `issueUpdate`, and `commentCreate` all wrap their payload in an `*Input!` type.

## Correct shapes

```graphql
mutation($input: IssueCreateInput!) {
  issueCreate(input: $input) {
    success
    issue { identifier url title }
  }
}

mutation($id: String!, $input: IssueUpdateInput!) {
  issueUpdate(id: $id, input: $input) { success }
}

mutation($input: CommentCreateInput!) {
  commentCreate(input: $input) { success }
}
```

Python invocation:

```python
input_ = {"issueId": "GRO-XXXX", "body": "..."}
requests.post(
    "https://api.linear.app/graphql",
    headers={"Authorization": linear_api_key, "Content-Type": "application/json"},
    json={"query": q, "variables": {"input": input_}},
)
```

## Other gotchas hit in the same session

- **`workflowStates` is global.** No team filter is needed. The state ID for `Todo` in this workspace looks like `3d29ebe3-00cf-428b-b52a-bfecb5ae4410`. The "In Review" state is type `started`, not `unstarted` — pick by `type: "unstarted"` plus `name: "Todo"` to avoid the wrong default.
- **`issueLabels(filter:{name:{eq:$name}})` is exact-match.** No fuzzy / contains. Apply labels by storing the returned `id` and passing it as `input.labelIds` on `issueUpdate`.
- **Project names must be exact.** `HD Engine Core`, not `HDE Core`. Always `projects(filter:{name:{eq:$name}}){ nodes { id } }` and assert `len(nodes) > 0` before using `nodes[0]["id"]`.

## Verification

After every mutation call:

1. Print the response JSON.
2. Confirm `data.<field>.success` is `true`.
3. If the call mutates a single issue, fetch it back with `query issue(id: $id) { state { name type } labels { nodes { name } } }` to confirm the change landed.

These three checks catch the cases where Linear returns HTTP 200 but the mutation is rejected or silently partial.