---
title: Linear API gotchas
description: Pagination ordering, comment-create JSON shape, and other Linear GraphQL quirks confirmed during Ned cron triage passes. Companion to Mode G/H in the parent skill (Linear API pitfalls when calling finalize_task.sh from cron).
type: reference
---

# Linear API gotchas

Small Linear GraphQL behaviors that have cost Ned cron passes extra tool calls. Consolidated here so future Ned sessions don't re-discover them. For the broader comment-creation landmines (curl+heredoc JSON escape, `$input` silently dropped), see Mode G and Mode H in the parent skill's SKILL.md.

## `comments(last:N)` returns the OLDEST N comments, not the newest

**Symptom:** A Ned cron pass needs to verify its freshly-posted triage comment actually landed on the issue. It runs:

```bash
curl -s "https://api.linear.app/graphql" \
  -H "Authorization: $LINEAR_API_KEY" -H "Content-Type: application/json" \
  -d '{"query":"{ issue(id: \"GRO-537\") { comments(last: 3) { nodes { createdAt body } } } }"}'
```

…and gets back Michael's triage notes from 2026-06-27 12:39Z, 17:25Z, 23:10Z. The fresh Ned pass-17 comment (posted moments ago) is NOT in the response. Panic: was the post dropped?

**Reality:** `comments(last: 3)` returns the **oldest 3** comments on the issue, not the newest. The Linear GraphQL `last:` argument is reverse-paginated relative to the default chronological (oldest-first) ordering. To get the newest comments, either:

```bash
# Option A — fetch all comments and sort client-side (works for ≤50 comments)
curl -s "https://api.linear.app/graphql" \
  -H "Authorization: $LINEAR_API_KEY" -H "Content-Type: application/json" \
  -d '{"query":"{ issue(id: \"GRO-XXX\") { comments { nodes { createdAt body } } } }"}' \
  | python3 -c "
import json, sys
cs = json.load(sys.stdin)['data']['issue']['comments']['nodes']
cs.sort(key=lambda c: c['createdAt'], reverse=True)
print(f'total: {len(cs)}')
for c in cs[:3]:
    print('==', c['createdAt'], '==')
    print(c['body'][:200])
"
```

```bash
# Option B — use first/last with endCursor pagination (more efficient for >50 comments)
# See Linear GraphQL docs on connection pagination.
```

**Confirmed pass-17 (2026-06-29 ~07:12Z):** My pass posted a comment to GRO-537 with `commentCreate` → `{"data":{"commentCreate":{"success":true}}}`. First verification call with `last:3` returned the three oldest comments from 2026-06-27. I assumed the post failed and started drafting diagnostic queries. The post had actually succeeded — when I refetched with `comments { ... }` (no `last:`) and sorted client-side, the fresh comment appeared at top with `createdAt: "2026-06-29T07:12:25.358Z"`.

**Detection recipe:** when verifying a fresh comment post:

```bash
# 1. Note the expected createdAt timestamp (record it before posting):
echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] expected comment timestamp" >> /tmp/linear-comment-post.log

# 2. After the commentCreate mutation, refetch with no `last:` filter:
curl -s "https://api.linear.app/graphql" \
  -H "Authorization: $LINEAR_API_KEY" -H "Content-Type: application/json" \
  -d '{"query":"{ issue(id: \"GRO-XXX\") { comments { nodes { createdAt } } } }"}' \
  | python3 -c "
import json, sys
cs = json.load(sys.stdin)['data']['issue']['comments']['nodes']
cs.sort(key=lambda c: c['createdAt'], reverse=True)
print('top 3 by createdAt:')
for c in cs[:3]: print(' ', c['createdAt'])
"
# 3. Confirm your fresh comment's createdAt matches the timestamp you recorded in step 1.
```

**Cost:** one extra fetch (~1 sec) per cron pass. Benefit: no false negative on `commentCreate` success.

**Why this matters for the BLOCKED_COMMENT guard:** the guard's `comments(last: 5)` query uses the same pattern. The guard is designed to scan the **most recent** 5 comments because Michael's dequeue notes are usually the latest. But because of the reverse-pagination quirk, `comments(last: 5)` actually returns the **oldest** 5 — which means dequeue notes from prior cron cycles that are now buried deep in the thread may NOT trip the guard.

**Practical implication for triage comments:** because the guard uses `last:5` and may miss older dequeue markers, Ned triage-comment templates must use canonical keywords ("out-of-lane", "dequeued", "relabel") so the **most recent** comments always reinforce the guard. See `references/dry-run-as-guard-verification.md` §"Ned triage comment as a self-tripwire" for the canonical-keyword discipline.

## `commentCreate` returns `success: true` but the comment may not appear immediately in `comments` queries

**Symptom:** after `commentCreate` → `{"data":{"commentCreate":{"success":true}}}`, an immediate `comments` query doesn't show the new comment.

**Reality:** Linear's GraphQL read replicas lag the write path by ~1–3 seconds. The `success: true` response is canonical; the comment will appear in subsequent reads. Don't re-post — that creates duplicate comments.

**Detection recipe:** wait 3 seconds before verifying, or accept that the immediate verification may show the OLD comment set.

```bash
# After commentCreate mutation:
sleep 3
# Then refetch comments
```

## `issueUpdate(id: $id, input: {stateId: $stateId})` — `id` is TOP-LEVEL (Mode C-refinement footnote)

Already documented in Mode C-refinement of the parent skill, but worth re-stating because it cost 2 failed attempts on GRO-537:

- **Correct:** `issueUpdate(id: $issueId, input: {stateId: $stateId})`
- **Wrong:** `issueUpdate(input: {id: $issueId, stateId: $stateId})` → `GRAPHQL_VALIDATION_FAILED: "Field \"id\" is not defined by type \"IssueUpdateInput\""`
- **Wrong:** `issueUpdate(id: $issueId, input: {state: "In Review"})` → `state` is not a valid field; use `stateId` (workflow state UUID).

## Workflow state UUIDs are stable per team

Once you query `workflowStates { nodes { id name } }` and capture the UUID for `Todo` / `In Review` / `Backlog` / `Canceled`, those UUIDs persist across issues in the same team (GRO team). Cache them:

```bash
# Query once, cache to /tmp/linear-states.json
curl -s "https://api.linear.app/graphql" \
  -H "Authorization: $LINEAR_API_KEY" -H "Content-Type: application/json" \
  -d '{"query":"{ workflowStates { nodes { id name type } } }"}' \
  > /tmp/linear-states.json

# Reuse in subsequent calls — no need to re-query per issue.
TODO_ID=$(python3 -c "import json; print([n['id'] for n in json.load(open('/tmp/linear-states.json'))['data']['workflowStates']['nodes'] if n['name']=='Todo'][0])")
```

**Caveat:** UUIDs may rotate if the team workflow is restructured. Refresh `/tmp/linear-states.json` weekly or on `GRAPHQL_VALIDATION_FAILED` for `stateId`.

## Cross-reference

- **Parent skill:** `finalize-task-script-bug` SKILL.md (Modes C, F, G, H all touch Linear API)
- **Companion recipe:** `references/dry-run-as-guard-verification.md` (the BLOCKED_COMMENT guard uses `comments(last: 5)` — see §"Ned triage comment as a self-tripwire" for the canonical-keyword discipline that compensates for the reverse-pagination quirk)