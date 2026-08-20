# Linear API Gotchas — Session Lessons (2026-07-26)

A condensed knowledge bank of Linear GraphQL API quirks that bite during `linear-handoff-build-out` runs. Each entry is paired with the symptom, the fix, and the verifier check that catches it next time.

## 1. State is a UUID, not a name

**Symptom:** `issueCreate` / `issueUpdate` returns `HTTP 400: Bad Request` when you pass `state: "Todo"`.

**Why:** Linear's `IssueUpdateInput.state` accepts a workflow-state UUID, not a name. The names ("Todo", "In Progress", "Backlog") are display strings; the API needs the UUID.

**Fix:** Query the workspace's workflow states first:

```graphql
query {
  workflowStates(filter: { team: { id: { eq: "<TEAM_ID>" } } }) {
    nodes { id name type position }
  }
}
```

Cache the UUIDs and use `stateId` (not `state`) on every mutation.

**Verifier check:** build-time sanity check that every `stateId` used in the script exists in the cached workflow states map.

## 2. Label IDs must be resolved before use

**Symptom:** `issueCreate` returns `HTTP 400: Bad Request` or `errors: "Invalid label ID"` when you pass label names.

**Why:** `IssueCreateInput.labelIds` (and the `IssueUpdateInput.labelIds`) accept Linear label UUIDs, not names. Labels are workspace-scoped.

**Fix:** Query all labels once at the start:

```graphql
query {
  issueLabels(first: 100) {
    nodes { id name color }
  }
}
```

Build a `{name: id}` map. If a label you need does not exist, create it with `issueLabelCreate` (the new ID is returned).

**Verifier check:** every `agent:*`, `dispatch:*`, `type:*` label used in the script must appear in the label map before mutation. If it doesn't, the build-out script must fail loudly (no silent fallback to creating labels mid-mutation, which pollutes the workspace).

## 3. Multi-line description bodies cause HTTP 400

**Symptom:** `issueCreate` returns `HTTP 400: Bad Request` when the description string contains literal `\n` characters that the JSON parser interprets as real newlines.

**Why:** Linear's GraphQL endpoint rejects description bodies with embedded raw newlines. The fix is to encode the description as a JSON-escaped string (`\\n`) so the JSON body itself is single-line but the resulting Markdown renders with line breaks.

**Fix:** Build the description as a Python string using `\n` escape sequences (NOT real newlines):

```python
desc = (
    "PARENT EXIT CRITERION (verbatim): ...\n\n"
    "EPIC EXIT CRITERION (verbatim): ...\n\n"
    "FIRST STEP: ..."
)
body = json.dumps({"query": mut, "variables": {"input": {"description": desc, ...}}}).encode()
```

**Verifier check:** the seven-field description shape must be a single Python string with `\n` escapes, not a multi-line literal.

## 4. Rate limiting — sleep 30s and retry

**Symptom:** `errors[0].extensions.code == "RATELIMITED"`.

**Why:** Linear's API rate-limits per-token, per-team. Bulk epic/task creation routinely trips it.

**Fix:** Catch the code; sleep 30 seconds; retry the same mutation. Don't fall back to no-op or partial-completion silently.

```python
for attempt in range(4):
    try:
        resp = urllib.request.urlopen(req, timeout=20).read().decode()
        data = json.loads(resp)
        errs = data.get("errors") or []
        if errs:
            code = errs[0].get("extensions", {}).get("code", "")
            if code == "RATELIMITED":
                time.sleep(30)
                continue
            return data
        return data
    except Exception:
        time.sleep(2)
raise RuntimeError("gql failed after retries")
```

**Verifier check:** post-batch readback confirms every expected identifier exists. If any is missing, the rate-limit retry loop must continue, not declare done.

## 5. Loading the API key from a dotenv file inside `execute_code`

**Symptom:** `KeyError: 'LINEAR_API_KEY'` even though the key is in the active shell.

**Why:** `execute_code` runs in a fresh sandbox per call. It does NOT inherit `os.environ` from prior `terminal()` calls. You must re-load the key inside every `execute_code` block:

```python
for src in ["/home/ubuntu/.hermes/profiles/fred/.env"]:
    if os.path.exists(src):
        for line in open(src):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                if k.strip() == "LINEAR_API_KEY" and v.strip():
                    os.environ[k.strip()] = v.strip()
key = os.environ["LINEAR_API_KEY"]
```

