# Linear bulk phased project creation — lessons from PWP Theme tree

Use this when turning a master plan into phased Linear epics + child issues.

## Pattern

1. Read the source plan and derive the full tree before creating anything.
2. Create one parent issue per phase, labeled `epic`, `plugin:pwp`/domain label, `prismatic-engine`, and the coordinating agent label.
3. Create child issues with `parentId`, explicit priority, correct agent lane labels, and acceptance criteria.
4. If the user says they will initiate the build later, keep issues in `Todo` and **do not** add `dispatch:ready`.
5. Make issue creation idempotent by exact-title lookup before `issueCreate`.
6. After creation, query by a shared title prefix (e.g. `[PWP Theme`) and verify: parent count, child count, parent links, state, labels, and priorities.

## Pitfalls observed

### Duplicate label IDs are rejected

Linear rejects `issueCreate` when `labelIds` contains duplicates:

```text
Argument Validation Error: All labelIds's elements must be unique.
```

Always de-duplicate label IDs while preserving order before sending the mutation.

### Hourly Linear rate limit can interrupt a large tree

Bulk creation can hit:

```text
Rate limit exceeded. Only 2500 requests are allowed per 1 hour.
```

Do not mark the project complete when this happens. Verify the partial tree, report what exists, then schedule a one-shot no-agent resume script after the reset window. The resume script should be idempotent and only create missing phases/children.

### Query shape that worked

For discovery/verification, prefer variables with `containsIgnoreCase` rather than embedding bracket-heavy titles inline:

```graphql
query($term:String!) {
  issues(first:100, filter:{ title:{ containsIgnoreCase:$term } }) {
    nodes { id identifier title url parent { identifier } state { name } priority }
  }
}
```

Inline title strings containing brackets/quotes are easy to break. Variables avoid that nonsense.

## Completion wording

If rate limited mid-run, say exactly what is complete and what is scheduled. Do not tell Michael the full tree is ready until all phases and children are verified.