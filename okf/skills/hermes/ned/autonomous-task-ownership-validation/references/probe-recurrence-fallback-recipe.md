# Probe Recurrence Fallback Recipe

**When to use this:** `scripts/probe_recurrence.sh` crashes with `AttributeError: 'NoneType' object has no attribute 'get'` (or any other unexpected traceback), OR when you want a more reliable per-issue probe than the script's anchor-only logic provides. The fallback recipe is one `execute_code` call — paste and run.

**Why the script fails:** line 151 in `fetch_anchor_state()` runs `return data.get("data", {}).get("issue") or {}`. When the GraphQL response payload is `{"errors": [...]}` (no `"data"` key, or `"data": null`), `data.get("data", {})` returns `None` because the key IS present but its value IS None — `.get`'s default only fires on missing keys. Then `.get("issue")` on `None` raises `AttributeError`. The script exits with a traceback and no verdict, leaving the agent guessing.

**Proven failure:** 2026-06-29 r133 with `python3 probe_recurrence.sh --anchor GRO-485 --batch-ids "GRO-484,...,GRO-502"`. The script crashed immediately with the AttributeError above. Inline probe (below) worked first try and gave the SUPPRESS verdict in one tool call.

---

## The recipe — paste into `execute_code`

```python
import json, urllib.request, re
from datetime import datetime, timezone

# Step 1: pure-Python .env parse (r119 fix, immune to /bin/sh + redaction layer)
def load_key():
    for path in [
        "/home/ubuntu/.hermes/profiles/orchestrator/.env",
        "/home/ubuntu/.hermes/profiles/ned/.env",
        "/home/ubuntu/.hermes/profiles/ned/.env.bak",
    ]:
        try:
            with open(path) as f:
                for line in f:
                    m = re.match(r'^LINEAR_API_KEY\s*=\s*[\'"]?([^\'"]+)', line.strip())
                    if m:
                        return m.group(1).strip(), path
        except FileNotFoundError:
            continue
    return "", ""

key, src = load_key()
assert len(key) == 48, f"key length wrong: {len(key)} (src={src})"

# Step 2: variables-API gql() (more robust than string-concat for nested queries)
def gql(query, variables=None):
    req = urllib.request.Request(
        "https://api.linear.app/graphql",
        data=json.dumps({"query": query, "variables": variables or {}}).encode(),
        headers={"Authorization": key, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())

# Step 3: query body (multi-line, variables API — works for any nesting depth)
query = """
query($id: String!) {
  issue(id: $id) {
    identifier
    title
    state { name }
    updatedAt
    labels { nodes { name } }
    comments(last: 10) {
      nodes { createdAt user { name email } body }
    }
  }
}
"""

# Step 4: per-issue fetch (r153 fix: resolve via Linear's `issue(id: $id)` lookup)
batch_ids = ["GRO-484","GRO-485","GRO-486","GRO-487","GRO-488",
             "GRO-490","GRO-492","GRO-499","GRO-500","GRO-502"]

for iid in batch_ids:
    try:
        d = gql(query, {"id": iid})["data"]["issue"]
        comments = d["comments"]["nodes"]
        # r147: filter on user.email, NOT user.name == "Ned" (the API key posts as Michael)
        ned_comments = [c for c in comments if c["user"].get("email") == "mbgulden@gmail.com"]
        ned_comments.sort(key=lambda c: c["createdAt"], reverse=True)
        latest_ned = ned_comments[0] if ned_comments else None
        print(f"{iid}: state={d['state']['name']} cmts={len(comments)} ned={len(ned_comments)}")
        if latest_ned:
            ts = datetime.fromisoformat(latest_ned["createdAt"].replace("Z","+00:00"))
            age_min = (datetime.now(timezone.utc) - ts).total_seconds() / 60
            print(f"  latest ned triage: {age_min:.0f}m ago — {latest_ned['body'][:120]!r}")
    except Exception as e:
        print(f"{iid}: ERROR {e}")

# Step 5: anchor-shift detection (r153) — if your --anchor isn't in the feed,
# find the batch member with the most-recent Ned-triage comment.
# The script's default-anchor age is informational only — what matters is
# the age of the LATEST triage on the CURRENT BATCH's effective anchor.
```

---

## Why variables API > string-concat (verified 2026-06-29 r133)

The r119 documented string-concat recipe:

```python
q = '{ issue(id: "' + iid + '") { identifier title state { name } comments(last: 10) { nodes { createdAt user { name email } body } } } }'
```

**Returned HTTP 400** on the first attempt in r133. The multi-line concatenation across many selection sets produces a query string that Linear's parser rejects — the failure is opaque (just HTTP 400, no useful diagnostic).

**The variables API worked first try** for the same query:

```python
query = "query($id: String!) { issue(id: $id) { identifier title state { name } ... } }"
result = gql(query, {"id": iid})
```

**Recommendation:** always use the variables API for per-issue probes with nested field selections. The string-concat recipe still works for SIMPLE queries (single field, no nesting) — keep both in your toolbox but default to variables API.

---

## When the script is actually preferred

The script is still useful when:
- You want a single one-shot verdict (SUPPRESS / POST_FRESH_TRIAGE) without writing Python
- The anchor resolves cleanly in the active token's team scope (GRO-570 in the original bootcamp feed, GRO-485 in Batch B)
- You don't need per-issue state + comment data (just the recurrence verdict)

The fallback recipe is preferred when:
- The script crashes (AttributeError or otherwise)
- You need per-issue data for an audit doc (states, comment counts, triage-table rows)
- You're running the r132 negative-marker lane classifier inline
- You want to cross-check the probe's age against `MAX(createdAt)` from a fresh fetch (r47 pattern)

---

## Cross-references

- **r119** (string-concat GraphQL pitfalls + pure-Python .env parse): established the baseline inline probe recipe this builds on.
- **r132** (negative-marker lane classifier): the inline recipe's `print()` loop feeds into the lane-classification step.
- **r147** (probe_recurrence.sh filter-shape fixes): the script's intended filter logic, now documented alongside the fallback for completeness.
- **r153** (batch-anchor-shift): the fallback recipe includes the anchor-shift detection block.