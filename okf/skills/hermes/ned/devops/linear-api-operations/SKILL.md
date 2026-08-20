---
name: linear-api-operations
category: devops
description: Guidelines and best practices for interacting with the Linear API.
---

# Linear API Operations

This skill provides guidance and common patterns for interacting with the Linear API, especially when executed within `execute_code` blocks.

## Trigger Conditions

Use this skill when:
*   You need to fetch Linear issue details (title, description, status, comments, labels).
*   You need to update a Linear issue's state or add comments.
*   You are performing any operation that requires programmatic interaction with Linear.

## API Key Handling (Crucial)

The `LINEAR_API_KEY` is typically stored in `/home/ubuntu/.hermes/profiles/orchestrator/.env`. When executing Python code via `execute_code`, environment variables set in `terminal` calls **do not persist**. Therefore, you must explicitly read the `.env` file within your `execute_code` block.

**Authentication:** The Linear API expects the API key *directly* in the `Authorization` header, **without** the `Bearer` prefix. Using `Bearer` will result in an `HTTPError 400` (not 401) with a specific message: `"It looks like you're trying to use an API key as a Bearer token. Remove the Bearer prefix from the Authorization header."` Strip the prefix and retry — no other fix is needed. This is a one-line diagnosis, do not chase it as a malformed request.

**Example of reading `LINEAR_API_KEY` in `execute_code`:**

```python
import os
import requests
import json

def load_env_vars(env_file_path):
    env_vars = {}
    try:
        with open(env_file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    env_vars[key] = value
    except FileNotFoundError:
        print(f"Warning: .env file not found at {env_file_path}")
    return env_vars

env_file = "/home/ubuntu/.hermes/profiles/orchestrator/.env"
loaded_env = load_env_vars(env_file)
linear_api_key = loaded_env.get("LINEAR_API_KEY")

if linear_api_key:
    # Proceed with API call
    headers = {
        "Authorization": linear_api_key, # IMPORTANT: No "Bearer " prefix
        "Content-Type": "application/json",
    }
    # ... rest of your API call logic
else:
    print("LINEAR_API_KEY is not set in the .env file.")
```

## GraphQL Query Pattern

When constructing GraphQL queries for the Linear API, ensure proper formatting and
escaping. Using the `requests` library with a multi-line string for the GraphQL
query is the most robust approach.

**Example of fetching issue details:**

```python
# ... (API key loading as above)

if linear_api_key:
    # Use `id` (UUID), not `identifier` (GRO-XXXX) — `id` is the only filter field.
    issue_id = "abc-123-..."   # resolve via a separate lookup if you only have an identifier
    graphql_query = f"""
    query {{
      issue(id: "{issue_id}") {{
        title
        description
        state {{ name }}
        labels {{ nodes {{ name }} }}
        comments(last: 5) {{ nodes {{ body createdAt user {{ name }} }} }}
      }}
    }}
    """
    # ...
```

For Linear's `IssueFilter` type, the fields available include `id`, `state`,
`priority`, `label`, `project`, `cycle`, `parent`, `assignee`, `createdAt`,
`updatedAt`, `completedAt`, `dueDate`, `title`, and `identifier` (sub-filter
on the `Comparable` form). The older skill text claiming `title` and
`identifier` were NOT filterable is stale — the live schema DOES accept
them (verified 2026-07-31 via `__type(name: "IssueFilter")` introspection).
Useful filter shapes:

- `filter: { title: { contains: "PE-KPI-FUNNEL" } }` — search by title prefix
  or substring. **This is the right way to find a task set that uses a
  bracket-prefix tag like `[PE-KPI-FUNNEL]` when there is no Linear project
  container.** See `references/linear-title-prefix-search.md`.
- `filter: { identifier: { in: ["GRO-4367", "GRO-4368"] } }` — DO NOT rely on
  this: it returned `400 Field "identifier" is not defined by type "IssueFilter"`
  on the live GrowthWebDev workspace 2026-08-15 (the earlier claim it works is
  stale/wrong). Use the `issue(id:)` loop instead.
- `filter: { id: { in: [...] } }` — always safe; resolves by UUID.

