# r52 Case Study — 2026-06-27 00:57Z

**Anchor state:** GRO-570 (canonical) moved to **In Review** state at session start. First time in the rN+ chain where the anchor is NOT in Backlog.

**Tick:** 2026-06-27 ~00:57Z (cron run via the recurring misroute sweep).
**Verdict:** POST_FRESH_TRIAGE (drift present: 2 items added, 5 removed vs 23:24Z baseline).
**Comment ID:** `fd1a8695-1e15-4653-916b-b0ff9cadfd45` posted on GRO-570.
**Audit:** `okf/audits/ned-scan-triage-2026-06-27-r2.md`.

## Key new findings

### 1. Anchor can leave Backlog — commentCreate still works, but be careful

The GRO-570 anchor moved from Backlog → In Review between r46 (23:24Z) and r52 (00:57Z). This is the first time in the rN+ chain where the anchor is not in `Backlog`/`Todo`/`In Progress`.

**Implications:**
- `commentCreate` mutation on an In Review issue **works fine** — confirmed at r52, posted successfully.
- `state` and `label` mutations also work on In Review issues (Linear doesn't restrict In Review from being mutated, unlike Canceled/Duplicate).
- **However:** the recurrence-probe script's filter (`state.name in ["Backlog", "Todo", "In Progress"]`) might exclude In Review anchors from the team-level query. If the anchor moves to In Review and you re-walk the team filter, the anchor is invisible to the probe's broad-fetch logic. **Fix when this matters:** explicitly include In Review + Done in the team filter, OR keep a separate `state.name = "In Review"` lookup for the canonical anchor.

For r52 specifically, the broader no-state-filter walk (page 20+) found GRO-570 with state In Review. The audit reflects both states.

### 2. Mode C finalize_task.sh auto-transition — second canonical example

GRO-565 had a `finalize_task.sh` run at 2026-06-26 23:40:38Z that auto-transitioned it to "In Review" — the same Mode C bug class documented at r5. The state churn was caught by an immediate correction comment at 23:40:49Z (11 seconds later) reverting GRO-565 to Backlog.

**Why it matters:** the `linear-agent-operations` SKILL.md §6 has a "finalize_task.sh is robust to contaminated working trees" pitfall, but the **Mode C state churn** failure mode (finalize_task.sh auto-moves state even when the agent did no real work) is a separate, more dangerous bug. It can fire when:

- The cron `Last action: bash finalize_task.sh ...` directive runs even though the agent refused execution in the body.
- The finalize script's transition logic doesn't check whether the agent actually committed any code.
- The agent's "no work to do" exit code is misinterpreted as "work complete."

**Detection pattern (what r5/r52 got right):**
- Watch for any Linear comment that posts within seconds of a `finalize_task.sh` run, containing "Mode C fix" or "Correction" or "reverted to Backlog" — these are the recovery comments from a prior finalize_task.sh state-churn incident.
- **Always check the latest 2–3 comments on the items in the current scanner feed**, not just the latest 1, before deciding to run finalize. If you see a Mode C correction comment, the cron directive's "bash finalize_task.sh" has already been satisfied (and produced false work); don't run it again.

### 3. GPU node sustained dual-interface outage — escalating to "physical-dead" tier

At r52 (00:57Z), the GPU node has been unreachable on **both Tailscale (100.78.237.7) AND LAN (192.168.1.230)** for ~27+ hours (since before r41 at 21:55Z, possibly earlier). The skill currently says "Default to LAN-probing on the third consecutive tick of GPU-down" — r52 extends this with a duration threshold:

| Outage duration | Tier | Action |
|---|---|---|
| <2h | Likely flap | Mention in delta table, no alarm |
| 2–12h | Network-path suspected | Continue Tailscale+LAN probes; check PVE6 + adjacent hosts |
| 12–24h | Sustained, hardware suspected | Continue probes; recommend physical inspection in cron reply |
| 24h+ | **Treat as permanently dead** | 🔴 Escalate as critical infra in headline of cron reply; recommend scheduled physical check; stop expecting recovery between ticks |

At r52 the node crosses the 24h tier. The cron reply headlines "GPU node ~27+ hours down" rather than just tabling it in the delta — a sustained-down item should never be a delta-table footnote.

### 4. First-time triage on drift-added items — post on the anchor, not on the new item

GRO-538 and GRO-542 were added to the scanner feed since the 23:24Z baseline and have **no prior Ned triage comment** on them. The skill says "post fresh triage on drift" but doesn't explicitly say where. **The drift-triage comment goes on the canonical anchor thread (GRO-570), NOT on each new item individually.**

**Why:**
- The anchor is where Michael already looks for the recurring-sweep story.
- Posting on each new item would create N parallel threads and dilute the routing-bug narrative.
- The drift-delta section in the anchor comment lists the added items with their lane-correct owner — Michael can click through to each from the anchor comment.
- One Linear comment per drift event keeps the noise-free ratio high (the existing 91–95% across the rN+ chain).

**Counter-example:** if a drift-added item is a **carve-out** (e.g. physically unactionable like GRO-703, or genuinely Ned-lane), post a separate comment on that item because it needs its own narrative thread. For pure misroute items, batch them into the anchor's drift-delta section.

### 5. Local workspace contains only r1 + r52 audits — broader rN chain lives elsewhere

At r52, only `okf/audits/ned-scan-triage-2026-06-26-r1.md` and the new `ned-scan-triage-2026-06-27-r2.md` exist in this workspace. The skill narrative references r5, r19, r38, r41, r46, r47, r48, r50 — those audits live in a different workspace or repo.

**Implication for audit numbering:** don't try to guess the rN counter from the skill narrative. Use the local counter (`okf/audits/`) and add a `rN` suffix that increments from the highest existing local file. The skill-narrative rN is a different chain in another workspace — the local chain is independent.

**Recommended:** when writing a new audit, `ls /home/ubuntu/work/okf/audits/ned-scan-triage-*.md | sort` and pick `rN+1` where N is the highest local counter. This session used `r2` because the local highest was `r1`.

## Drift delta at r52

**PERSIST:** GRO-567, GRO-565, GRO-564, GRO-559, GRO-558, GRO-557, GRO-545, GRO-543

**ADDED (NEW first-time-in-sweep):**
- GRO-538 "Create About page with founder story and team" — marketing/content lane
- GRO-542 "Implement Contact and Booking flow" — web dev lane

**REMOVED (no longer in scanner feed):**
- GRO-546, GRO-551, GRO-570 (anchor → In Review), GRO-571, GRO-572, GRO-608

Decision per the SKILL.md table: items not identical (drift) + last triage age 75–92 min (<2h) → **POST_FRESH_TRIAGE**.

## Carry-over infra findings (r52)

| Probe | Current (00:57Z) | Last probe (r41 21:55Z) | Delta |
|---|---|---|---|
| GPU Tailscale | ❌ UNREACHABLE | ❌ UNREACHABLE | **unchanged — ~27h+ sustained** |
| GPU LAN | ❌ UNREACHABLE | ❌ UNREACHABLE | **unchanged — physical box-off confirmed** |
| Ollama HTTP | ⚠️ offline | ⚠️ offline | unchanged |
| PVE6 | ✅ reachable | ✅ reachable | unchanged |
| Hermes VM disk | 🟢 29% | 🟢 ~30% | unchanged, no rate anomaly |

🔴 **GPU node has crossed the 24h outage tier** (see §3 above) — escalate in cron reply headline, not just delta table.

🔴 **GRO-565 IRS Q2 estimated tax payment** — 11+ days past 2026-06-15 deadline. Daily penalty accrual. ~26h since first Michael escalation (2026-06-25 23:15Z), no action observed. Michael-direct, not Ned autonomous.

## Recommendation

1. Same as r1 audit + prior triages: fix the scanner-config so the routing-sweep stops surfacing content/marketing/CPA items to Ned's queue. The 10-item list has been leaking for >24h.
2. **Physical GPU node inspection** — sustained dual-interface downtime (~27h+) indicates power/hardware fault.
3. **GRO-565** — escalate IRS penalty to Michael again, or accept the loss and file extension.

## Files of record

- `okf/audits/ned-scan-triage-2026-06-27-r2.md` — full audit for this tick.
- `okf/audits/index.md` — updated with the r52 row.
- Linear comment `fd1a8695-1e15-4653-916b-b0ff9cadfd45` — posted on GRO-570 anchor.