**Verifier check:** the first call in a multi-step batch must include the dotenv-load block; subsequent calls in the same session can reuse the cached env if the sandbox persists (it usually does within one logical session).

**Security pitfall:** never print or log the key value. Audit-log only the first 12 characters + `"..."` to confirm the right credential loaded.

## 6. `parentId` is the issue UUID, not the identifier

**Symptom:** `issueCreate` succeeds but the child lands at the top level instead of nested under the parent.

**Why:** `IssueCreateInput.parentId` is the parent issue's UUID, not its identifier like `GRO-4214`.

**Fix:** Walk the parent → children tree once at the start of the build-out, capture `{identifier: uuid}` for every epic, then pass `parentId=uuid` to the child task mutation.

```python
q = "query($id: String!) { issue(id: $id) { children(first: 10) { nodes { id identifier title } } } }"
# walk recursively
```

**Verifier check:** post-batch readback confirms the parent → child nesting in the live GraphQL response.

## 7. Title prefix matters for label-driven routers

**Symptom:** Dispatcher ignores an issue because no agent label matches, even though the description says it's for `ned`.

**Why:** PE's dispatcher keys off Linear labels, not title text or description content. A task titled `[JOURNAL-STORAGE-01] Add pe/journal/storage/...` looks like a fred task if it's only labeled `agent:fred`; it has to actually carry `agent:ned` to land on ned's queue.

**Fix:** the seven-field build-out script must attach the per-task owner label from `TASK_META[ident]["owner"]`, never the parent epic's owner.

**Verifier check:** every child task's label list contains exactly one `agent:*` and that label matches the owner field in `TASK_META`.

## 8. Verification before mutation — never skip the dry-run

Always run these queries before any mutation, in this order:

1. `viewer { id name email }` — confirms auth.
2. `teams { nodes { id name key } }` — confirms team UUID.
3. `workflowStates(filter: { team: ... }) { nodes { id name } }` — captures state UUIDs.
4. `issueLabels(first: 100) { nodes { id name } }` — captures label UUIDs.

Cache all four results. Only then start `issueCreate`. If any of the four fails, abort the build-out and surface the auth/permission failure to Michael — do not silently skip or fall back.

## 9. Post-batch readback — the truth is in the live response

After the batched mutation, run a final GraphQL query that walks the full tree:

```graphql
query($id: String!) {
  issue(id: $id) {
    identifier title state { name }
    children(first: 10) {
      nodes {
        identifier title state { name }
        labels(first: 5) { nodes { name } }
        description
        children(first: 10) {
          nodes { identifier title state { name } labels(first: 5) { nodes { name } } description }
        }
      }
    }
  }
}
```

Verify against the build-out plan:

- 1 parent + N epics + M tasks.
- All in `Todo`.
- All labels present.
- All seven fields in every task description.

If any check fails, the build-out is incomplete. Patch the missing piece and re-run. Don't declare done on a partial result.

## 10. The "audit prefix" pattern for credential logging

When you must prove a credential loaded correctly without exposing it, log only the first 12 characters:

```python
audit = key[:12] + "..."
print(f"audit_prefix={audit}")
print(f"viewer={data['data']['viewer']['name']}")
```

**Verifier check:** the audit prefix is enough to confirm "the right credential loaded" without leaking the value into session transcripts or git diffs.

## 11. Auto-numbering is sequential, not gap-resumable

**Symptom:** the build-out plan names expected identifiers like `GRO-4373, GRO-4374, GRO-4375, GRO-4376` but `issueCreate` returns `GRO-4377, GRO-4378, GRO-4379, GRO-4380, GRO-4381`. The "missing" identifiers exist — they belong to other work in the same workspace (Zapier infra, peer-review cleanup, etc.).

**Why:** Linear's identifier counter is a single workspace-wide sequence. It does not pause for "next available local slot" logic. If a peer agent or earlier session created issues in the gap, the next auto-assigned number lands after the highest existing identifier.

**Fix:**

