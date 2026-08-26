# Linear GraphQL API patterns (verified 2026-08-21)

Burst-learned this session creating 6 tasks + state updates in one go. The API
rejected ~5 different mutation shapes before settling on the working forms below.
Do not re-derive these from scratch.

## Auth + transport

- Endpoint: `https://api.linear.app/graphql`, header `Authorization: <LINEAR_API_KEY>` (bare key, NOT `Bearer ...`), `Content-Type: application/json`.
- Key lives in `LINEAR_API_KEY` env var on this box.
- ALWAYS catch `HTTPError` and print `e.read().decode()` — the API returns useful GraphQL validation errors in the HTTP 400 body, and a naive `urllib` raise buries them in a traceback.

## Resolving IDs

```graphql
{ teams(first: 10) { nodes { id name } } }
{ projects(first: 20, filter: {name: {contains: "<name>"}}) { nodes { id name } } }
{ users(first: 25) { nodes { id name email } } }
```

Known IDs on this workspace (growthwebdev):
- Team **GRO** = `b6fb2651-5a1f-4714-9bcd-9eb6e759ffef`
- Project **Journal Continuity Audit** = `ece6a786-c1a8-477d-87cb-1fde304e5d4b`
- User **Prismatic Engine (PE bot)** = `ab8a37c8-b5fc-439c-82ea-5a197ac471e4`
- User **Michael Gulden** = `4a8a76b2-63f2-4706-b501-3ab2f0709866`

## Fetching a single issue by human identifier

The SINGULAR `issue(id:)` query works with the human identifier (verified live
2026-08-21, repeatedly — `issue(id: "GRO-4830") { identifier state { name }
team { states { nodes { id name type } } } }` etc.):

```graphql
{ issue(id: "GRO-4830") { id identifier title state { id name } team { id } } }
```

An earlier 2026-08-21 probe reported HTTP 500 for `issue(id:)` with a human id;
it was not reproducible in later sessions — if you ever do hit it, fall back
to the plural `issues` list with an `eq` filter (matches on identifier, returns
empty `nodes` — not an error — when missing):

```graphql
query($i: String!) {
  issues(first: 1, filter: {id: {eq: $i}}) {
    nodes { identifier title state { name } description }
  }
}
```

The singular form is also how you read **team + workflow states in one call**:
`issue(id: "...") { team { states { nodes { id name type } } } }` — no separate
`team(id:)` query needed (the `team` root field REQUIRES an id arg, and the
`states` connection needs the `nodes` wrapper).

## issueCreate (WORKING shape)

```graphql
mutation($t: String!, $d: String!, $team: String!, $proj: String!, $p: Int, $a: String) {
  issueCreate(input: {title: $t, description: $d, teamId: $team, projectId: $proj,
                      priority: $p, assigneeId: $a}) {
    success issue { id identifier url }
  }
}
```

Pitfalls that cost attempts:
1. **`priority` is a plain `Int`** (0=none, 1=low, 2=medium, 3=high, 4=urgent) — NOT `PriorityEnum`.
2. `assigneeId` is nullable String — pass `null` for unassigned (omit or null, not empty string).
3. Description is markdown; Linear renders it. Full context belongs HERE (file paths, line numbers, decision quotes, definition of done) because the assignee (often an agent) reads the task description, not the chat.
4. **`IssuePayload` REQUIRES a subfield selection** (hit live 2026-08-21): bare `issueCreate(input: {...})` → 400 "must have a selection of subfields". `IssuePayload` = `{ success, issue, lastSyncId }` — select `success issue { ... }` (introspect with `__type(name: "IssuePayload")` if in doubt).
5. **Never hardcode `teamId`** — fetch it: `issue(id: "<sibling-issue>") { team { id } }`. A wrong/guessed team id fails validation.
6. **Do NOT select `id`/`identifier` directly on `issueCreate`** → 400 "Cannot query field id on type IssuePayload". They live under `issueCreate.issue { id identifier url }`.

