# Curator-Flag Stale-Backlog Misroute Fingerprint

**Codified:** 2026-06-30 ~02:14Z (Pass-N+32, first observation)
**Updated:** 2026-06-30 ~04:43Z (Pass-N+42, multi-wave + interview-trap refinements)
**Author commit:** `9021904b` on `ned/gro-485-triage-pass-1`
**Anchor evidence:** `cc9427ce-342f-410a-bad4-364a641260d4` on GRO-146
**Newest evidence (Pass-N+42):** anchor `fdb2fe2d-9223-4b96-9aaa-27212b84fcef` on GRO-24

---

## The fingerprint (100% reliable signature)

When a fresh scanner feed has ALL of the following:

1. **Zero overlap** with every prior registered rotation pool (Batch A `GRO-594..2976`, Batch B `GRO-484..502`, GRO-146..165 stale-backlog chain).
2. **>50% of the feed** (typically 10/10) carries an identical orchestrator-side comment:
   > ## Curator flag: Stale backlog issue (no agent label for >48h)
3. The curator flags were posted within a **<10-minute window** (Pass-N+32: 7 sec; Pass-N+42: 7 sec).
4. **All** carry the `agent:ned` + `dispatch:ready` label pair auto-applied by the orchestrator-side dispatcher immediately after the curator flag.

Then it's a **100% reliable signature of orchestrator-side stale-backlog auto-routing** via the GRO-559 dispatcher bug. Cure is at the dispatcher level, NOT the per-issue level.

---

## Why recurring-batch detector signatures can never cover this

The pool grows monotonically. Pass-N+19 estimated ~13 IDs; Pass-N+32 found 26; Pass-N+42 found ~36. The pool is unbounded — it grows at the rate of `(backlog_velocity / orchestrator_tick_interval) × wave_size` until the dispatcher fix lands.

Detector signature by set-membership fails because:
- New IDs are added to the pool every time the orchestrator tick fires.
- A set-membership check like `if ID in {Batch A ∪ Batch B ∪ Pass-N+32 pool}` returns FALSE for newly rotated-in IDs.
- The pool grows ~10 IDs per orchestrator wave; the detector would have to track the union of every wave ever observed.

**Realistic detector signature** (suggested but not yet implemented):

```
classification: stale_backlog_auto_routing
when:
  curator_flag_density >= 0.5
    ∧ LAST_COMMENT_TIMESTAMP_CLUSTER_WIDTH < 600s
    ∧ all(labels has "agent:ned")
    ∧ all(labels has "dispatch:ready")
```

---

## Multi-wave same-window firing (Pass-N+42 first observation)

The GRO-559 dispatcher bug does NOT fire one wave per cron tick. It fires **multiple ~10-ID slices per orchestrator tick**. Evidence:

- Pass-N+32's 10 IDs (GRO-146..165) curator-flagged at 2026-06-29T15:54:05Z–15:54:12Z.
- Pass-N+42's 10 IDs (GRO-24/55/93/116/138-143) curator-flagged at the SAME 2026-06-29T15:54:05Z–15:54:12Z window.
- Both waves were auto-routed within ~7 seconds of each other, NOT across separate cron ticks.

Implication: the dispatcher applies the `stale_backlog` filter to a sorted-by-age list and slices into ~10-ID windows. Multiple slices per orchestrator tick. Each slice enters Ned's scanner feed as a new rotation pool that appears "fresh" (no overlap with prior batches).

**Pool growth curve (convex, not linear):** ~13 → ~16 → **~26** → **~36** over 23 passes (Pass-N+19 → Pass-N+29 → Pass-N+32 → Pass-N+42). Multi-wave firing increases the rate of pool expansion.

---

## Multi-agent epic detector gap (GRO-149 case)

Pass-N+32's feed contained GRO-149, whose description said "**14-week** Honeybadger buildout" and listed 6+ phases. Single-issue cron-pass handed a multi-week epic is **doubly-wrong**:

1. **Wrong lane.** Multi-agent cross-cutting epics belong with the orchestrator, not a lane-specific specialist.
2. **Wrong granularity.** A single Ned pass cannot execute a 14-week buildout; the issue belongs in a project with sub-tasks, not a single Linear ticket dispatched to one agent.

