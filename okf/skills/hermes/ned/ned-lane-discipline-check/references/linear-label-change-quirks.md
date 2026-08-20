# Linear Label-Change Quirks — Ned Lane-Discipline Relabel

**Captured:** 2026-06-30 ~04:50Z (this session — GRO-143 lane-discipline relabel).

Two related Linear API behaviors discovered while cleaning up a misrouted
AOT interview issue. Worth recording because they're easy to trip on.

---

## Quirk 1 — Auto-state-transition on label change

**Symptom:** when you mutate an issue's `labelIds` via `IssueUpdate`
mutation, Linear may auto-transition the issue's `state` — typically
Backlog → In Progress — even though you did NOT set `stateId`.

**Why:** Linear's workflow rules can map label changes to state transitions.
For example, adding an `agent:*` label may trigger "agent picked up → In
Progress" automatically. The rule is workspace-scoped and not visible in
the API docs.

**Defensive practice:** always pass `stateId` explicitly in the same
mutation, preserving the original state:

```graphql
mutation IssueUpdate($id: String!, $input: IssueUpdateInput!) {
  issueUpdate(id: $id, input: $input) {
    success
    issue { id state { name } labels { nodes { name } } }
  }
}

# variables:
{
  "id": "<issue-uuid>",
  "input": {
    "labelIds": ["<new-label-1>", "<new-label-2>"],
    "stateId": "<original-state-uuid>"   # <-- DEFENSIVE: pin state
  }
}
```

If you forget `stateId`, query the issue after the mutation and revert
the state if it drifted. Cost: 1 extra GraphQL round-trip. Worth it.

---

## Quirk 2 — Label co-existence pattern (agent:ned on already-correctly-labeled issues)

**Symptom:** the GRO-559 dispatcher bug can fire on issues that ALREADY have
a correct lane label (e.g. `agent:fred`). The dispatcher auto-adds `agent:ned`
on top, leaving the issue with BOTH labels.

**Observed in GRO-143 (this session):**
- Pre-mutation labels: `[dispatch:ready, dispatch:priority, agent:fred, agent:ned]`
- The issue had been correctly tagged for Fred's lane (`agent:fred`) AND
  had `agent:ned` auto-applied by the dispatcher on stale-backlog trigger.
- My disposition: drop `agent:ned`, add `agent:kai-content` per the
  description's stated owner, keep `agent:fred` (correct lane).

**Implication for the lane-partition walk:** when you encounter an issue
with `agent:ned` + a SECOND `agent:*` label, do NOT just drop `agent:ned` —
you may need to also ADD a third label if the description names a more
specific owner than the existing co-label.

**Pre-check recipe before mutation:**

1. Query all current labels: `issue(id: "GRO-XXX") { labels { nodes { name } } }`
2. Read description: `issue(id: "GRO-XXX") { description }`
3. Apply the lane-partition walk with these inputs:
   - **Existing lane labels:** the issue may already have a correct lane
   - **Description's stated owner:** the description may name a more specific lane
   - **Comment thread:** may contain "Owner: kai-content when prioritized" or similar

**Disposition patterns:**

| Existing labels | Description says | Action |
|---|---|---|
| `[agent:fred, agent:ned]` | "Owner: kai-content" | Drop `agent:ned`, add `agent:kai-content`, keep `agent:fred` |
| `[agent:fred, agent:ned]` | "Owner: fred" (no other lane) | Drop `agent:ned`, keep `agent:fred` |
| `[agent:fred, agent:ned]` | no owner hint | Drop `agent:ned`, keep `agent:fred` |
| `[agent:ned]` only | "Owner: kai-content" | Drop `agent:ned`, add `agent:fred` AND `agent:kai-content` |
| `[agent:ned]` only | no owner hint | Add `agent:fred` (content default per partition table) |

In all cases: **always pin `stateId` explicitly** per Quirk 1.

---

## Quirk 3 — `stateId: null` does NOT clear state

**Pitfall:** if you want to "leave state alone" in `IssueUpdate`, do NOT
pass `stateId: null` — Linear rejects this and your whole mutation may
fail. Always pass the explicit UUID of the desired state, even if you want
to preserve the current one.

```graphql
# BAD — silently fails or rejects
{ "input": { "labelIds": [...], "stateId": null } }

# GOOD — preserves current state explicitly
{ "input": { "labelIds": [...], "stateId": "e5544f55-..." } }   # Backlog UUID
```

If you're unsure of the current state, query first:

```graphql
query { issue(id: "GRO-XXX") { state { id name } } }
```

---

## Recipe — label-change + state-pin mutation (canonical)

```python
# 1. Query current state + labels
write_file /tmp/gro_query.json << 'JSON'
{"query": "{ issue(id: \"GRO-143\") { id state { id name } labels { nodes { id name } } } }"}
JSON
curl -s https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" -H "Content-Type: application/json" \
  -d @/tmp/gro_query.json

# 2. Resolve label UUIDs for the target lane set
write_file /tmp/label_query.json << 'JSON'
{"query": "{ fred: issueLabels(filter: {name: {eq: \"agent:fred\"}}) { nodes { id } } kai: issueLabels(filter: {name: {eq: \"agent:kai-content\"}}) { nodes { id } } }"}
JSON
curl -s ... -d @/tmp/label_query.json

# 3. Mutate with state-pin
write_file /tmp/gro_update.json << 'JSON'
{
  "query": "mutation IssueUpdate($id: String!, $input: IssueUpdateInput!) { issueUpdate(id: $id, input: $input) { success issue { id state { name } labels { nodes { name } } } } }",
  "variables": {
    "id": "<issue-uuid>",
    "input": {
      "labelIds": ["<label-1-uuid>", "<label-2-uuid>"],
      "stateId": "<preserved-state-uuid>"
    }
  }
}
JSON
curl -s ... -d @/tmp/gro_update.json
```

---

## Reference

- `references/bash-heredoc-backtick-pitfall.md` — the JSON-payload write_file pattern used in steps 1–3 (Linear comment bodies and mutation JSON often contain prose with parens / backticks / dollar signs; write_file sidesteps all of them)
- `references/finalize-task-sh-three-failure-modes-and-rollback.md` — the Mode 3 (wrong-issue) rollback protocol also benefits from explicit state-pinning in step 2's `mutation IssueUpdate`
- `references/curator-flag-stale-backlog-misroute-fingerprint.md` — the GRO-559 dispatcher bug that auto-applies `agent:ned` to aged-backlog items is the root cause of both Quirk 1 and Quirk 2