# Linear comment-ID verification after finalize

When `finalize_task.sh` or a manual evidence-refresh mutation posts a Linear comment, do not rely only on `comments(last:N)` to prove the comment landed. In the GRO-4007 refresh, `commentCreate` returned `success=true` and a concrete comment id (`5107394f-ac7b-4d67-8030-c441baddd712`), but a follow-up `comments(last:2)` query still returned older finalization comments and omitted the just-created evidence refresh.

Durable pattern:

1. Capture the `comment.id` returned by `commentCreate`.
2. Verify that specific object directly:

```graphql
query($id: String!) {
  comment(id: $id) {
    id
    createdAt
    body
    issue { identifier }
  }
}
```

3. Use `comments(last:N)` only as secondary context/windowing evidence, not as authoritative proof that a known returned comment exists.

This avoids false “comment missing” escalations after a successful evidence-refresh mutation, especially during redispatch/finalize loops where several Ned finalization comments already exist on the issue thread.
