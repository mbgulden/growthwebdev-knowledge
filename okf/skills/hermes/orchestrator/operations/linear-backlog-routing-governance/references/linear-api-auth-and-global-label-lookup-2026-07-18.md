# Linear API auth and label lookup quirks (2026-07-18)

Use this when a routing/remediation task needs direct Linear GraphQL calls from Hermes/terminal.

## Auth header rule

Linear accepts different header shapes depending on credential type:

- Raw Linear API key: `Authorization: <LINEAR_API_KEY>` — do **not** prefix with `Bearer`.
- OAuth access token: `Authorization: Bearer <token>`.

A raw API key with `Bearer` can fail with:

```text
It looks like you're trying to use an API key as a Bearer token. Remove the Bearer prefix from the Authorization header.
```

## Query-shape rule

Before a mutation batch, validate a minimal issue lookup:

```graphql
query {
  issues(filter: {team: {key: {eq: "GRO"}}, number: {eq: 120}}, first: 1) {
    nodes { identifier title state { name type } }
  }
}
```

Then move to multiline nested queries. Avoid dense one-line GraphQL when requesting nested `labels`, `project`, `assignee`, and `state`; brace errors are easy and Linear may return a 500/GraphQL syntax body.

## Label lookup rule

Routing labels such as `agent:agy`, `dispatch:ready`, and `engine_consumable` may be workspace-global labels, not team-local labels. If `teams { labels { ... } }` does not return them, query:

```graphql
query {
  issueLabels(first: 250) { nodes { id name } }
}
```

Use those IDs for `IssueUpdateInput.labelIds`.

## GraphQL payload via shell: never inline `id: "GRO-4797"` in a curl one-liner (2026-08-20)

GraphQL `issue(id: "GRO-4797")` (and any field with an escaped-quoted string argument) is fatal in a bash double-quoted heredoc/one-liner — `\"` gets mangled by shell expansion and curl dies with `syntax error near unexpected token '('` before it ever reaches Linear. Observed 2026-08-20: the same query worked perfectly once written to a file.

**Recipe:** `write_file` a JSON payload, then send it:

```bash
# /tmp/gro4797.json  (no shell quoting involved)
{"query": "{ issue(id: \"GRO-4797\") { identifier title url state { name } description } }"}

curl -s https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d @/tmp/gro4797.json
```

`-d @file` is the fix; inline `'{...}'` is the failure mode.

**Schema note:** `pullRequests` is NOT a field on the `Issue` type (GraphQL validation error 2026-08-20). For PR lookups, query the GitHub branch (`branchName` field works on Issue) or search PRs via the GitHub API instead of retrying the Linear schema.

## Search fallback

Some schemas do not support `issueSearch(term:)`. If that fails, do not keep retrying the same search. Prefer:

- issue lookup by team key + number when the identifier is known;
- existing title-prefix upsert only if the schema supports the search argument;
- otherwise create a bounded owner-routed issue and document duplicate risk.
