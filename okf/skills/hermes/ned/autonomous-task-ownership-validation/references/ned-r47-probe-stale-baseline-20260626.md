# r47 — Probe Stale-Baseline Corrected SUPPRESS (2026-06-26 23:30Z)

**Job:** Prismatic Engine Ned autonomous task loop (cron `20759afd096b` — Window B stripped-prompt variant)
**Anchor:** GRO-570
**Audit:** `okf/audits/ned-scan-triage-2026-06-26-r47.md`
**Commit:** `813204d` on `ned/scan-triage-2026-06-26-r43`, pushed to origin

## What happened

The recurrence probe (`probe_recurrence.sh`) returned `POST_FRESH_TRIAGE` based on anchor age = 376 min (vs the 17:15Z baseline). The 17:15Z baseline IS 376 min old — the probe was factually correct from its own reference point. But three fresh triages had been posted since: r38 (20:58Z), r44 (22:59Z), r46 (23:24Z). The actual latest triage was r46 at 23:22:35Z — only ~7 min ago at the time of r47.

## Reproduction recipe

```bash
# 1. Run probe (returns POST_FRESH_TRIAGE on stale baseline)
python3 ~/.hermes/profiles/ned/skills/autonomous-task-ownership-validation/scripts/probe_recurrence.sh

# 2. Probe output:
#    Anchor: GRO-570
#    Last triage age: 376.0 min (2026-06-26T17:15:07.658Z)
#    Drift detected: +['GRO-509', ...] -['GRO-546', ...]
#    Items identical to prior triage: NO
#    Decision: POST_FRESH_TRIAGE
#    Reason: age 376min in 2h-24h window; per decision table, items-identical doesn't matter — post fresh triage

# 3. Sanity check (override the probe):
# Fetch the anchor's comments, sort by createdAt DESC, find MAX(createdAt)
python3 -c '
import json, urllib.request, os
KEY = os.environ["LINEAR_API_KEY"]
q = """{ issue(id: \"GRO-570\") { comments(last: 15) { nodes { id createdAt user { email } body } } } }"""
r = urllib.request.urlopen(urllib.request.Request(
    "https://api.linear.app/graphql",
    data=json.dumps({"query": q}).encode(),
    headers={"Authorization": KEY, "Content-Type": "application/json"},
    method="POST"))
data = json.loads(r.read())
nodes = sorted(data["data"]["issue"]["comments"]["nodes"], key=lambda c: c["createdAt"], reverse=True)
newest = next(n for n in nodes if n.get("user", {}).get("email") == "mbgulden@gmail.com")
print(f"Latest Ned triage: {newest[\"createdAt\"]}  body preview: {(newest[\"body\"] or \"\")[:100]}")
# Expected: ~7 min ago, NOT 376 min
'

# 4. Override the probe with the correct verdict per decision table:
#    - Last triage age: 7 min (<2h threshold)
#    - Items identical to last triage: YES
#    - → SUPPRESS, no Linear comment, brief cron reply only
```

## Why the probe missed this

The probe's reference baseline is a fixed point in time (the 17:15Z triage was the most recent one that the probe had in its parsed-once-and-cached state). The probe correctly measured 376 min since that baseline. It does NOT re-parse the anchor's comment thread on every invocation to find the truly-latest triage — it relies on a regex to extract the last triage's timestamp from the previous probe's body, which becomes stale when multiple fresh triages have landed since.

**Fix direction (not yet implemented in the probe):** the probe should fetch `comments(last: 15)` and compute `MAX(createdAt)` across ALL Ned-authored comments, not just the last one it found via the body-extraction regex. This would prevent the stale-baseline false-positive across long bursts with many drift-triage posts.

**Workaround (applied at r47):** when the probe returns `POST_FRESH_TRIAGE` on a SUPPRESS-shaped tick (script feed items feel identical to last tick, recent prior cron), do the manual sanity check and override the probe's verdict.

## Decision rules (r47-derived)

| Probe says | Manual check finds | Correct verdict |
|---|---|---|
| POST_FRESH_TRIAGE, age 376min (vs old baseline) | MAX(createdAt) is 7 min ago, items identical | **SUPPRESS** (override probe) |
| POST_FRESH_TRIAGE, age 200min, drift +2 items | MAX(createdAt) is 200 min ago, items match drift | POST_FRESH_TRIAGE (trust probe) |
| SUPPRESS, age 18min | MAX(createdAt) is 18 min ago | SUPPRESS (trust probe) |
| SUPPRESS, age 18min | MAX(createdAt) is 8h ago (probe missed a fresh triage) | **POST_FRESH_TRIAGE** (override probe) |

## Lessons

1. **The probe's `Last triage age:` reading is correct from its own reference point, but the reference point can be stale.** Always sanity-check `MAX(createdAt)` from a fresh fetch before posting.
2. **The 7-min vs 376-min difference is the canonical signal that the probe is comparing against the wrong triage.** Any time the probe's age reading is in the 2h-24h window AND a cron has run more recently than the probe's referenced baseline, this case is in play.
3. **This is the 2nd canonical confirmation that the Window B stripped-prompt variant cron (`20759afd096b`) fires the validation skill correctly.** First was r38 (20:58Z), second is r47 (23:30Z). The skill is robust to prompt stripping across multiple variants.
4. **Cumulative stats at r47:** 47 cron runs, 4 Linear comments on the 10-item batch = **91.5% noise-free ratio**. The probe + manual-verification combo sustains that ratio even when the probe itself gives a misleading reading.