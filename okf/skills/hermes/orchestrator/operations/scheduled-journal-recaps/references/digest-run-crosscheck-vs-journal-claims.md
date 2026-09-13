# Digest run vs recap write — cross-check journal claims against ground truth

This session was a **Becca / journal digest** (a reader of the journal), not a recap-write. The distinction matters for what a digest owes the operator.

## What happened (2026-09-13)

The 09-13 Hermes daily journal declared the four mangled 5-min cron jobs
`s`/`c`/`t`/`o` "**CONFIRMED STILL LIVE. all enabled: True**." A live `jobs.json`
read this run showed only **three** exist — `s`, `c`, `t` — with `o`
(id `c91822e6f27a`) **absent entirely** and `p` (id `7e91a881f69f`) paused. The
fleet had already shrunk 4→3; the journal's "confirmed still live" claim was two
days stale by the time this digest read it.

## The rule

A digest **reads** the journal; a recap **writes** it. When a digest surfaces a
journal's "fixed" or "still live" assertion, verify the load-bearing ones against
the live source before relaying:

- cron claim → read `~/.hermes/profiles/orchestrator/cron/jobs.json`
- `in_flight` Linear issue → query the Linear API live (see `linear-api-direct-queries`)
- wire signal → read the DB / inbox directly

Correct the count in the digest and report the correction explicitly
(e.g. "recap listed four mangled jobs; live check found three — `o` is gone").
Do not propagate a "still live" claim that ground truth has already retired.

This is the read-side mirror of the skill's existing "query Linear live, don't
surface stale commitments as current blockers" rule — applied to the journal's
*own* operational claims, which a digest would otherwise inherit verbatim.

## Ground-truth recipe (jobs.json)

```python
import json
d = json.load(open("/home/ubuntu/.hermes/profiles/orchestrator/cron/jobs.json"))
for j in d["jobs"]:
    if (j.get("name") or "") in ("s","c","t","o","p"):
        print(j["name"], j["id"], "enabled=", j.get("enabled"),
              "state=", j.get("state"), "completed=", j.get("repeat",{}).get("completed"))
```

Count the enabled short-name jobs; that is the true "mangled fleet" number for
the digest. Expect drift between what the last journal *claimed* and what is
*now* enabled — jobs get disabled/removed between journal runs.
