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

## Search fallback

Some schemas do not support `issueSearch(term:)`. If that fails, do not keep retrying the same search. Prefer:

- issue lookup by team key + number when the identifier is known;
- existing title-prefix upsert only if the schema supports the search argument;
- otherwise create a bounded owner-routed issue and document duplicate risk.
