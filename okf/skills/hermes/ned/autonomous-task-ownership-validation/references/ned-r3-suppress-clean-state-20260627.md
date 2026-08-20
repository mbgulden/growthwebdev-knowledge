# r3 Case Study — 2026-06-27 ~01:59Z

**Anchor state:** GRO-570 (canonical) still in **In Review** state — the new steady-state per r52.

**Tick:** 2026-06-27 ~01:59Z (cron run via the recurring misroute sweep).
**Verdict:** SUPPRESS (anchor newest triage = 61.7 min < 2h; items identical to r2 at 00:57Z).
**Linear comment posted:** none.
**Audit:** none written (per SUPPRESS verdict — the audit chain lives in `growthwebdev-knowledge`, not in this workspace).

## Key new findings

### 1. `updatedAt` ≠ state transition (the headline pitfall of this tick)

On the r3 verification pass, four items showed `updatedAt` newer than the anchor's newest triage comment:

| Item | updatedAt | Anchor newest triage | Delta |
|---|---|---|---|
| GRO-558 | 2026-06-27T01:58:32Z | 2026-06-27T00:57:53Z | +60.6 min newer |
| GRO-543 | 2026-06-27T01:23:31Z | 2026-06-27T00:57:53Z | +25.6 min newer |
| GRO-542 | 2026-06-27T01:23:32Z | 2026-06-27T00:57:53Z | +25.7 min newer |
| GRO-538 | 2026-06-27T01:23:33Z | 2026-06-27T00:57:53Z | +25.7 min newer |

On first glance this looks like "drift happened between the anchor's last triage and now" — which would push toward POST_FRESH_TRIAGE per the decision table. **But it's not drift.** All four bumps came from intra-batch triage comments posted by prior cron runs (the 01:23Z cluster and a fresh 01:58Z triage), not state transitions. All 10 items remained `state.name == "Backlog"`.

**Detection recipe (now in SKILL.md pitfalls):**
- For each script-feed item, fetch `state.name`, `updatedAt`, and `comments(last:2).nodes[].createdAt`.
- If `state.name` is unchanged AND the recent `updatedAt` is explained by a comment (look at `comments(last:2).nodes[].createdAt`), it's NOT drift.
- The drift decision is based on (a) item set identity, (b) state identity, (c) the **anchor's** newest triage comment age — not per-item `updatedAt` variance.

This catch prevented a false-positive fresh-triage post on r3 — saving one Linear comment and one audit-doc write for a non-event.

### 2. Per-item triage-comment age ≠ anchor's

