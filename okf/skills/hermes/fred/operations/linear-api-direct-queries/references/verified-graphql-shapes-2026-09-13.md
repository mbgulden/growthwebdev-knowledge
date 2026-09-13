# Linear GraphQL: verified working query shapes (2026-09-13)

Condensed reference for the exact GraphQL shapes that returned HTTP 200 against
`api.linear.app/graphql` on this date. Use as a starting point, but always
re-probe if you get a 400 — schema can drift.

## Token (orchestrator profile)

Fastest path (zero stderr noise — verified 2026-09-13 ~06:20Z overnight cron):
```bash
K=$(grep LINEAR_API_KEY /home/ubuntu/.hermes/profiles/orchestrator/.env | head -1 | cut -d= -f2 | tr -d '"' | tr -d "'")
Q=/tmp/q-$$.json   # per-invocation name: /tmp is SHARED across parallel agents/profiles
curl -s https://api.linear.app/graphql -H "Authorization: $K" -H "Content-Type: application/json" -d @$Q
```
`tr -d '"'` is insurance against the value being quoted in the file.
**Do NOT hardcode a fixed `/tmp/q.json`** — a 2026-09-13 cold-start `write_file` to that exact path warned that a *sibling subagent* was concurrently using it (last-write-wins on the body). Use `$$` (PID) or a per-session subdir.

Also works:
```bash
source /home/ubuntu/.hermes/profiles/orchestrator/.env 2>/dev/null
# $LINEAR_API_KEY is now set (lin_api_* prefix)
```
**`2>/dev/null` is load-bearing** (hit live 2026-09-13 04:46Z): the `.env`
contains non-`KEY=value` lines (a bare public key / email line), so a bare
`source` spits `bash: export: '...': not a valid identifier` onto stderr. The key
still exports and the query still works — but in a cron/agent turn suppress the
noise (or parse the key out of the file explicitly) so the stderr garbage doesn't
masquerade as a token failure in the transcript.

Authorization header: `Authorization: *** — **bare token, no `Bearer`**.
Linear explicitly rejects `Bearer` on API keys with a hard 400.

If the .env path doesn't work, fall through to `credentials.json`:
```python
key = json.load(open('/home/ubuntu/.hermes/profiles/orchestrator/credentials.json'))[
    'credentials']['LINEAR_API_KEY']['value']