If `identifier` filter returns 400, prefer the `id`-based loop pattern. The
`title` filter is the right tool when the only signal is a tag prefix in
the title.
        "Authorization": linear_api_key,
        "Content-Type": "application/json",
    }
    payload = {"query": graphql_query}

    try:
        response = requests.post("https://api.linear.app/graphql", headers=headers, json=payload)
        response.raise_for_status()
        print(json.dumps(response.json(), indent=2))
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Linear issue: {e}")
```

### Pitfalls

* **`LINEAR_API_KEY` not available in `execute_code` (especially in cron jobs):** Always read the `.env` file directly as shown above if it's available. For cron jobs, ensure the `LINEAR_API_KEY` is explicitly set in the cron environment, as it will not be inherited from the user's shell or other Hermes profiles automatically. `export` from `terminal` does not carry over to `execute_code` or subsequent cron runs.
* **`Bearer` prefix in `Authorization` header:** The Linear API explicitly rejects this. Remove it.
* **GraphQL Query Syntax:** Pay close attention to curly braces, quotation marks, and field names. Start with simpler queries and add complexity incrementally if you encounter `400 Bad Request` errors.
* **`finalize_task.sh` state transition behavior:** Be aware that the `finalize_task.sh` script, when used without explicit state arguments, might default to a 'In Review' state transition. If a specific state (e.g., "Todo" for a blocked issue) is required, verify the script's behavior or explicitly use the Linear API to set the desired state after the script runs, as observed in this session. To set a specific state via the Linear API, first, fetch the `workflowStates` to get the correct `stateId` for your target state (e.g., "Todo").
* **Mutation input shape (`issueCreate`, `issueUpdate`, `commentCreate`):** All three mutations take an `input:` argument of an `*Input!` type — they do NOT accept top-level arguments like `id`, `issueId`, `body`. The correct shape is:
    ```graphql
    mutation($input: IssueCreateInput!) { issueCreate(input: $input) { success issue { identifier url } } }
    mutation($id: String!, $input: IssueUpdateInput!) { issueUpdate(id: $id, input: $input) { success } }
    mutation($input: CommentCreateInput!) { commentCreate(input: $input) { success } }
    ```
    Passing `commentCreate(issueId: ..., body: ...)` produces `GRAPHQL_VALIDATION_FAILED: Unknown argument "issueId"` and `Unknown argument "body"` plus `Field commentCreate argument "input" of type CommentCreateInput! is required, but it was not provided.` The fix is to wrap both fields in `input: {issueId: ..., body: ...}`. Same pattern for `issueCreate` — never assume flat arguments.
* **`commentUpdate` is the asymmetric one — it takes BOTH `id` AND `input` as separate top-level args, NOT just `input`:** the mutation signature is `commentUpdate(id: String!, input: CommentUpdateInput!)`. This is different from `commentCreate` (which only takes `input`). Calling `commentUpdate(input: {id: ..., body: ...})` returns `Field commentUpdate argument "id" of type String! is required, but it was not provided.` Correct shape:
    ```graphql
    mutation($id: String!, $input: CommentUpdateInput!) {
      commentUpdate(id: $id, input: $input) { success }
    }
    ```
    with `input = {body: "..."}` (no `id` inside input). The asymmetry between `commentCreate(input)` and `commentUpdate(id, input)` is the kind of inconsistency the Linear API inflicts on agents; introspect the schema once per session with `__type(name: "Mutation") { fields { name args { name type { kind } } } }` and the pitfall disappears.

* **`issueRelationCreate` with type `blocks` — the direction is the OPPOSITE of what the natural reading of the field names suggests, and is the single most common reason a blocking chain is built backwards.** The mutation takes `issueId` and `relatedIssueId` as separate fields. The semantic is: **`issueId` is the thing doing the blocking** — it must be completed first; `relatedIssueId` is the thing that must wait. So to wire an execution chain where step N must finish before step N+1 starts, the call is:
    ```graphql
    issueRelationCreate(input: {
      issueId: "<N+1_id>",          # the LATER step is the one being blocked
      relatedIssueId: "<N_id>",     # the EARLIER step is the one doing the blocking
      type: "blocks",
    })
    ```
    **Why this is counterintuitive:** the field name "relatedIssueId" suggests "the related (later) thing" but Linear inverts that — `relatedIssueId` is the BLOCKER. If you write the call as `issueId: "<earlier>", relatedIssueId: "<later>"`, you are telling Linear "the earlier step blocks the later step" — which is correct in English — but **Linear will create the relation in the opposite direction in the dependency DAG**, because the API treats `issueId` as the thing that owns the relation (and therefore the thing that must complete first). Verified via live API 2026-08-04: I built a 9-issue chain (1 umbrella + 8 children) and got the direction wrong twice in a row, having to delete and recreate all 15 relations both times.

    **Mnemonic that always works:** "issueId is the parent in time, relatedIssueId is the child." Pass the LATER step's id as `issueId`, the EARLIER step's id as `relatedIssueId`. Equivalently: the relation's *outbound arrow* points from `issueId` to `relatedIssueId`, but in the Linear UI "blocks" arrows point *into* the blocked item — so `issueId` ends up being the thing with the arrow leaving it, which means it's the one that must finish first.

* **Verifying the direction of a whole blocking chain, not just a single relation.** The single-relation rule is half the trap — the other half is that an agent who gets one relation backwards in a chain will systematically get all of them backwards the same way. After building any chain (or umbrella+children setup), run this verification on **the first child, the last child, and the umbrella** — if any of these reads inverted, the entire chain is wrong and must be rebuilt:

    ```graphql
    query($id: String!) {
      issue(id: "<id>") {
        relations { nodes { type relatedIssue { identifier } } }
        inverseRelations { nodes { type issue { identifier } } }
      }
    }
    ```

    For the **FIRST child** in the chain, expect:
    - `relations` (what it blocks) — `[]`
    - `inverseRelations` (what blocks it) — `[]`

    For the **LAST child** in the chain, expect:
    - `relations` — `[<umbrella_id>]`  (because the last child also blocks the umbrella)
    - `inverseRelations` — `[<previous_child_id>]`

    For the **UMBRELLA**, expect:
    - `relations` — `[]`
    - `inverseRelations` — `[<all_children_ids>]`

    If the FIRST child shows anything in its `inverseRelations` other than empty (other than the umbrella), the chain direction is backwards. The umbrella having anything in `relations` (other than empty) means the children are blocking the umbrella backwards — every relation needs to be deleted and recreated with the parameters swapped. Do NOT try to "fix forward" by adding more relations — delete the wrong ones by UUID and re-issue the correct calls. Sleep 0.2s between deletes to stay under Linear's ~50 writes/minute rate limit (HTTP 400 with `RATELIMITED` body).

* **Deleting a wrongly-directed `blocks` relation requires the relation's UUID, not the issue IDs.** `issueRelationDelete(id: "<relation_uuid>")` is the only way to remove a relation. Find the relation id by querying either endpoint: `issue(id: "<A>") { relations { nodes { id type relatedIssue { identifier } } } }` returns relations where A is `issueId`; `inverseRelations` returns relations where A is `relatedIssueId`. To clean up a whole batch of wrong-direction relations from a script: query all issues in the batch, collect `relations.nodes[].id` for type=blocks, then loop `issueRelationDelete` on each. Linear's rate limit (HTTP 400 with `RATELIMITED`) kicks in around 50+ writes per minute — sleep 0.2s between deletes and you're fine.

* **No-op project description retries.** `projectCreate` enforces `description <= 255 chars` strictly. The error path is an `Argument Validation Error` with `property: "description"` and the exact length constraint. If your description is long, truncate before sending — don't try to set `description: null` first and update later, because the create still rejects. Plan the description to fit in 255 chars from the start, or split long content into a Linear *doc* linked from a shorter project description.

* **`Project` GraphQL type does NOT have a `key` field.** Querying `{ project { id name key url } }` returns `400 GRAPHQL_VALIDATION_FAILED: Cannot query field "key" on type "Project"`. Project has only `id`, `name`, `url`, `description`, `state`, `targetDate`, `startDate`, etc. If you need a human-readable short tag, use `state` (which is an enum like `planned`/`started`/`backlog`/`completed`) — there's no `GRO-XXXX`-style project key in Linear's data model.
* **`workflowStates` is global (no team filter):** Query it directly with `query { workflowStates { nodes { id name type } } }`. The team filter that Linear docs sometimes suggest is not required to enumerate states for the agent's workspace. Pick the one matching `{name: "Todo", type: "unstarted"}` (state ID looks like `3d29ebe3-00cf-428b-b52a-bfecb5ae4410`).
* **`issueLabels(filter:{name:{eq:$name}})` returns 0 or 1 node per exact match.** When applying labels by name in code, store the returned `id` and pass it via `input.labelIds` on `issueUpdate` — do not invent UUIDs.
* **Naming projects:** Use the project name exactly as it appears (e.g., `HD Engine Core`, not `HDE Core`). A `filter:{name:{eq:$name}}` that misses returns an empty list and your `nodes[0]` will throw `IndexError`. Query the project list first if unsure.
* **`comments(last: N)` silently drops comments older than the Nth most recent:**
    if you create a comment via `commentCreate` and then query `comments(last: 3)` on
    an issue that already has 5 older comments, your newly created comment may NOT
    be in the result. This is the depth-of-listing trap. For any verifier that needs
    to confirm "did this comment land?" either:
    1. Use `comments(last: 20)` (or higher) to be safe; or
    2. Filter by `createdAt` substring (e.g. `'2026-07-28' in c['createdAt']`); or
    3. Match by exact body prefix (`(c['body'] or '').startswith('PR-batch close:')`)
       — every verbatim match wins against recency-order surprises.
    This is the single most common false-negative in Linear-state verifiers and was
    hit repeatedly during the HDE reconciliation packet work.
- **Finding an issue by GRO-XXXX — the `IssueFilter` does NOT accept `identifier` as a top-level filter field.** `filter: { identifier: { eq: "GRO-4463" } }` returns `400 GRAPHQL_VALIDATION_FAILED: Field "identifier" is not defined by type "IssueFilter"`. **Re-verified 2026-08-15: the batch form `filter: { identifier: { in: [...] } }` is ALSO rejected with the same 400** — the earlier note claiming the `in:` form works is wrong for the live workspace. Two working alternatives:
  1. **Use the `issue(id: "...")` query directly** with the identifier string. `issue(id: "GRO-4463") { id title state { name } }` works — `issue(id:)` accepts both UUIDs and identifier strings (unlike the `IssueFilter` type, which only accepts UUIDs). This is the fastest lookup when you already know the identifier.
  2. **Filter by `team` + `number`** with the right variable types: `query($teamId: ID!, $number: Float!) { issues(filter: { team: { id: { eq: $teamId } }, number: { eq: $number } }) { nodes { id identifier } } }`. Two gotchas in this shape: the `teamId` variable MUST be declared `ID!` (not `String!` — Linear distinguishes UUID-shaped IDs from arbitrary strings at the type level), and the `number` variable MUST be `Float!` (not `Int!`). Verified via live API 2026-08-04.

- **`IssueFilter` filter set is wider than this skill's older text claims.**
    The notes that "`title` and `identifier` are NOT filterable" are stale as
    of the 2026-07-31 introspection. The live API accepts:
    - `filter: { title: { contains: "PE-KPI-FUNNEL" } }` ✓
    - `filter: { identifier: { in: [...] } }` ✗ — rejected live 2026-08-15 (see
      the earlier `IssueFilter` pitfall). Do not use.

    If a query against these fields returns 400, introspect first
    (`{ __type(name: "IssueFilter") { inputFields { name } } }`) — the schema
    has evolved. The agent-friendly pattern for a small set of known IDs is
    still `query($id:String!){issue(id:$id){...}}` in a loop, but for "find
    all tasks carrying a tag prefix in their title" the title filter is the
    right tool. See `references/linear-title-prefix-search.md`.

* **Bracket-prefix tags in titles are NOT Linear projects or labels.**
    `[PE-KPI-FUNNEL]` looks like a project container label but is just a
    title prefix shared across 12 tasks. There is no Linear project entity
    named "PE-KPI-FUNNEL" and no `Linear label` with that name. If you
    search for it via `filter: { project: { name: { contains: "PE-KPI" } } }`
    or `filter: { labels: { some: { name: { eq: "PE-KPI-FUNNEL" } } } }` you
    get zero results and conclude the tasks don't exist. **Always probe
    with a title-prefix filter first when the tag text is in brackets at
    the start of an issue title.** Two falsy probes cost time; one
    `title: { contains: <prefix> }` resolves it.
* **`WorkflowState` does NOT have a `title` field.** It has `type`, `name`, `position`.
    A `state { name title }` query returns `400 Bad Request: Cannot query field "title"
    on type "WorkflowState". Did you mean "type"?`. Use `name` to identify states
    and `type` to bucket them (unstarted/backlog/started/completed/canceled).
* **Verification strings against Linear titles/descriptions are fragile when the text contains Markdown formatting.** Linear titles and descriptions often contain backticks (`` `zapier-sdk` ``), asterisks (`*bold*`), or other Markdown. A naive substring search like `"zapier-sdk shell alias"` (literal, no formatting) will fail against a title like `` Add `zapier-sdk` shell alias + per-host README `` even though the underlying words are present. When writing ad-hoc verifiers that confirm a task was created with the right content, search for **individual keywords** (each in `title.lower()`) rather than multi-word literal substrings. Example pattern for verifying a task title:

    ```python
    expected_kw = {"GRO-4374": ["zapier-sdk", "alias"]}
    for ident, words in expected_kw.items():
        title_lc = issue["title"].lower()
        present = all(w in title_lc for w in words)
        assert present, f"{ident} missing keywords {words} in {issue['title']!r}"
    ```

    This is roughly the rule "robust keyword set vs. brittle multi-word substring." Hit during the 2026-07-29 Zapier-task-creation turn when the verifier failed on GRO-4374's backticked title even though the keywords were present.

- **`commentCreate` returning `success: true` is necessary but not sufficient proof the
    comment is observable.** Combine with one of the comment-listing assertions above
    before reporting "comment posted". The API occasionally accepts a `commentCreate`
    and returns `success: true` while the comment is not yet queryable from the same
    connection; re-fetch with a short delay or use the `comments(last: 20)` plus
    body-prefix filter for the resilient pattern.

- **`parentId` on `issueCreate` requires the parent's UUID, not its identifier.** The mutation
    input field is `parentId: ID` (UUID-shaped). Passing `parentId: "GRO-4367"` returns
    `400 GRAPHQL_VALIDATION_FAILED: ID! mismatch error` because identifier strings
    (`GRO-XXXX`) and UUIDs are different ID shapes in Linear's eyes. The pattern is:
    look up the parent first (`{ issue(id: "GRO-4367") { id } }`), then pass the
    returned UUID as `parentId`. The same applies to `issueUpdate` for reassigning
    parent. The asymmetry between `issue(id: "GRO-XXXX")` (accepts the identifier)
    and `input.parentId` (requires UUID) is the trap — both are "issue IDs" in
    conversation but the API distinguishes them.

- **`issueCreate` allocates the next free identifier, not the one you hint.** If you
    pass `identifier: "GRO-4377"` in the input, Linear ignores it (the field is not
    writable on `IssueCreateInput`) and returns whatever the next free ID happens
    to be. In a busy team with concurrent actors (other agents, humans, the
    orchestrator), the next free ID is NOT predictable. Hit during 2026-07-31 KPI
    task decomposition: 12 tasks were filed with hints `GRO-4377..GRO-4388`, but
    Linear allocated `GRO-4382..GRO-4393` because GRO-4377..GRO-4381 were taken by
    concurrent Move 15–19 cleanup work that landed between my read and write.
    **Always read the returned `issue.identifier` from the create response and
    verify it matches what you planned to file. If you need the canonical list in
    a follow-up comment, post the *actual* identifiers that landed, not the planned
    ones.** And never assume two consecutive `issueCreate` calls will land at N and
    N+1 — read back the returned identifier, advance the pointer from that, not
    from a separate counter.

- **Agent routing labels (`agent:ned`, `agent::fred`, `agent:kai`) are labels, not assignees.**
    The Linear teams use these labels as the dispatch routing convention instead of
    the `assigneeId` field. When the user says "assign to agent:ned" the right move
    is `input.labelIds: [agent:ned_id]`, NOT `input.assigneeId: <ned_uuid>`. There
    is no Linear user named `ned`; setting `assigneeId` to a fake UUID returns 400
    and setting it to a real-but-wrong user silently routes the task to that
    person. Concretely: `agent:ned` id `6e0400c9-fc04-4868-86e3-f3156821f413`,
    `agent::fred` id `ee18e998-7155-4910-a5a1-c6a692038ffa`, `agent:kai` id
    `c4d929be-8d15-4482-b6d7-a5ed85aa2e73`. The full label list is enumerable via
    `{ issueLabels(first: 200) { nodes { id name } } }`. The same convention shows
    up in `next-action-truth-source` — the registry mirrors these labels, not
    `assigneeId`.

* **`StringComparator` field is `containsIgnoreCase`, NOT `containsCaseInsensitive`.**
    The old name was retired at some point and the live API now returns
    `400 GRAPHQL_VALIDATION_FAILED: Field "containsCaseInsensitive" is not defined by
    type "StringComparator"`. Confirmed via introspection of the live schema (probe:
    `{ __type(name: "StringComparator") { inputFields { name type { name kind } } } }`).
    The full list of valid StringComparator fields is:
    `eq`, `neq`, `in`, `nin`, `eqIgnoreCase`, `neqIgnoreCase`, `startsWith`,
    `startsWithIgnoreCase`, `notStartsWith`, `endsWith`, `notEndsWith`, `contains`,
    `containsIgnoreCase`, `notContains`, `notContainsIgnoreCase`,
    `containsIgnoreCaseAndAccent`. If a query references a name not in this list,
    introspect first — the Linear API silently renames comparator fields and breaks
    existing client code without a version bump.

* **Newly-created issues land in `state: "Backlog"`, not `Todo`.** When a fresh issue is created
    via `issueCreate`, the default Linear team workflow may have two unstarted states
    (`backlog` and `unstarted` / `Todo`). The new issue lands in `Backlog` (state_type
    `backlog`) by default — the difference is team-configuration-driven. If a UI
    component (e.g. a status pill) renders colors based on `state.name`, it will
    misclassify `Backlog` as a different bucket than `Todo`. **Always key color/CSS
    classes on `state_type` (the canonical bucket: `backlog | unstarted | started
    | completed | canceled | triage`), never on `state.name` (the team-localized
    label).** The two are different fields and the Linear team workflow customization
    UI makes `state.name` opaque. The 2026-07-30 Phase 4.4 dashboard verifier caught
    this in the wild: GRO-4367 was rendered with `state_type=backlog` and the
    `pwp-kpi-linear-status-backlog` CSS class. The `state` field is for human
    display only; the `state_type` field is for programmatic bucketing.

## References

- `references/linear-title-prefix-search.md` — when a project tag like
  `[PE-KPI-FUNNEL]` is a title prefix rather than a Linear project entity
  or label, the title-prefix filter is the right tool. Includes the exact
  GraphQL query, the falsy-filter traps to avoid, and the introspection
  recipe for confirming the live schema.
- `references/2026-07-hde-analytics-extraction-linear-pitfalls.md` — session-specific
  pitfalls hit during the HDE analytics extraction (2026-07-28): verified comment
  prefix, `comments(last: 50)` filter, `IssueFilter` not accepting `identifier`,
  `WorkflowState` not having `title`, and the multi-comment timeline pattern used
  to land drift + ready-to-push notes on every parent.
- `references/idempotent-epic-and-child-task-creation.md` — reusable pattern for
  spinning up a Linear epic + N child tasks in a way that's safe to re-run.
  Covers find-before-create, parent-scoped child search, label-id resolution,
  the four-step probe recipe (viewer/teams/labels/existing-issues), and
  re-submit semantics (find+comment vs find+reopen). Used to bootstrap
  PE-KPI-FUNNEL (GRO-4356 + 10 children) in 2026-07.