## issueUpdate (WORKING shape)

`id` and `input` are SEPARATE top-level args — not both inside `input`:

```graphql
mutation($id: String!, $s: String!) {
  issueUpdate(id: $id, input: {stateId: $s}) {
    success issue { identifier state { name } }
  }
}
```

Pitfall: `issueUpdate(input: {id: $id, ...})` → HTTP 400 "Field id is not defined by type IssueUpdateInput".

## Comments + parent links (verified live 2026-08-21)

- **Comment mutation is `commentCreate`** (NOT `issueCommentCreate`, NOT
  `createComment`): `commentCreate(input: {body: $body, issueId: "GRO-XXXX"}) { success }`.
  Pass the markdown body as a **variable** (`$body`) — inline string literals in
  the query break on quotes/newlines.
- **Parent link is `issueUpdate(parentId:)`** — the `relationshipCreate`
  mutation does NOT exist in this API version (400 "Cannot query field
  relationshipCreate on type Mutation"). Working shape:
  `issueUpdate(id: "<child>", input: {parentId: "<parent-uuid>"}) { success }`.
  Fetch the parent UUID with `issue(id: "GRO-XXXX") { id }`.
- **Read-back after any create/transition** (never trust the mutation's
  `success` flag alone): re-query `issue(id: "...") { identifier state { name }
  parent { identifier } comments { nodes { body } } }` and assert the state,
  parent, and comment body. This session's "verify" step caught that the
  expected state/PR state had moved (issue closed, PR merged by Michael) — the
  read-back is what tells you the truth.

## Team states (GRO team, verified 2026-08-21)

Query: `{ team(id: "<team-id>") { states(first: 20) { edges { node { id name type } } } } }`
NOTE: `team` REQUIRES the `id` argument (`team { ... }` without id → 400), and
`workflowState` connections don't expose `id`/`name` directly — use `states`.

| State | type | id |
|---|---|---|
| Todo | unstarted | `3d29ebe3-00cf-428b-b52a-bfecb5ae4410` |
| Backlog | backlog | `e5544f55-482e-49ac-b0f7-3dd2e1775dbb` |
| In Progress | started | `734901ee-58f0-457c-b9a0-f911c0da13a4` |
| In Review | started | `6a5050ad-3386-4623-a404-7f2791047cd5` |
| Done | completed | `bbf71b3e-9a05-48ce-9418-df8b9c0b8fec` |
| Canceled | canceled | `a19484ec-9752-4c31-8110-f5043312e328` |
| Duplicate | duplicate | `8a67aa62-ee98-4d67-a513-64217d8859c3` |

(There are TWO "started" types — In Progress and In Review both. Match by name.)

## Assignment limitation (hit live 2026-08-21)

**The app key CANNOT assign issues to the PE bot user** (`ab8a37c8-...`):
`issueCreate` with that assigneeId → HTTP 400 `"App user not valid" ... "One or more app users lack the required scope."`

Resolution: create tasks **unassigned** with full context in the description, then
route them to the owning agent via chat (e.g. Prismatic group message) or have
Michael assign. Do not treat the assignment failure as a blocker for task creation.

## Bulk task creation pattern

Write a script file (`/tmp/linear_*.py`) — do NOT hand-type mutations inline:
1. Define `gql(q, v)` with HTTPError body capture.
2. Define `make(title, desc, priority, assignee=None)` wrapper.
3. One `make()` call per task, sequential (rate-limit safe).
4. Second pass: `issueUpdate` per task to set states (create-then-update, since
   issueCreate doesn't set state).
5. Print every `identifier` returned — record them in the report/handoff.

Reference pattern doc: `prismatic-abandonment-guard-portability/portable-skills/golden-thread/references/linear-bulk-task-creation.md` (team ID + script-first approach) — but it predates the shape fixes above.
