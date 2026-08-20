# Linear GraphQL API — Auth & Task Creation Pattern

**Date:** 2026-07-26
**Updated:** 2026-07-26 — confirmed correct auth format

## Auth: NO "Bearer" Prefix

Linear API uses `Authorization: <key>` — **NO "Bearer" prefix**. The Bearer format returns `{"errors": [{"message": "Authentication required"}]}`.

```bash
LINEAR_KEY=$(grep LINEAR_API_KEY ~/.hermes/profiles/kai/.env | cut -d= -f2)
curl -sS -X POST https://api.linear.app/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: ${LINEAR_KEY}" \
  -d '{"query":"{ teams { nodes { id name } } }"}'
```

## Python Pattern (Recommended)

```python
import subprocess, json, os

key = os.environ.get('LINEAR_API_KEY', '')  # Use env var, NOT .env file
auth_val = key  # No "Bearer" prefix

def gql(query, vars=None):
    payload = {'query': query}
    if vars:
        payload['variables'] = vars
    r = subprocess.run([
        'curl', '-sS', '-X', 'POST', 'https://api.linear.app/graphql',
        '-H', 'Content-Type: application/json',
        '-H', 'Authorization: Bearer ' + auth_val,
        '-d', json.dumps(payload)
    ], capture_output=True, text=True)
    return json.loads(r.stdout)

# Get teams
data = gql('{ teams { nodes { id name } } }')
for t in data['data']['teams']['nodes']:
    print(t['id'], t['name'])
```

## Critical Env Var Gotcha

The `hermes --profile kai` shell has a `LINEAR_API_KEY` env var that **shadows** the `.env` file value. `os.environ.get('LINEAR_API_KEY', '')` returns the real 48-char key. `grep LINEAR_API_KEY ~/.hermes/profiles/kai/.env` shows a **masked** value with two concatenated entries (the file has a duplicate entry).

Use `os.environ.get()` in Python, or `grep LINEAR_API_KEY ~/.hermes/profiles/kai/.env | cut -d= -f2` in bash.

## Useful Queries

### List teams
```python
gql('{ teams { nodes { id name } } }')
```

### List issues (workspace-level)
```python
gql('{ issues(first: 20) { nodes { id identifier title priority state { name } team { name } } } }')
```

### Get team ID
```python
# GrowthWebDev team
TEAM_ID = "b6fb2651-5a1f-4714-9bcd-9eb6e759ffef"
```

### Create issue (mutation)
```python
mutation = '''
mutation createIssue($title: String!, $body: String, $teamId: String!, $priority: Int, $labelIds: [String!]) {
  issueCreate(input: {
    title: $title,
    description: $body,
    teamId: $teamId,
    priority: $priority,
    labelIds: $labelIds
  }) {
    success
    issue { id identifier title }
  }
}
'''
vars = {
    'title': '[CRIT-01] AOT: Fix broken booking calendar',
    'body': 'Problem: ...\nFix: ...\nVerification: ...',
    'teamId': 'b6fb2651-5a1f-4714-9bcd-9eb6e759ffef',
    'priority': 1,
    'labelIds': ['122...', '123...']  # type:task, priority:critical
}
data = gql(mutation, vars)
```

## Available Labels (as of 2026-07-26)

| Label ID | Name |
|----------|------|
| `122...` | type: task |
| `123...` | priority: critical |
| `124...` | priority: high |
| `125...` | priority: medium |
| `126...` | priority: low |
| `127...` | area: cro |
| `128...` | area: seo |
| `129...` | area: content |
| `130...` | area: a11y |
| `131...` | area: technical |

Use the Ned skill's linear_api.py to get current label IDs:
```bash
cd /home/ubuntu/work/prismatic-engine/worktrees/ned-GRO-3165/portable-skills/linear
python3 scripts/linear_api.py list-issues --limit 5
```

## Known Team (GrowthWebDev)

- **Team ID:** `b6fb2651-5a1f-4714-9bcd-9eb6e759ffef`
- **Key:** `GRO`
- **Workspace:** GrowthWebDev

## 11 AOT Gap Analysis Tasks (Created 2026-07-26)

| Linear ID | Priority | Title |
|-----------|----------|-------|
| GRO-4292 | 🔴 Critical | Fix broken booking calendar on /rentals/ |
| GRO-4293 | 🔴 Critical | Add booking CTA to guide pages |
| GRO-4294 | 🔴 Critical | Fix heading hierarchy (H1→H3→H4→H2) |
| GRO-4295 | 🟠 High | Add Organization + LocalBusiness schema |
| GRO-4296 | 🟠 High | Fix image alt text on tour cards |
| GRO-4297 | 🟠 High | Add trust signals near booking CTAs |
| GRO-4298 | 🟠 High | Fix /adventure-guide/ 404 |
| GRO-4299 | 🟠 High | Add meta keywords to key pages |
| GRO-4300 | 🟠 High | Fix Japanese hreflang |
| GRO-4301 | 🟡 Medium | Add x-default hreflang declaration |
| GRO-4302 | 🟡 Medium | Fix broken links on Japanese tour pages |
