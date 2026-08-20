# Linear pagination and owner-label proof

Session lesson: a default `team.labels` query can omit valid labels. In the Phase 2 opaque-workspace issue packet, an initial bounded-but-nonexhaustive label read omitted `agent:agy`, causing a wrong owner fallback. A corrected read with explicit collection bounds returned 97 labels and proved:

```text
agent:agy|1b69d9c0-20a8-45b3-a594-771b8cba75a7
```

## Durable rule

For Linear reads that influence dispatch ownership, label/state existence, duplicate guards, or writer preconditions:

1. Request an explicit bounded page size, normally `first:100`.
2. Read `pageInfo.hasNextPage` for every collection.
3. If `hasNextPage=true`, fail closed or implement reviewed pagination; never treat the page as exhaustive.
4. Bind labels/states by exact display name and stable Linear ID.
5. In writer packets, include the live collection count and exact ID used.
6. Preserve any prior packet that used a nonexhaustive read as `BLOCKED`; do not silently revise it into authorization evidence.

## Minimal GraphQL shape

```graphql
query TeamLabels($teamKey: String!) {
  team(id: $teamKey) {
    labels(first: 100) {
      pageInfo { hasNextPage }
      nodes { id name }
    }
    states(first: 100) {
      pageInfo { hasNextPage }
      nodes { id name type }
    }
  }
}
```

If either collection has `hasNextPage=true`, the safe output is `BLOCKED: collection not exhaustive`, not `label missing` or `state missing`.