1. Plan the build-out by **titles, descriptions, parent linkages, labels** — never by pre-assigned identifiers.
2. After each `issueCreate`, capture `issue.identifier` from the live response into a `{(title): (identifier, uuid)}` map.
3. The post-batch readback (gotcha #9) is the truth source — confirm the children list by parent UUID walk, not by identifier prefix.

**Verifier check:** the readback query uses the parent's UUID and walks `children(first: N) { nodes { identifier ... } }`. If the count matches the plan, the build-out succeeded regardless of which identifiers Linear assigned.

**Discovered 2026-07-31:** planning a 5-move cleanup pass expected `GRO-4373–4376` for the 4 intermediate tasks and a 5th beyond. All five landed at `GRO-4377–4381` because `4373–4376` were already consumed by Zapier infra tasks in the same workspace. The 5 Linear task creates succeeded; the only error was in the planning artifact that pre-named the wrong identifiers.

## 12. Bulk `issues(first: N)` queries can return HTTP 500 — paginate with smaller page size

**Symptom:** `{ issues(filter: { state: { type: { in: ["unstarted", "started"] } } }, first: 100) { ... } }` returns `HTTP 500: Internal Server Error` even though smaller queries work fine. Simpler queries like `{ viewer { id name } }` and `{ issues(filter: ..., first: 20) }` succeed.

**Why:** Linear's GraphQL endpoint has complexity / depth limits that aren't documented. Bulk queries with many nested fields (deep children walks, pageInfo pagination, multiple label traversals) can exceed the limit and 500 silently with no `errors` payload.

**Fix:** use cursor pagination with smaller page sizes (`first: 30` max), and walk the tree across multiple calls:

```python
all_issues = []
cursor = None
for page in range(5):  # 5 pages × 30 = 150 issues, enough for most triage scans
    if cursor:
        q = '... after: "%s"' % cursor
    else:
        q = '... first: 30)'
    d = gql(q)
    all_issues.extend(d['data']['issues']['nodes'])
    pi = d['data']['issues']['pageInfo']
    if not pi['hasNextPage']:
        break
    cursor = pi['endCursor']
```

**Verifier check:** before declaring "all X PE-* tasks fetched", confirm `pageInfo.hasNextPage == false` on the final iteration. If pagination wasn't exhausted, the count is wrong.

**Discovered 2026-07-31:** a 100-issue bulk scan returned 500 three times in a row; switching to `first: 30` with cursor pagination produced 150 issues across 5 pages cleanly.

## 13. Agent labels are entry-point conventions, NOT lane ownership — trust swarm_locks + branch_slug + review_signal

**Symptom:** A Linear issue is labeled `agent:fred` (or `agent:ned`, etc.), tempting a fast pickup. But reading the full description shows `swarm_locks: ['workspace-global']`, `branch_slug: ned/pe-workflow-XX-...`, and `review_signal: agent:peer-review-blocked required before Done`. Picking it up cold = protocol violation.

**Why:** the build-out script applies the per-task `agent:*` label from `TASK_META[ident]["owner"]`, but the project convention has historically used `agent:fred` as the universal "entry-point agent" for orchestration work — independent of who actually owns the lane. The Distributed-Execution Header (field 8) carries the **true** ownership signals: `branch_slug` (whose branch convention), `swarm_locks` (whose protocol to follow), `review_signal` (whose approval gate).

**Fix:** before claiming any task labeled `agent:<you>`:

1. Read the full description, including field 8 (Distributed-Execution Header).
2. If `branch_slug` does NOT match your lane's prefix (`feature/`, `ned/`, `content/`, `design/`, `fix/`), do not claim — the task is labeled for entry-point visibility but owned by another lane.
3. If `swarm_locks` declares paths outside your lane (`['workspace-global']`, `['okf/standards/...']`), you need to acquire the lock per your lane's protocol — if you don't know how, post a comment asking the named owner and pick a different task.
4. If `review_signal: agent:peer-review-blocked required before Done`, remember your work is not Done until peer approves — even if your tests pass.

**Verifier check:** the build-out script must (a) read the description of any task it's about to claim, (b) verify `branch_slug` matches the pickup agent's lane, (c) verify `pickup_signal` says `agent:in-progress NOT present`. The label alone is not the gate.

**Anti-pattern:** trusting the `agent:*` label and starting work without reading the Distributed-Execution Header. This was caught in 2026-07-31 when 3 PE-WORKFLOW-* tasks labeled `agent:fred` had `branch_slug: ned/pe-workflow-*` — the agent label was misleading, the swarm_locks were Ned's protocol, and picking them up cold would have triggered a cross-lane collision.

**Authoritative ownership signals, in priority order:** (1) `branch_slug` prefix, (2) `swarm_locks` paths, (3) `review_signal` required, (4) `agent:*` label — never label alone.

## 14. This workspace's Linear is a self-hosted / "portability" build — it drifts from cloud Linear's schema. Introspect before you mutate.

**Symptom:** queries that work against api.linear.app cloud 400 here with GraphQL-validation errors, even when they look correct.

**Observed on the growthwebdev workspace (2026-08-20, 237 labels, most `port00:*` portability noise):**

- **`Query.issue` only accepts `id` (UUID), NOT `identifier`.** `issue(identifier: "GRO-4799")` → 400. To look an issue up by its human identifier, use the list query: `issues(filter: { number: { eq: 4799 } }, first: 1) { nodes { id identifier ... } }`. (Do NOT add `team: { key: ... }` to that filter — the plain `number` filter is workspace-scoped already and works.)
- **`NumberComparator` expects `Float`, not `Int`.** `eq: $n` with `$n: Int!` → 400 `Variable "$n" of type "Int!" used in position expecting type "Float".` Declare `$n: Float!` and pass `float(n)`.
- **Sort enums are capitalized.** `PaginationSortOrder` values are `Ascending` / `Descending` (NOT `DESC`). Sort is the `sort` list arg taking `IssueSortInput` objects: `sort: { createdAt: { order: Descending } }`. (`orderBy` is a separate `PaginationOrderBy` enum — `createdAt`/`updatedAt` — but `sort` is the one that takes the object form.)
- **`workflowStates` team filter shape:** `workflowStates(filter: { team: { key: { eq: "GRO" } } })` worked; `workflowStates(filter: { teamId: ... })` → `Field "teamId" is not defined by type "WorkflowStateFilter". Did you mean "team"?`. `TeamFilter` accepts both `id` (IDComparator) and `key` (StringComparator).
- **`issueLabels(first: 100)` is not exhaustive.** There were 237 labels (mostly `port00:*` noise). Cursor-paginate with `pageInfo.hasNextPage`/`endCursor`, then filter to the real routing set (`agent:*`, `dispatch:*`, `type:*`). The PE label set (`agent:fred`, `dispatch:ready`, `type:task`, `agent:peer-review-blocked`, etc.) all existed — resolve UUIDs from the full paginated set, don't assume the first page.

**Verifier check:** before the first mutation, introspect `__type(name:"Query")` args for `issue`/`issues`, `__type(name:"PaginationSortOrder")`, and `__type(name:"NumberComparator")`-family comparators. If the deployment disagrees with this skill's cloud-Linear assumptions, trust the introspection, not this file.

## 15. Rate-limit retry can double-fire `issueCreate` and create a stray duplicate issue.

**Symptom:** after a batched `issueCreate` run, the post-batch readback shows one epic with **one more child than planned**. The extra child has an identical title to an earlier task and an identifier *past* the last one you created (e.g. you created up to GRO-4815, but a stray GRO-4816 exists with the same title as GRO-4809).

**Why:** the rate-limit retry loop (gotcha #4) sleeps 30s and re-fires the *same* mutation. If the original request actually committed on the server but the response timed out or was lost, the retry creates a second issue. The retry is the cure for the timeout and the cause of the dup — they're the same code path.

**Fix:**
1. The post-batch readback (gotcha #9) is what *catches* this — walk the full parent→epic→task tree and count children per epic against the plan. Any extra child with a duplicated title is a retry double-fire.
2. **Do not delete** the stray. Neutralize it: move it to `Canceled` (terminal, cannot be picked up) + post a comment naming the canonical issue ("DUPLICATE of GRO-4809; stray echo from issueCreate rate-limit re-fire; all real work lives on GRO-4809").
3. Note: the `Duplicate` workflow state is **guarded** on this build — `issueUpdate` to `Duplicate` → 400 `Issues can only be moved to a duplicate state when a duplicate issue relation exists.` (it needs a formal relation object). So `Canceled` + comment is the reliable neutralization, not `Duplicate`.

**Verifier check:** after ANY bulk `issueCreate`, assert per-epic child count == planned count. If a child title is duplicated within one epic, it is a retry double-fire → Cancel + comment, then re-run the readback. Treat this as a known failure mode of bulk create, not a readback bug.

## 16. A hosted review link can 400 while the packet is fine — verify the SURFACE before promising the link, and supersede SHAs when the packet changes.

**Symptom (2026-08-20, HFG guest-fleet review packet):** a reviewer-ready `REVIEW_PACKET.md` placed under the Prismatic workspace-tree surface (`/api/workspace-tree/preview?workspace_id=…&path=…` behind `prismatic.growthwebdev.com`) started returning `400 invalid workspace identifier` for *valid* workspace IDs — on BOTH the public domain and the local origin — even though the same request had returned 200 with the exact file bytes minutes earlier. The packet was perfect; the surface was not. A second habit bites the same handoff: the packet gains a §7 sender-verification log AFTER the tarball + SHA were posted, silently invalidating the posted SHA.

**Why (two distinct causes):**
1. **Surface regression ≠ packet problem.** The deployed gateway runs from its own runtime checkout (for Prismatic: `/home/ubuntu/work/prismatic-engine`, NOT the `prismatic-*-<feature>` worktrees that look current — check `ls -l /proc/<pid>/cwd` of the gateway process). Its workspace-tree preview uses a *strict registry* (`PRISMATIC_WORKSPACE_REGISTRY_FILE`, default `~/.prismatic/config/workspace-registry.json`, validated in `prismatic/gateway/workspace_tree.py`: uid/mode/size/JSON-schema checks, request-scoped pinned fd). The list endpoint (`/api/workspaces`) and the preview endpoint's `resolve()` can disagree: the list reports the registry objects while resolve intermittently fails with `invalid workspace identifier` / `workspace object unavailable`. A flaky registry does NOT mean your file/path is wrong.
2. **SHA drift.** Every byte change to the packet (including adding a verification log) changes the tarball SHA. A reviewer who verifies the *first* posted SHA fails verification on the *current* tarball.

**Fix — surface:**
1. Before promising a link, probe the exact API shape the deployed frontend uses (read the `fetch` calls in the served dashboard bundle) and confirm 200 + byte-identical content (`sha256` of returned `content` == file on disk) on the PUBLIC domain, not just localhost.
2. If the preview API 400s on a valid ID: check the list endpoint — if it still lists the ID, the registry `resolve()` is flaky/broken (a pre-existing gateway bug). **Do not burn the handoff session fixing a production registry bug** (flag it, offer to fix separately — it's the orchestrator's infra lane and Michael's call).
3. **Fallback that always works:** the org-standard handoff shape — tarball + SHA256 + contents list in a Linear comment on the parent epic. The reviewer starts with `sha256sum`, then the §3 checklist. A broken web link must never be the only delivery path.
4. Never hand off a link you haven't fetched yourself end-to-end (public domain, exact bytes). "The route exists" is not proof the reviewer will see the file.

**Fix — SHA supersede:**
1. Keep the packet self-consistent: the §7 verification count (N/N) must equal the actual check count; when the verifier gains a check, update §7 in the same pass.
2. Rebuild the tarball, re-run the verifier against the NEW sha, then post a **superseding Linear comment** ("⚠️ PACKET UPDATE — supersedes the SHA in the comment above") and, once stable, a **📌 FINAL BUNDLE STATE** comment naming the one SHA to use. Mark earlier SHAs explicitly stale ("ignore the earlier … value"). Three comments (initial, update, final) are cheaper than a reviewer verifying the wrong bundle.

**Verifier check:** (a) link promised ⇒ public-domain fetch returned 200 + matching sha256 of content, logged; (b) tarball sha256 == the SHA in the LATEST Linear comment; (c) extract == disk (`diff -r` byte-identical); (d) §7 count string in the packet == check count in the verifier script.

**Worked example:** HFG guest-fleet packet, GRO-4797 — three SHA comments posted (6c751b7f… → b92950d5… → final 6a17af85…cf9a32), each supersede explicitly named; workspace-tree preview 400'd the whole session (registry flake), tarball+SHA delivery used instead; 17/17 ad-hoc verifier passed.