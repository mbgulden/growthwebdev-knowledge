# Mixed-Batch Triage Recipe

When the scanner feeds a batch where **some** issues are in-lane and **others** are misrouted, do NOT use the first-issue-as-anchor shortcut from the recurring-batch playbook. Triage per issue first.

## Workflow

```python
import json, urllib.request, os
import subprocess

token = os.environ["LINEAR_API_KEY"]

def gql(query, variables=None):
    req = urllib.request.Request(
        "https://api.linear.app/graphql",
        data=json.dumps({"query": query, "variables": variables or {}}).encode(),
        headers={"Authorization": token, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())

ids = ["GRO-2876", "GRO-537", "GRO-512", ...]

# Pull full state + last 3 comments for every issue in one query
q = """
query($ids:[ID!]!){
  issues(filter:{id:{in:$ids}}){
    nodes {
      id identifier title state { name } labels { nodes { name } }
      comments(last: 3) { nodes { body createdAt user { name } } }
    }
  }
}
"""
res = gql(q, {"ids": ids})

# Partition
in_lane, misroute = [], []
for n in res["data"]["issues"]["nodes"]:
    labels = [l['name'] for l in n['labels']['nodes']]
    has_dispatch_ready = "dispatch:ready" in labels
    comment_bodies = " ".join(c['body'].lower() for c in n['comments']['nodes'])
    has_dequeue_note = any(
        kw in comment_bodies
        for kw in ("out of lane", "dequeued", "wrong agent", "not ned", "relabel", "lane violation")
    )
    if has_dispatch_ready or (not has_dequeue_note and "<in-lane-keyword-in-title>" in n['title'].lower()):
        in_lane.append(n['identifier'])
    else:
        misroute.append(n['identifier'])

print(f"in_lane: {in_lane}")
print(f"misroute: {misroute}")
```

## Decision rules (in order)

1. `dispatch:ready` label present → **in-lane** (positive signal overrides everything)
2. Comment thread empty AND title/file targets in Ned's lane → **in-lane**
3. Prior triage comment names a different lane (`agent:fred`, `agent:kai-content`, `agent:agy`, `agent:designer`) → **misroute**
4. Prior triage comment contains "out of lane", "dequeued", "wrong agent", "not Ned's lane" → **misroute**
5. Title contains marketing/build keywords (landing page, pricing, bootcamp, curriculum, copy, content, etc.) → **misroute**

## Action per partition

**Misroute subset:**
- Post ONE consolidated comment on the first misroute ID (not first scanner ID) naming the rest.
- Do NOT run `finalize_task.sh` on misroute issues (5a exception).
- Do NOT change state; do NOT relabel (GRO-559 owns the dispatcher fix).

**In-lane subset:**
- For each: create/find `ned/GRO-XXXX` branch, do work, commit early, open PR.
- Run `finalize_task.sh` per issue (this transitions state to In Review — desired for in-lane work).
- If `finalize_task.sh` swept unrelated untracked files (e.g., a `pip install` into `.venv_dev/`), revert that commit and push the revert immediately. Pattern:
  ```bash
  cd /home/ubuntu/work/prismatic-engine
  git revert --no-edit HEAD
  git push origin ned/GRO-XXXX
  ```

## Common pitfalls

- **Do not anchor on the first scanner issue.** It's frequently not the same as the first misroute. Always run the partition query above.
- **Do not assume a recurring batch is uniformly misrouted.** The Ned-dispatcher-broken bug (GRO-559) re-feeds 9 misroutes every cron pass, but new in-lane issues can land on top of the list. Verify each.
- **`gh pr create` prints "Warning: N uncommitted changes" alongside a successful URL.** Check `git status` to see what; ignore if it's `.venv_dev/` or test-fixture noise, fix only if it's real work.

## Pre-pass state audit (mandatory on recurring batches)

Even on a pure-recurring dequeue pass (no in-lane work, 5a exception applies), scan the entire scanner-fed set with the partition query above BEFORE posting the anchor comment. The state field is the catch — a prior cron pass that ran full finalize and didn't reverse will leave one or more issues stuck in `In Review`, which Michael never wanted. The current pass must:

1. Read state for every issue in the scanner list (one GraphQL `issues(filter: {id: {in: [...]}})` call — the same call you use for partitioning).
2. If any issue is in `In Review` or `Done` and the issue is being dequeued this pass, reverse it to `Todo` (or to the state Michael's prior triage notes indicate).
3. Post a brief state-reversal note on the affected issue (NOT the anchor — anchor is for the consolidated dequeue, the reversal note goes on the drifted issue itself so the thread tells the full story).
4. Only then post the consolidated dequeue anchor comment.

This drift is cumulative across passes. The 2026-06-28 ~05Z pass surfaced GRO-509 in `In Review` — the residue of a 2026-06-28 ~01Z finalize that didn't reverse. The post-finalize state-check (SKILL.md step 5a.1) catches drift the current pass *causes*; this pre-pass audit catches drift from *prior* passes that didn't run the reversal step.

**Why this matters:** Michael sets these issues to Todo/Backlog deliberately after dequeueing them. Leaving them in `In Review` blocks downstream agents (the Linear UI filters out In Review for "ready to pick up") and forces Michael to fix it manually. The audit is cheap — already part of the partition query — and prevents one extra manual fix per recurrence.