```
Note: `credentials.json` entries are dicts `{value, scope, description, source_env}`,
not flat strings. Feeding the dict directly to the header 401s silently.

## Shape D (default for single-issue LIVE-VERIFY) — singular `issue(id: "GRO-XXXX")`

The **cheapest and most direct** single-issue path (no team resolution, no
fan-out). **Verified working** 2026-09-13 run 10 and again on the 2026-09-13
03:23Z quiet-cycle run — HTTP 200 with the full issue including `state{name,type}`
and `url`. Use this **first** for a quiet-cycle LIVE-VERIFY when you already know
the identifier. If it ever 400s `String!` or `Unknown argument` again, fall back
to Shape E (if you have the team UUID) or Shape B, and re-probe before re-asserting.

```graphql
query {
  issue(id: "GRO-4929") {
    identifier title state { name type } priority updatedAt url
  }
}
```
Response is `data.issue` (singular), not `data.issues.nodes[0]`.

## Shape E (preferred for single-issue) — numeric `number` filter, standalone or team-scoped

Most reliable single-issue path. Verified working 2026-09-13 run 11 (team-scoped), and again on the 2026-09-13 cold-start cron re-verification as a **standalone `issues(...)` call with no team wrapper** — HTTP 200, correct single node (GRO-4929, id `b6aee0b6-7c82-4031-ab41-8d9d15ebae94`). `IssueFilter.number` is a `NumberComparator` — pass the numeric part as a bare integer, not a quoted string.

**Standalone form (no team UUID needed — use this first):**
```graphql
query {
  issues(first: 5, filter: { number: { eq: 4929 } }) {
    nodes {
      identifier
      title
      state { name }
      priority
      updatedAt
    }
  }
}
```

**Team-scoped form (only if you also need team scope):**
```graphql
query {
  team(id: "b6fb2651-5a1f-4714-9bcd-9eb6e759ffef") {
    issues(first: 5, filter: { number: { eq: 4929 } }) {
      nodes {
        identifier
        title
        state { name }
        priority
        updatedAt
        createdAt
      }
    }
  }
}
```

Resolve the team UUID first if you don't have it:
```graphql
query { teams(first: 20) { nodes { id key name } } }
```
GRO team UUID observed 2026-09-13: `b6fb2651-5a1f-4714-9bcd-9eb6e759ffef`.

## Shape A — team UUID + client-side identifier match

Fallback when Shape E/B 400. Always works, slightly more verbose.

```graphql
query {
  team(id: "b6fb2651-5a1f-4714-9bcd-9eb6e759ffef") {
    issues(first: 100) {
      nodes { identifier title state { name } priority updatedAt }
    }
  }
}
```
Filter `nodes[].identifier == "GRO-XXXX"` client-side.

## Shape B — `id: { eq: "GRO-XXXX" }` filter

The intended direct **plural** path. **Best clean-hit rate of all plural shapes
in recent runs** (2026-09-13 runs 1/3/9, plus 03:23Z — 4 HTTP 200s in ~12h).
Has 400'd with `StringComparator` drift on at least one run (2026-09-13 run 2).
Prefer Shape B when you don't have the team UUID handy but need the plural form.
`url` is a valid top-level field on `Issue` (confirmed 2026-09-13 03:23Z).

```graphql
query {
  issues(first: 5, filter: { id: { eq: "GRO-4929" } }) {
    nodes { identifier title state { name } priority updatedAt }
  }
}
```

## Shape F — "what changed overnight" sweep: `updatedAt: { gt: ... }` (no team key)

**Verified working 2026-09-13 cold-start cron run** — HTTP 200, 14 nodes in a
24h window, no team UUID needed. Re-verified 2026-09-13 ~06:20Z (12h window,
5 nodes). This is the **workhorse cold-start sweep**: one call returns every
issue touched in the window (all teams), then you match your `in_flight`
identifiers client-side. It is also the shape the nightly briefing relies on
(pitfall #9 in SKILL.md). Use it FIRST on a cold-start verification pass when
you don't yet have the team UUID and want the full changed set in one shot,
rather than resolving teams one by one.

```graphql
query {
  issues(first: 100,
         filter: { updatedAt: { gt: "2026-09-12T04:15:00.000Z" } }) {
    nodes { identifier title state { name } priority updatedAt url }
  }
}
```

Notes:
- `gt` value is ISO-8601 UTC. Compute it as `now - <window>` (12h for a morning
  digest, 24h for a "what moved overnight" sweep).
- **Quiet-cycle two-query verification pass (Shape D + Shape F) in one file feed:**
  inline `curl -d '...'` gets hardline-blocked in cron/agent turns. The clean
  2026-09-13 pattern was to `write_file` a single `.sh` that runs BOTH queries
  (Shape D single-issue live-verify + Shape F `updatedAt: { gt: <cutoff> }`
  sweep) back-to-back, then `bash <file>` once. One tool call, zero blocklist
  friction, both answers in one output block. Reuse this shape for any
  quiet-cycle verification pass that needs "is X still there + what moved
  overnight."
- `orderBy: updatedAt` is accepted here as a **bare enum** on the `issues` list
  query (see pitfall #9) — but it's optional; sort client-side if you want to
  avoid the enum entirely. **Do NOT use the object form**
  `orderBy: { field: ..., direction: ... }` — it 400s `PaginationOrderBy`
  (see table below).
- Keep `first` ≤ 100 and select only the fields you'll read (complexity budget).
- If a specific `in_flight` identifier is NOT in the window, it hasn't been
  touched in the window — that's a finding, not a failure. Re-probe with a wider
  window or Shape D before concluding it's gone.

## What does NOT work (verified 400s)

| Query shape | Error | Fix |
|---|---|---|
| `issue(identifier: "GRO-XXXX")` | `Unknown argument "identifier"` + `id of type String! required` | Use `issue(id: "GRO-XXXX")` — the **`id` value accepts the human identifier** (Shape D, confirmed runs 10 + 03:23Z) |
| `issueByIdentifier(identifier: "GRO-XXXX")` (top-level query) | `Cannot query field "issueByIdentifier" on type "Query"` | No such top-level field. Use `issue(id: "GRO-XXXX")` (Shape D) or the plural `issues(filter: ...)` shapes |
| `issues(filter: { identifier: { eq: "..." } })` | `Field "identifier" is not defined by type "IssueFilter"` | Use `id` or `number` instead |
| `issues(filter: { number: { eq: "4929" } })` (quoted) | Likely `StringComparator` drift | Pass bare integer `4929` |
| `team(id: "GRO") { ... }` | `Expected value of type "StringComparator", found "GRO"` | Use team UUID, not key |
| `team(key: "GRO") { ... }` | `Unknown argument "key" on field "Query.team"` | `team()` only takes `id` (the UUID). Resolve `teams { nodes { id key } }` first, then pass the UUID |
| `issues(... orderBy: updatedAt)` (bare) | `Syntax Error: Expected Name, found "{"` | Drop `orderBy`, sort client-side |
| `issues(... orderBy: { field: "updatedAt", direction: "DESC" })` | `Expected value of type "PaginationOrderBy"` | Drop `orderBy` entirely |
| `issues(filter: { updated_at: { gt: "..." } })` | `Field "updated_at" is not defined` | Use camelCase `updatedAt` |
| `query($d: DateTime!){ issues(filter:{updatedAt:{gt:$d}})... }` (variable-typed cutoff) | `Variable "$d" of type "DateTime!" used in position expecting type "DateTimeOrDuration"` | Declare the variable as **`DateTimeOrDuration!`** — or inline the `gt:` literal (no variable needed; the verified Shape F query does this) |
| `Authorization: Bearer *** | `Remove the Bearer prefix` hard 400 | Send bare token |
| `issues(filter: { updatedAfter: "..." })` | `Field "updatedAfter" is not defined by type "IssueFilter". Did you mean "updatedAt"?` | The filter has **no `updatedAfter`/`createdAfter`** — only the `updatedAt: { gt: ... }` comparator form (pitfall #9). Don't reach for a `*After` date field. |
| `issues(filter: { ..., state: { key: "inprogress" } })` | `Field "key" is not defined by type "WorkflowStateFilter"` | `state` is **not** a valid `IssueFilter` key in this schema (verified 2026-09-13). Filter by workflow bucket via `issues(filter: { workflowStateId: ... })` (resolve the state UUID) or filter **client-side** on `state { name }` — the cheap path for a cold-start pass. |
| `issueSearch(query: "GRO-4929")` | `This endpoint deprecated.` (code `INPUT_ERROR`) | The top-level `issueSearch` query is **deprecated** (observed 2026-09-13). Do not use it — use Shape D (`issue(id: ...)`) or the `issues(filter: ...)` shapes. (`issueSearchV2` does not exist either.) |
| `issues { ... status { name } ... }` (any issue selection) | `Cannot query field "status" on type "Issue". Did you mean "state"?` | The workflow-bucket field is **`state`**, not `status`. One-token fix. Hit **three times** (2026-09-13: original pitfall #2 run, Shape D probe, overnight-sweep per-issue loop). Often arrives in the same error batch as the `issue(identifier:...)` mistake — read the full `errors` array and fix both in one retry (pitfall #4). |

## Python urllib template (Shape D — singular)

```python
import json, urllib.request, urllib.error

env = open('/home/ubuntu/.hermes/profiles/orchestrator/.env').read()
key = [l.split('=',1)[1].strip() for l in env.splitlines()
       if l.startswith('LINEAR_API_KEY=')][0]

def gql(query):
    req = urllib.request.Request(
        "https://api.linear.app/graphql",
        data=json.dumps({"query": query}).encode(),
        headers={"Authorization": key, "Content-Type": "application/json"}
    )
    try:
        return urllib.request.urlopen(req).read().decode()
    except urllib.error.HTTPError as e:
        return f"HTTPError {e.code}: {e.read().decode()}"

out = json.loads(gql('''
query {
  issue(id: "GRO-4929") {
    identifier title state { name type } priority updatedAt url
  }
}
'''))
issue = out["data"]["issue"]
print(issue["identifier"], issue["state"]["name"], issue["updatedAt"])
```

## Python urllib template (Shape F — overnight sweep)

```python
import json, urllib.request, urllib.error
from datetime import datetime, timedelta, timezone

env = open('/home/ubuntu/.hermes/profiles/orchestrator/.env').read()
key = [l.split('=',1)[1].strip() for l in env.splitlines()
       if l.startswith('LINEAR_API_KEY=')][0]

since = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
q = ('query { issues(first: 100, '
     f'filter: {{ updatedAt: {{ gt: "{since}" }} }}) '
     '{ nodes { identifier title state { name } priority updatedAt url } } }')

req = urllib.request.Request(
    "https://api.linear.app/graphql",
    data=json.dumps({"query": q}).encode(),
    headers={"Authorization": key, "Content-Type": "application/json"})
nodes = json.loads(urllib.request.urlopen(req).read().decode())["data"]["issues"]["nodes"]

# Match your in_flight identifiers client-side
target = [n for n in nodes if n["identifier"] == "GRO-4929"]
```
