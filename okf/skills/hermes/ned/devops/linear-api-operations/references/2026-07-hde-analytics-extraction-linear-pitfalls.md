md
# Session reference: 2026-07-28 HDE analytics extraction — Linear API pitfalls

Trigger: Ned was posting several sequential comments to the same HDE parent Linear
issues (GRO-4004, GRO-4010, GRO-3992) during a PR-batch cleanup task. Each comment
needed verification, and several GraphQL filter assumptions were wrong. This file
captures the exact pitfalls triggered and the resilient patterns.

## Multi-comment timeline pattern

When posting 3+ comments to the same issue in one session, distinguish them by
**prefix** in the body so verification is cheap and order-independent:

```python
# Header prefixes used in this session (chronological):
hdrs = [
  "PR-batch close authorization (2026-07-28)",                                            # 05:38
  "PR-batch close authorization (2026-07-28) — live-surface drift finding",              # 05:47
  "PR-batch close authorization — extraction branch ready, push requires human action",  # 05:50
]
```

Each comment lands independently. The verification query does not need to be
recency-aware:

```python
q = '''query($id:String!){issue(id:$id){identifier comments(last:50){nodes{body createdAt}}}}'''
for ident in ['GRO-4004','GRO-4010','GRO-3992']:
    cs = requests.post(LINEAR_URL, headers=H, json={'query':q,'variables':{'id':ident}}, timeout=30).json()['data']['issue']['comments']['nodes']
    todays = [c for c in cs if c['createdAt'].startswith('2026-07-28')]
    for c in todays:
        print(c['createdAt'], c['body'].splitlines()[0][:80])
```

`comments(last: 5)` is unreliable for an issue with 10+ historical comments because
it picks the 5 most recent comments globally, not the 5 most recent *today*. Use
`comments(last: 50)` plus a date-substring filter, or a body-prefix filter, to
verify the just-posted comment landed.

## IssueFilter does NOT accept `identifier`

`api.linear.app/graphql` rejects `filter:{identifier:{in:[...]}}` with:

```
"message": "Field \"identifier\" is not defined by type \"IssueFilter\"."
```

The actual `IssueFilter` fields are: `id`, `state`, `priority`, `label`, `project`,
`cycle`, `parent`, `assignee`, `createdAt`, `updatedAt`, `completedAt`, `dueDate`,
`team`, `estimate`, `subscriber`, `number`, `searchQuery`, etc. **`identifier` and
`title` are not filterable fields.**

The agent-friendly pattern is `id` per issue (preferred — `id` is the canonical
UUID like `3d29ebe3-00cf-428b-b52a-bfecb5ae4410`):

```python
q = '''query($id:String!){issue(id:$id){id identifier state{name}}}'''
for ident in ['GRO-4004','GRO-4010','GRO-3992']:
    r = requests.post(LINEAR_URL, headers=H, json={'query':q,'variables':{'id':ident}}, timeout=30).json()
    # 'id' here is the *GRO-XXXX* shortcut that Linear's API resolves; the underlying
    # field name is `id` but you can pass the identifier string and it works.
    # Don't use `filter:{identifier:...}` — that doesn't exist.
```

Loop over identifiers; do not try to list-filter.

## WorkflowState does NOT have `title`

A `state { name title }` query returns:

```
"Cannot query field \"title\" on type \"WorkflowState\". Did you mean \"type\"?"
```

The available fields are `id`, `name`, `type`, `position`, `color`, `description`.
The intent was likely to use `name` (which is the human-readable label).

## Posting comments with `commentCreate` and the input shape

The right shape (always wrap body + issueId in `input`):

```python
qcm = '''mutation($input:CommentCreateInput!){
  commentCreate(input: $input){success comment{id createdAt}}
}'''
rr = requests.post(LINEAR_URL, headers=H, json={
    'query': qcm,
    'variables': {'input': {'issueId': issue_id, 'body': body}},
}, timeout=30)
if rr.get('errors'): raise RuntimeError(rr['errors'])
```

Do not pass `commentCreate(issueId, body)`. Linear rejects top-level args.

## Linear state for parent/epic gold-gating

When a parent issue is closed while child issues are still incomplete, the right
move is **not** to flip the parent back to Done. Instead,

1. Post a comment explaining the drift (which child is incomplete, why the work
   did not land, what the canonical rubric requires).
2. Re-open the parent from `Done` to `Todo` (`stateId: 3d29ebe3-00cf-428b-b52a-bfecb5ae4410`).
3. Re-verify after each child independently completes.

Use `workflowStates` to get the IDs:

```graphql
query { workflowStates { nodes { id name type position } } }
```

The IDs observed in this session:
- `Todo (unstarted)`: `3d29ebe3-00cf-428b-b52a-bfecb5ae4410`
- `In Progress (started)`: `734901ee-58f0-457c-b9a0-f911c0da13a4`
- `In Review (started)`: `6a5050ad-3386-4623-a404-7f2791047cd5`
- `Backlog (backlog)`: `e5544f55-482e-49ac-b0f7-3dd2e1775dbb`
- `Done (completed)`: `bbf71b3e-9a05-48ce-9418-df8b9c0b8fec`

These are workspace-global. Different teams may have different state IDs; query
once per session.

## Lesson: gate honesty over closure momentum

A parent Done with multiple children still Todo is dishonest state. The HDE
reconciliation rubric (`docs/operations/hde-green-state-rubric.md`) requires every
required child to produce independent evidence before the parent can be green.
The 2026-07-28 reopen of GRO-4004, GRO-4010, GRO-3992 from Done to Todo is
exactly the right move whenever a "Done" auto-finalize contradicts the evidence
the parent gate requires.

The Linear-comments-as-audit-trail pattern is what makes this defensible: every
reopen is documented in the issue's comment history with timestamps, evidence,
and the canonical rubric reference. Future dispatches and agents reading the
issue see the same audit trail.
