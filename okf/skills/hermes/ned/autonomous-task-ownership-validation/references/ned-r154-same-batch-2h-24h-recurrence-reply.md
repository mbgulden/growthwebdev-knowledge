# Ned r154 — Same-batch recurring in the 2h–24h window: reply shape

**Date:** 2026-06-29 ~20:40Z (r2 of 2026-06-29)

## What this case is

The cron preamble returns the same 10-item misroute batch that Ned triaged 2h–24h ago (today: 5h58m ago on GRO-485, the 5th pass at 14:42:13Z + this 6th pass at 20:40Z). Items are byte-identical. The skill's r59 mechanical-SUPPRESS rule applies — but the **<2h literal case** (covered in r1 of the day, where last triage was 90 min ago) and the **2h–24h same-batch case** (this r2) both produce SUPPRESS, with one practical difference in reply shape.

## Why reply shape differs

- **<2h case:** the prior triage is so recent that a fresh recurrence statement risks reading as "still here, still the same misroute" — minimum 6-line reply.
- **2h–24h case:** the prior triage is several hours old, so the reader may have forgotten the routing-bug context. A slightly fuller recurrence statement that re-anchors the misroute (table of 10 items → lane-fit → owner) is warranted, but **without re-posting the per-issue triage comment to Linear** (which would be the Theater-adjacent failure mode of churn-posting on a stable state).

## Reply template (validated r2 of 2026-06-29)

```
🔴 Routing sweep misfire — same 10 items, ~Nh since last triage. **No Linear comment, no `finalize_task.sh`.**

| ID | Title | Lane-fit |
|---|---|---|
| GRO-... | ... | ❌ <owner> |
| ... (10 rows, all ❌ not-infra) |

**N/10 match Ned's lane.** Effective anchor = <anchor-ID> (canonical GRO-570 absent from feed);
last Ned-triage on anchor <HH:MM:SSZ> (~Nh ago) → 2h–24h window → **r59 mechanical-SUPPRESS** applies.
Running `finalize_task.sh` would auto-promote Backlog→In Review on N misrouted items = Theater Failure Mode.

**Infra delta (<HH:MMZ> vs <prior HH:MMZ>):**

| Probe | Now | Prior | Delta |
|---|---|---|---|
| GPU Tailscale <ip> | 🔴/🟢 | 🔴/🟢 | unchanged / <rate> |
| GPU LAN <ip> | ... | ... | ... |
| Ollama HTTP :<port> | <code> | <code> | unchanged |
| PVE6 <ip> | ✅ | ✅ | unchanged |
| Hermes VM disk | 🟢 N% (used/total) | 🟢 N% | unchanged |
| Synology NAS | N% (used/total) | N% | unchanged |

**Carry-over escalation:** (optional, only if a real finding persists across passes — GPU node down for Nh, disk climbing, etc.)

Audit written: `/home/ubuntu/work/okf/audits/ned-scan-triage-YYYY-MM-DD-rN.md` · Index updated.
```

## Reply shape variants

The 2h–24h reply template above is the **clean** case (no infra deltas,
no wrapper-side incidents to recover from). Two variants add sections:

- **SUPPRESS-with-Symptom-2-recovery** (e.g., Pass-17 2026-06-29
  ~20:58Z): when the push step surfaces a wrapper-leaked
  auto-commit from a prior pass, the reply must add an "Actions taken"
  section showing: wrapper SHA identified, file extracted via
  `git show <wrapper-sha>:<path> > /tmp/<file>`, reverted, restored to
  `.fred-*-prefixed` working-tree location, push re-attempted and
  approved. See `references/okf-prepush-hook-silent-block-detection-and-lane-governance-gap.md`
  §"Pass-17 refinement" in `ned-autonomous-task-loop` for the full
  recipe. Without this section, a reader scanning the cron reply
  misses the fact that the audit doc only landed after a wrapper-leak
  remediation.

- **SUPPRESS-with-infra-escalation** (per the table in main SKILL.md):
  when the infra-delta table crosses the warn/critical/catastrophic
  thresholds, the reply stays as the template above but the infra
  table gets a "Michael action required" line with specific
  intervention steps. The 2h–24h context-re-anchor table stays.

In all cases the **decision rationale** (SUPPRESS per r59 + 2h–24h +
items-identical) stays at the top of the reply so a reader doesn't
have to scroll to find why Ned didn't post a Linear comment.

## Key differences vs <2h case

1. **Header says "Nh since last triage"** (specific number), not "same as recent" — re-anchors context for a reader who may have forgotten.
2. **Per-item lane-fit table is kept inline** in the reply, not just the audit doc — because the prior triage was several hours ago, the routing-bug context needs re-surfacing in the channel.
3. **Infra-delta table is mandatory** (not optional). The carry-over infra findings are why the suppression on Linear doesn't translate to silence in the cron reply — the cron reply IS the delivery channel for infra deltas.
4. **Audit doc still gets written** with full per-issue ownership mapping + decision rationale. The cron reply is the delivery; the audit doc is the durable record.

## Don't do this in the 2h–24h case

- ❌ **Don't post a new Linear comment** to the anchor or any batch member. The thread already carries 6+ Ned-triage comments today; one more is churn.
- ❌ **Don't shorten the reply below 6 lines** even though the verdict is SUPPRESS. The 2h–24h window means the prior-triage context has faded; a one-liner "still misroute" reads as low-signal.
- ❌ **Don't re-run the broad lane-filter query** to prove "0 actionable" — the SUPPRESS verdict from this single probe is already authoritative for the current 10-item feed.
- ❌ **Don't write a fresh "first encounter" template** — this is recurrence, not first sight. The 3-component "routing error / owner / infra findings" template from `references/ned-refusal-template-20260625.md` is for first encounters; recurrence uses this r154 template.

## Audit trail

- Reply template validated: 2026-06-29 r2 (~20:40Z) → 10/10 items SUPPRESS, no Linear mutation, audit `ned-scan-triage-2026-06-29-r2.md` written, `index.md` row added.
- This is the 6th cron pass on the same Batch B (GRO-484/485/486/487/488/490/492/499/500/502) today; r1 of 2026-06-29 (~13:31Z) was the <2h literal case; r2 of 2026-06-29 (~20:40Z) is this 2h–24h case.
- Both r1 and r2 SUPPRESS per r59, but the reply shape differs per this template.

## Cross-references

- r153 anchor-shift: `references/ned-r153-batch-anchor-shift-20260629.md`
- r59 mechanical-SUPPRESS rule: main SKILL.md, "Stale-Backlog Sweep" section, decision table
- 3-component first-encounter template: `references/ned-refusal-template-20260625.md`