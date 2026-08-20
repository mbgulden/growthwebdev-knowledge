# Drift detection — when scanner batch changes between ticks

> Canonical reference: Ned r44 (2026-06-26 22:59Z) was the canonical drift-after-prior-triage variant. The scanner feed had lost 6 items (anchor GRO-570 itself + 5 items completed by other agents) since r43 4 minutes earlier. Decision rule applied: `POST_FRESH_TRIAGE` (drift + 2h-24h window), drift-delta comment posted on anchor only, no per-issue re-commentary.

## Why drift detection matters more than identity match

The recurrence probe (`probe_recurrence.sh`) returns one of:
- `SUPPRESS` (anchor age + identity match → no Linear comment)
- `POST_FRESH_TRIAGE` (anchor age in 2h-24h window OR drift OR no prior triage)
- `IDENTITY_UNKNOWN` (could not parse prior triage item list)

When the probe returns `POST_FRESH_TRIAGE` with reason "drift," the agent must:

1. **Fetch the prior triage comment body** via GraphQL `issue(id: GRO-XXX) { comments(last: 10) }`.
2. **Parse the item list** it documented (use `re.findall(r"GRO-\d+", body)`).
3. **Compare against current scanner feed** via set diff: `set(current) - set(prior)` = added, `set(prior) - set(current)` = removed.
4. **Post the drift delta** to the anchor — focus the comment on what changed, NOT per-item re-validation.

## Decision table for drift vs identity match

| Prior triage age | Item identity vs current | Action |
|---|---|---|
| <2h ago | identical (set diff empty) | SUPPRESS — comment spam prevention |
| <2h ago | drift (set diff non-empty) | **POST_FRESH_TRIAGE** — drift is material |
| 2h-24h ago | identical | **POST_FRESH_TRIAGE** — prior triage is no longer "recent enough" to anchor the thread |
| 2h-24h ago | drift | **POST_FRESH_TRIAGE** — drift + age both warrant |
| >24h ago | either | **POST_FRESH_TRIAGE** — likely new cron reader, treat as first encounter |

The 2h-24h row for identical items is the trap: a probe returning `POST_FRESH_TRIAGE` on an aged-but-identical batch often produces noise (the prior comment already covered everything). **But** when probe returns `POST_FRESH_TRIAGE` due to drift (provenance ≠ identity-match), the comment is warranted even at 4-min age (r44 case).

## Provenance vs identity match

`probe_recurrence.sh` returns `POST_FRESH_TRIAGE` for two different reasons:
- **Age-based:** anchor age in 2h-24h window (no prior triage under 2h)
- **Drift-based:** set diff non-empty (items added or removed)

The agent must check which reason fired before posting. If drift-based AND <2h age, **still post** (material change). If age-based AND no drift AND anchor age >24h, post fresh triage treating it as a first encounter. If age-based AND drift AND 4-6h age, post focused on drift delta (r44 pattern).

## Drift-delta comment shape (the r44 canonical)

```
## Ned routing triage — 2026-06-26 HH:MMZ (drift detected, Nth feed)

**Anchor:** GRO-570 (canonical Ned-scan-triage anchor)
**Probe verdict:** POST_FRESH_TRIAGE — drift detected vs r(N-1) batch (last triage ~XhYm ago, in 2h-24h window)
**Linear comment posted:** yes (this one)
**finalize_task.sh invoked:** NO

### Drift delta vs r(N-1) (HH:MMZ)

N items dropped from scanner feed since r(N-1):
- GRO-XXX (reason: completed / state change / re-routed)
- ...

M items added.

### Current batch (all misrouted, all Backlog) — same lane-validation table as usual

| Lane | Last Ned comment |
| ... |

### Live infra probes (delta table)

(same as suppression-style audits)

### Standing alerts (carry-over, no change from rN-(N-X))
1. GPU down ...
2. GRO-565 IRS ...
```

The drift comment is **shorter than a first-encounter triage** — it doesn't re-justify why each item is misrouted (the prior comment did that), it just announces what changed and confirms carry-over infra alerts.

## Per-item policy when drift detected

For each item in the current batch:
- **If the item has a recent Ned comment (<24h):** anti-fan-out holds, don't re-comment
- **If the item has 0 Ned comments:** check if it's been deferred per established disposition (e.g. GRO-543/542/538 are r25/r33/r41/r42/r43-deferred Beyond-SaaS content/marketing lane — adding a Ned comment now would be a lane-violation)
- **If the item is NEW in the batch (drift-added):** validate lane, post only if actionable in Ned's lane

The drift comment covers all three cases without per-item commentary — the per-item verdict table is enough.

## Anti-pattern: posting per-item comments on drift

The wrong move is to post 10 separate comments (one per scanner item) when drift is detected. This:
- Pollutes Michael's notifications
- Triggers Linear subscriber spam on items he hasn't actioned
- Duplicates the routing-triage content (the drift-delta comment already documents why each item is misrouted)

**Always post one drift-delta comment on the anchor**, not N comments on the N items. This is the same anti-fan-out discipline that holds for non-drift runs.
