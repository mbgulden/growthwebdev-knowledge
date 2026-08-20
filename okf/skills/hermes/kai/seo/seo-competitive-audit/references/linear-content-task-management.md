# Linear API — Content Task Management

## Purpose

Create, close, and track content production tasks in Linear from within a Hermes agent session. Used when bridging audit data → content production needs to be tracked alongside the actual page work.

## Authentication

- API key in `Authorization` header WITHOUT "Bearer" prefix
- Key: stored in env `LINEAR_API_KEY`
- Endpoint: `https://api.linear.app/graphql`
- Team: GrowthWebDev (key: GRO, id: b6fb2651-5a1f-4714-9bcd-9eb6e759ffef)
- Active Oahu Tours project ID: `5a9ea0d6-f6c1-42ee-adf6-f4dd59e9db9b`

## Python Pattern (Reliable — Use write_file, Not Heredocs)

Inline `python3 -c "..."` heredocs fail when descriptions contain em-dashes, smart quotes, or multi-paragraph markdown. Always write a `.py` file first, then execute it.

```python
import os, json, urllib.request

key = os.environ['LINEAR_API_KEY']
team_id = 'b6fb2651-5a1f-4714-9bcd-9eb6e759ffef'
proj_id = '5a9ea0d6-f6c1-42ee-adf6-f4dd59e9db9b'

def gql(query, variables=None):
    req = urllib.request.Request('https://api.linear.app/graphql',
        data=json.dumps({'query': query, 'variables': variables or {}}).encode(),
        headers={'Authorization': key, 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())
```

## Creating Issues in Bulk

```python
tasks = [
    {'title': 'Task title here', 'desc': 'Multi-line description with any characters.'},
]

for task in tasks:
    result = gql("""
    mutation($t: String!, $d: String!, $team: String!, $proj: String!) {
      issueCreate(input: {title: $t, description: $d, teamId: $team, projectId: $proj}) {
        issue { id identifier title }
      }
    }
    """, {'t': task['title'], 'd': task['desc'], 'team': team_id, 'proj': proj_id})
    issue = result['data']['issueCreate']['issue']
    print(f"{issue['identifier']}: {issue['title']}")
```

## Closing Issues (Moving to Done)

Find the done state ID once, reuse it:

```python
# Get state ID from an issue already in Done state
result = gql('{ issues(filter: {number: {eq: 387}}) { nodes { id state { id name } } } }')
done_state_id = result['data']['issues']['nodes'][0]['state']['id']
# On 2026-06-03, this was: bbf71b3e-9a05-48ce-9418-df8b9c0b8fec

# Close an issue by number
for num in [455, 456]:
    result = gql('{ issues(filter: {number: {eq: %d}}) { nodes { id } } }' % num)
    issue_id = result['data']['issues']['nodes'][0]['id']
    gql('mutation { issueUpdate(id: "%s", input: {stateId: "%s"}) { success } }' % (issue_id, done_state_id))
```

## Finding Issues by Number

Use the `number` filter (integer, no "GRO-" prefix). The `identifier` filter (`GRO-455`) returns HTTP 400.

```graphql
# WRONG — returns 400:
{ issues(filter: {identifier: {eq: "GRO-455"}}) { nodes { id } } }

# RIGHT:
{ issues(filter: {number: {eq: 455}}) { nodes { id identifier title state { name } } } }
```

## Listing All Issues in a Project

```python
result = gql('{ project(id: "PROJECT_ID") { issues { nodes { id identifier title state { name } updatedAt } } } }')
```

## Checking Workflow States

```python
result = gql('{ issues(filter: {number: {eq: 387}}) { nodes { id state { id name } } } }')
# The done state ID from the response: bbf71b3e-9a05-48ce-9418-df8b9c0b8fec
```

## Commenting on Issues

```python
result = gql("""
mutation($issueId: String!, $body: String!) {
  commentCreate(input: {issueId: $issueId, body: $body}) {
    success
  }
}
""", {'issueId': issue_id, 'body': "Comment text here"})
```

## Formatting Rules (Michael's Preference)

**Always use direct URLs when referencing Linear issues in descriptions or comments.**
Never use bare issue numbers like `GRO-340` — always format as a clickable link:

```
<!-- BAD: -->
GRO-340 is the Kualoa interview script.

<!-- GOOD: -->
[GRO-340](https://linear.app/growthwebdev/issue/GRO-340) is the Kualoa interview script.
```

This applies to:
- Issue descriptions (set via `description` field in `issueCreate` or `issueUpdate`)
- Comments on issues (via `commentCreate`)
- Any document or report that references Linear issues (reports, content packs, backlog status docs)

## Known Issues

- **Usage limit:** The free Linear tier caps active issues at ~45-50. Tasks hit `USAGE_LIMIT_EXCEEDED` when exceeded. Clean up completed tasks before creating new ones.
- **`issueUpdate` transient failure:** `stateId` transitions may fail with `INPUT_ERROR: "Entity not found in validateAccess: stateId"` on first attempt even when stateId is correct. Retry — succeeds on second call.
- **Mutation variable types:** Always use `String!` for all three IDs (teamId, projectId, stateId) — Linear treats them as opaque strings.