GRO-558 had a triage comment at 01:58:32Z (newer than the anchor's 00:57:53Z by ~61 min). A naive "newest comment anywhere in the feed" baseline check would have read 1.1 min and SUPPRESS would have been wrong-by-accident (the items WERE identical to r2 at 00:57Z, so the SUPPRESS verdict was right, but the reasoning would have been wrong).

**Rule:** the recurrence-probe baseline is the ANCHOR's newest triage comment age, not max-across-items. Anchor = GRO-570 = canonical Ned-scan-triage thread. Per-item triage comments are intra-batch side effects that *support* SUPPRESS (they prove prior cron runs saw the same misroute), not contradict it.

### 3. Anchor in In Review is the new steady-state

GRO-570 has been in `In Review` since before r52 (00:57Z). At r3 (01:59Z) it's still there — confirming the r52 finding that the anchor can leave Backlog and the recurrence probe still works.

**Concrete evidence the probe still works at r3:**
- `comments(last: 15)` on the In Review anchor returned 14 comments
- `comments(last: 25)` returned 14 (no truncation issue at this size)
- All comment timestamps were returned in chronological order
- Direct `issue(id: $GRO570_UUID)` query worked (no team-filter gate needed)

**Implication for `probe_recurrence.sh`:** the script must use a direct `issue(id: ...)` lookup for the anchor baseline, not rely on the team-level `issues()` filter. If the script's team filter excludes `state.name = "In Review"`, the anchor disappears and the probe loses its baseline. This is now in the SKILL.md pitfalls.

### 4. `comments(last: N)` — N=15 vs N=25 for high-frequency anchors

GRO-570 had 14 comments at r3. `comments(last: 15)` returned all 14 (with 1 buffer slot). This was adequate for r3 but won't scale — the anchor is gaining comments every drift-triage event. If a future run sees 20+ comments and the probe uses `last: 15`, a buggy prior-run stale comment could push out the actual newest entry.

**Recommended default: `comments(last: 25)`** for recurrence probes on canonical anchors. 25 is well under Linear's per-field pagination cap (50) and gives headroom for 2× the comment volume of r3. Verified working at r3.

## Decision walkthrough for r3

1. **Recurrence probe on GRO-570:** `comments(last: 15)` → 14 comments. Newest = `2026-06-27T00:57:53.629Z` by Michael Gulden, body starts "[Ned cron triage — 2026-06-27 ~00:57Z — recurring Backlog sweep, drift present]". That body matches the Ned-triage filter (contains "Ned", "triage", "cron", "routing").
2. **Age calculation:** current = 01:59:37Z, newest = 00:57:53Z → **61.7 min**.
3. **Decision-table lookup:**
   - Last triage age: 61.7 min (< 2h threshold)
   - Items identical to last triage: yes (script-feed = 567/565/564/559/558/557/545/543/542/538 = identical to r2 documented drift-delta)
   - **Verdict: SUPPRESS** — no new Linear comment, no `finalize_task.sh`.
4. **Per-item `updatedAt` variance check:** 4 items showed `updatedAt > anchor newest triage`. Cross-check via `comments(last:2)` confirmed all four were triage comments, not state transitions. No drift override.
5. **Lane-fit verification:** 0-of-10 match Ned (3 finance/CPA, 7 content/marketing) — same as r1/r2/r38–r52.
6. **Infra probes:** GPU Tailscale + LAN both 100% loss (~28+ hours sustained), PVE6 reachable, disk 29%.

## Infra findings (carry-over from r2)

| Probe | r3 (01:59Z) | r2 (00:57Z) | Delta |
|---|---|---|---|
| GPU Tailscale (100.78.237.7) | 🔴 100% loss | 🔴 100% loss | unchanged — sustained ~28h+ |
| GPU LAN (192.168.1.230) | 🔴 100% loss | 🔴 100% loss | unchanged — physical box-off confirmed |
| Ollama HTTP (100.78.237.7:31434) | ⏱️ timeout | ⚠️ offline | unchanged |
| PVE6 (100.90.63.4) | 🟢 reachable 1.38ms | 🟢 reachable | unchanged |
| Hermes VM disk `/` | 🟢 29% (84G/292G) | 🟢 29% | unchanged |

🔴 **GPU node has crossed the 24h outage tier (per r52 escalation rules)** — sustained dual-interface downtime. Physical power check / IPMI needed. Not a recovery candidate between cron ticks.

🔴 **GRO-565 IRS Q2 estimated tax payment:** 12+ days past 2026-06-15 deadline. Daily penalty accrual continues. Sam/CFO lane, not Ned autonomous. Standing escalation unchanged.

## Cron-reply discipline at r3

- ✅ Recurrence probe + manual `comments(last:25)` cross-check
- ✅ Per-item state verification (`state.name` for all 10)
- ✅ `updatedAt` drift override check (comments vs state changes)
- ✅ Live infra probes (Tailscale + LAN + Ollama + PVE6 + disk)
- ❌ NO `finalize_task.sh` invoked
- ❌ NO empty commits to `prismatic-engine`
- ❌ NO fake "In Review" transitions
- ❌ NO new Linear comment (SUPPRESS verdict — anti-fan-out window holds)
- ❌ NO audit doc written (r2 already documented; the r3 cron reply is the deliverable)

## Cumulative noise-free ratio at r3

3 cron runs in this 2026-06-27 ~01:59Z workspace session, **1 Linear comment posted on the 10-item batch** (the r2 first-encounter-style drift-triage). 2/3 = 66% noise-free this session. Skill-canonical case study (across the broader rN+ chain) holds at **~92% noise-free**.

## Recommendation (unchanged from r2)

1. Fix scanner-config — `scan_tasks.py` lacks explicit `agent:ned`-only gate; has been leaking this 10-item misroute for >24h.
2. Physical GPU node inspection — ~28h dual-interface downtime, treat as permanently dead until physically verified.
3. Resolve GRO-565 IRS penalty — accept loss or pay (Sam / Michael-direct).

## Files of record

- `okf/audits/index.md` — updated by r2; no r3 row added (SUPPRESS, no audit written).
- No Linear comment posted this tick (correct per SUPPRESS verdict).
- This reference file is the canonical r3 case-study doc — captures the `updatedAt` ≠ drift pitfall and the per-item-vs-anchor baseline refinement.