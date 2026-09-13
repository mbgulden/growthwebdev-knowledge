# Linear GraphQL issue lookup — working shape (verified live 2026-08-28)

The Linear API surface has drifted; several intuitive shapes are rejected. Record of what failed and what works.

## Working

```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" -H "Content-Type: application/json" \
  -d '{"query":"{ searchIssues(term: \"GRO-3319\") { nodes { identifier url title state { name } } } }"}'
```

Response (real, 2026-08-28):

```json
{"data":{"searchIssues":{"nodes":[{"identifier":"GRO-3319",
  "url":"https://linear.app/growthwebdev/issue/GRO-3319/visibility-deploy-smoke-test-and-verify-prismaticgrowthwebdevcom",
  "title":"[VISIBILITY] Deploy, smoke test, and verify prismatic.growthwebdev.com",
  "state":{"name":"Done - Doc Pending"}}]}}}
```

Notes:
- `url` includes the slug. The slugless form `https://linear.app/growthwebdev/issue/GRO-3319` also resolves (200) — use slugless for composed links, API `url` for quoting.
- Workspace slug for this org: `growthwebdev`.
- `LINEAR_API_KEY` is set in the next-step profile's shell env (and `LINEAR_OAUTH_TOKEN` in the gateway process env on :9000).

## Rejected (do not retry these shapes)

| Shape | Error |
|---|---|
| `issue(identifier: "GRO-3319")` | `Unknown argument "identifier" on field "Query.issue"` (only `id` — a UUID — is accepted) |
| `issues(filter: { identifier: { eq: "GRO-3319" } })` | `Field "identifier" is not defined by type "IssueFilter"` |
| `issueSearch(query: "GRO-3319")` | `This endpoint deprecated.` (HTTP 400, deprecated since before 2026-08) |

Introspection fallback if the API drifts again:

```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" -H "Content-Type: application/json" \
  -d '{"query":"{ __schema { queryType { fields { name args { name } } } } }"}'
# filter fields whose name contains "issue"; searchIssues(term:) is the string-identifier path
```