**Recipe:** when an `agent:ned`-labeled issue has description containing `week` OR `(?<=\d+\s)phase` OR `sub-?task`, do NOT partition to a lane-fit specialist. Recipe is `PASS_TO_ORCHESTRATOR` (post anchor, log to orchestrator's intake queue) rather than dispatch to Ned for execution. Hard-block `finalize_task.sh` — there's no single issue to finalize.

---

## Interview-content fabrication trap (Pass-N+42 first observation)

Pass-N+42's feed contained 6/10 content interviews:

- GRO-138 (YHG Kayak Routes & Safety) — "Michael's expert first-hand knowledge..."
- GRO-139 (YHG Tour Operator Comparisons) — same shape
- GRO-140 (YHG Best Beaches) — same shape
- GRO-141 (YHG Oahu by Region) — same shape
- GRO-142 (AOT Mokes — assigned to "Ella") — "Ella, answer these however is easiest"
- GRO-143 (AOT Chinamans Hat — assigned to "Ella") — same shape

The lane-partition walk MUST mark these rows `HARD-SKIP \`finalize_task.sh\`` with reason **"fabricating expert voice"** rather than just "wrong lane — relabel." Even after the curator flag is corrected and the issue is relabeled `agent:fred`, no agent can synthesize another human's expert kayak/beach/Mokes/Chinaman's-Hat knowledge into prose on their own without fabrication.

The standing cure is to **relabel and route to Michael/Ella for actual recording**. No agent generates the interview answers.

---

## Standing cure (orchestrator-side patch — GRO-559 territory)

Patch `~/.hermes/profiles/orchestrator/scripts/post_publish_audit_v2.py` (or equivalent):

```python
# BEFORE: auto-apply agent:ned to any stale-backlog item
def label_stale_backlog(issue):
    if is_stale(issue) and not issue.labels.has_any_agent():
        issue.add_label("agent:ned")
        issue.add_label("dispatch:ready")

# AFTER: only apply to items whose PROJECT is in Ned's lane
NED_LANE_PROJECTS = {
    "Prismatic Engine",
    "Agentic Swarm Ops Documentation",
    # add others per lane-ownership table in SWARM.md
}
def label_stale_backlog(issue):
    if is_stale(issue) and not issue.labels.has_any_agent():
        if issue.project.name in NED_LANE_PROJECTS:
            issue.add_label("agent:ned")
            issue.add_label("dispatch:ready")
        else:
            issue.add_label("agent:auto-stale")  # generic, requires Michael triage
```

This is **cross-profile write territory** for Ned — coordinate with the orchestrator before patching.

---

## Quick-check recipe for the next Ned pass

When you see a 10-issue feed where >50% carry an identical curator-flag comment:

1. **Confirm the fingerprint.** Run `comments(last: 1)` on the lowest-GRO-ID; if it shows `## Curator flag: Stale backlog issue (no agent label for >48h)`, fingerprint matches.
2. **Check the project + lane.** For each issue, compute the correct lane per the lane-ownership table. If 0/10 in Ned's lane, this is a curator-flag-stale-backlog misroute.
3. **Apply the rotation-equivalence ratchet.** Criteria (a) + (b) always HOLD for this fingerprint. Criterion (c) requires checking the prior-pass anchor body for the 10 IDs.
4. **Execute the Pass-N+19 actual-execution recipe** if criterion (c) FAILS:
   - Audit doc at `scripts/ops/gro-<lowest>-<highest>-batch-routing-Nth-pass-infra-findings.md`
   - Commit on `ned/gro-485-triage-pass-1` with `[Ned]` prefix
   - Anchor comment on the **new lowest-GRO-ID** (not the prior pass's anchor target)
   - Final response: `[SILENT]`

---

## Filesystem evidence trail

- Pass-N+32 commit: `9021904b` on `ned/gro-485-triage-pass-1`
- Pass-N+42 commit: `0632df8a` on `ned/gro-485-triage-pass-1`
- Pass-N+32 anchor: `cc9427ce-342f-410a-bad4-364a641260d4` on GRO-146
- Pass-N+42 anchor: `fdb2fe2d-9223-4b96-9aaa-27212b84fcef` on GRO-24
- Pass-N+32 audit doc: `scripts/ops/gro-146-165-batch-routing-32nd-pass-infra-findings.md`
- Pass-N+42 audit doc: `scripts/ops/gro-24-143-batch-routing-42nd-pass-infra-findings.md`
- Ned's branch: `ned/gro-485-triage-pass-1` (single-day log; 42 commits deep after this pass)
