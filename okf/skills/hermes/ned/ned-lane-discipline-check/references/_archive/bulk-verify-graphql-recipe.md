---
name: ned-lane-discipline-check-bulk-verify-recipe
description: Canonical bash + inline Python recipe for verifying a batch of Linear issues via GraphQL in one shot. Verified 2026-06-29 on the GRO-503..512+537 recurring misroute batch.
---

# Bulk-verify GraphQL recipe — for scanner batch triage

When the cron pre-run script emits `Found N Linear issue(s)` and you need to
verify every ID in one pass (lane check, dequeue-status check, state drift),
use this recipe. It runs N HTTP calls and prints a tidy per-issue summary
to stdout, all in one terminal invocation.

## The recipe (verbatim, working as of 2026-06-29)

```bash
for id in GRO-503 GRO-504 GRO-505 GRO-507 GRO-508 GRO-509 GRO-510 GRO-511 GRO-512 GRO-537; do
  echo "=== $id ==="
  curl -s "https://api.linear.app/graphql" \
    -H "Authorization: $LINEAR_API_KEY" -H "Content-Type: application/json" \
    -d "{\"query\":\"{ issue(id: \\\"$id\\\") { title description labels { nodes { name } } } }\"}" \
    | python3 -c "
import sys, json
d = json.loads(sys.stdin.read())['data']['issue']
print(f\"TITLE: {d['title']}\")
print(f\"LABELS: {[l['name'] for l in d['labels']['nodes']]}\")
desc = (d.get('description') or '')[:200].replace(chr(10), ' ')
print(f\"DESC:  {desc}\")
"
done
```

## Why this shape (lessons baked in)

1. **`issue(id: "GRO-XXX")` accepts the human-readable identifier.** This is
   the only safe single-issue filter — `identifier:{eq:...}` returns
   GRAPHQL_VALIDATION_FAILED. Confirmed in `linear-lane-filter-query.md`.

2. **GraphQL payload is escaped with `\"` and `\\\\\"` for the inner `\"$id\\\"`.**
   Bash + JSON double-quoting stacks three levels deep. Easy to break; the
   exact escape pattern shown here is what works.

3. **Inline `python3 -c` rather than `jq`.** `jq` is not always installed in
   the cron sandbox (it wasn't on 2026-06-29 ~0545Z). Python 3 is. The
   `python3 -c` block runs in the parent shell's env, so `$LINEAR_API_KEY`
   inherited from the parent shell is in scope.

4. **`d.get('description') or ''`** — see footgun below.

5. **`chr(10)` not `\\n`** — inside the bash single-quoted Python `-c`
   block, `chr(10)` is the safe form for newline in print().

6. **`echo "=== $id ==="` before each query** — lets you match output back
   to ID even if curl prints interleaved warnings.

## Footgun: `NoneType` when `description` is null

**Symptom:**
```
TypeError: 'NoneType' object is not subscriptable
Traceback (most recent call last):
  File "<string>", line 6, in <module>
```

**Cause:** Linear issues without a description field return `"description": null`,
not an empty string. `d['description'][:200]` then crashes. On the 2026-06-29
batch (GRO-503..512), 9 of 10 issues had `null` descriptions — only GRO-537
(home page) had a real description.

**Fix:** always use `d.get('description') or ''` in the recipe.

This is also why **title + labels** are the reliable triage signals — don't
build the loop around `description` content.

## Reading the output

For the 2026-06-29 GRO-503..512+537 batch, every row printed:

```
=== GRO-503 ===
TITLE: PHASE 1: Execute Week 2 — Pricing and Financial Modeling
LABELS: ['agent:ned']
DESC:
```

That single line `LABELS: ['agent:ned']` + a non-infra `TITLE:` is the
diagnostic that confirms "all 10 are still misrouted." Combine with a
comment-thread scan of the anchor (GRO-537) for dequeue-pattern keywords
(see `linear-lane-filter-query.md`) to upgrade to SUPPRESS verdict.

## When NOT to use this recipe

- **Single-issue deep dive** (you want full comment thread, audit history):
  use the longer `comments(last: 5)` query in `linear-lane-filter-query.md`.
- **Production access audit** (no bash heredocs, want JSON output to feed
  downstream tooling): use `python3 -c "import json, urllib.request; ..."`
  with `json.dumps` to file.
- **Batch >20 issues**: rate-limit risk. Use the `issues(filter:{...})` query
  in `linear-lane-filter-query.md` instead — single round-trip, single
  pagination, no N HTTP calls.

## See also

- `linear-lane-filter-query.md` — single-issue GraphQL shapes + dequeue
  comment grep markers
- `recurring-batch-suppress-2026-06-29.md` — what to do once you confirm
  all N are misrouted
- `pass-log-2026-06.md` — append-only audit log of which passes used
  this recipe and what verdict came out