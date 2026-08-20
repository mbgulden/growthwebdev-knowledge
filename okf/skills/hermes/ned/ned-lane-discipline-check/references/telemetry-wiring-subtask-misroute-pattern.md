# Telemetry-wiring sub-task auto-routing pattern (GRO-2990..3012, Pass-N+44, 2026-06-30 ~10:05Z)

**Codified from Pass-N+44 — the first observation of telemetry-wiring-sub-task auto-routing as a distinct dispatcher-trap signature.** This is a *third* dispatcher-trap signature distinct from the Pass-N+32 curator-flag fingerprint and the Pass-N+42 interview-fabrication trap. All three share the same underlying GRO-559 dispatcher bug (auto-applies `agent:ned` + `dispatch:ready` to issues lacking a correct lane label), but each surfaces differently and requires its own detector heuristics.

## When this pattern applies

The scanner feed contains 10 `agent:ned`-labeled issues where:

1. **≥50% carry the `[Ned]` tag in their title** (e.g. `[Ned] GRO-2980.1 — Wire record_tokens() at LLM call sites`).
2. **Their acceptance criteria mention `telemetry_*` table writes, hook bus, plugin loader, pipeline state transitions, LLM call sites, vertex/gcp spend events, or process observer/dispatch caps.**
3. **The cure lives outside Ned's lane** — typically in `~/.hermes/profiles/orchestrator/scripts/` (orchestrator profile's dispatcher, supervisor, or poller scripts).
4. **A prior Ned investigation has already root-caused the family** that these sub-tasks belong to (e.g. GRO-2981 for telemetry-silence, GRO-2980 sub-tasks; or another investigation for other families).

This is the **Pass-N+20 in-lane-but-subsumed pattern applied to a FAMILY of sub-tasks** — the prior investigation root-caused the underlying pathology, and the scanner rotated in the family members as separate-but-related issues. The cure is shared; building per-issue investigations for the sub-tasks duplicates the prior investigation's findings without producing actionable in-lane code.

## Pass-N+44 canonical example (GRO-2990..3012 batch)

The 10-issue scanner feed at 10:05Z on 2026-06-30:

| # | ID | Title (truncated) | Partition |
|---|----|--------------------|-----------|
| 1 | GRO-2990 | [Ned] GRO-2980.1 — Wire record_tokens() at LLM call sites | ⚠️ subsumed by GRO-2981 (orchestrator-side launch path bypasses all `record_*` writers; cure is in orchestrator lane) |
| 2 | GRO-2991 | [Ned] GRO-2980.2 — Wire record_hook_fired() at hook bus | ⚠️ subsumed by GRO-2981 (`telemetry_hook_fired` is one of 5 always-zero tables per GRO-2981 §3) |
| 3 | GRO-2992 | [Ned] GRO-2980.3 — Wire record_pipeline_action() at pipeline state transitions | ⚠️ subsumed by GRO-2981 (same orchestrator-bypass pathology) |
| 4 | GRO-2993 | [Ned] GRO-2980.4 — Wire record_plugin_registered() at plugin loader | ⚠️ subsumed by GRO-2981 (same orchestrator-bypass pathology) |
| 5 | GRO-2995 | [Ned] GRO-2980.6 — Build gcp_vertex_spend_events INSERT writer | ⚠️ subsumed by GRO-2981 (Vertex telemetry write path runs in orchestrator poller; Ned lane lacks the poller boundary) |
| 6 | GRO-2996 | [Ned] GRO-2979.1 — Add process_observer_thread + dispatch caps to fix GRO-2051 retry storm | ⚠️ subsumed by GRO-2981 (retry storm = 27 rows from GRO-2051 window in GRO-2981's 635-row set; cure is orchestrator-side dispatch caps) |
| 7 | GRO-2998 | [SILENT-CRON] `Fred Persistent Factory Monitor — 48h watchdog` is silent-failing | ❌ wrong lane (Fred lane owns persistent factory monitor) |
| 8 | GRO-2999 | [SILENT-CRON] `Fred Persistent Factory Monitor — 48h watchdog` is silent-failing | ❌ wrong lane (duplicate of GRO-2998) |
| 9 | GRO-3011 | [SILENT-CRON] `AGY Sandbox Supervisor — event-driven organic scaling` is silent-failing | ❌ wrong lane (orchestrator lane owns the supervisor) |
| 10 | GRO-3012 | [SILENT-CRON] `AGY Sandbox Supervisor — event-driven organic scaling` is silent-failing | ❌ wrong lane (duplicate of GRO-3011) |

**Partition walk result: 6/10 in-lane-but-subsumed + 4/10 wrong-lane = 0/10 executable in Ned lane.**

## Why this is a distinct signature from prior dispatch-traps

| Trap signature | Codified pass | Detector signal |
|----------------|---------------|-----------------|
| Recurring-batch rotation within stable pool | Pass-N+19 (~13 IDs) | `RECURRING_BATCH_SIGNATURES` set-membership check; same family IDs across passes |
| Curator-flag stale-backlog auto-routing | Pass-N+32 (~26 IDs) | `curator_flag_density >= 0.5 ∧ LAST_COMMENT_TIMESTAMP_CLUSTER_WIDTH < 600s ∧ all(labels has agent:ned ∧ labels has dispatch:ready)` |
| Interview-content fabrication trap | Pass-N+42 (~36 IDs) | Title or description begins with "Michael's expert first-hand knowledge of..." or names Michael/Ella for recording |
| **Telemetry-wiring sub-task auto-routing (NEW — Pass-N+44, ~46 IDs)** | This pass | `≥50% titles contain "[Ned]" AND ≥50% titles mention telemetry_*, record_*, hook bus, plugin loader, pipeline state, vertex/gcp, process observer, dispatch caps` |

**Pool growth curve (cumulative):** ~13 (Pass-N+19) → ~16 (Pass-N+29) → ~26 (Pass-N+32) → ~36 (Pass-N+42) → **~46 (Pass-N+44)**. Pool growth tracks `~10 IDs per ~24h cron cycle` while GRO-559 fix remains un-landed. All three signatures are downstream of the same GRO-559 dispatcher bug.

## Detector extension (recommended patch to `scripts/suppress_class_detect.py`)

Add a `TELEMETRY_WIRING_SUBTASK_HEURISTIC` check to the detector's classification pipeline:

```python
def is_telemetry_wiring_subtask_misroute(issue):
    """Pass-N+44 detector: GRO-2990..3012-style auto-routed sub-tasks."""
    title = (issue.title or "").lower()
    desc = (issue.description or "").lower()
    has_ned_tag = "[ned]" in title
    has_telemetry_keyterm = any(
        kw in title or kw in desc
        for kw in [
            "telemetry_", "record_tokens", "record_hook_fired",
            "record_pipeline_action", "record_plugin_registered",
            "record_agent_run", "hook bus", "plugin loader",
            "pipeline state", "vertex", "gcp spend",
            "process observer", "dispatch cap", "retry storm",
            "wire ", "insert writer",
        ]
    )
    return has_ned_tag and has_telemetry_keyterm
```

When ≥5 of 10 scanner-feed issues trigger `is_telemetry_wiring_subtask_misroute`, classify the feed as `telemetry_wiring_subtask_misroute` and apply the Pass-N+20 subsumption recipe automatically.

## Pass-N+20 subsumption checklist (apply to all `[Ned]` tagged items)

For each rotated-in ID that the partition walk flags as in-lane, apply the 4-point checklist from `references/in-lane-subsumed-by-prior-investigation.md`:

1. **Prior root-cause commit exists.** A commit on `ned/<some-branch>` addresses the **family** of issues this ID belongs to. The commit message or audit doc names the architectural root cause, not just the single issue's symptom.
2. **Prior commit is recent and In Review or Done.** Typically within 24h of the current pass.
3. **This ID's acceptance criteria trace to the prior root cause.** The ID's description explicitly names a table / metric / behavior that the prior investigation already analyzed. GRO-2981's §"Related issues" lists all GRO-2980 family tables as downstream of the same orchestrator-bypass pathology.
4. **Cure is in another lane, not Ned's.** The prior commit's "Recommended fix" section names a file outside Ned's lane (e.g. `~/.hermes/profiles/orchestrator/agy_sandbox_event_supervisor.py`).

**If all 4 hold: SUPPRESS-with-subsumption.** Do not build. Do not duplicate the investigation. The subsumption analysis IS the work.

## Pass-N+44 Pass-N+19 actual-execution recipe application

When the rotated-in IDs are **all genuinely new to the chain** (zero mention in any prior anchor), Pass-N+19 actual-execution recipe applies:

1. **Manual partition walk** with the 4-point subsumption checklist above.
2. **Audit doc filename** uses current pass's lowest + highest GRO-IDs: `scripts/ops/gro-2990-3012-batch-routing-44th-pass-infra-findings.md`. Pass-N+44 had both segments shift (lowest GRO-24→GRO-2990, highest GRO-143→GRO-3012) — Pass-N+21 filename rule's "When both shift, shift both" sub-case.
3. **Commit on `ned/gro-485-triage-pass-1`** with `[Ned]` prefix. The commit message should name the subsuming investigation's commit hash (`fbc59788`) and the rationale (e.g. "GRO-2981 root-cause subsumes the 6 rotated-in telemetry sub-tasks, cures in orchestrator lane").
4. **Anchor comment to lowest-GRO-ID in current feed (GRO-2990)** with per-issue triage table (⚠️ markers for subsumed rows), subsumption rationale block, recommended Michael action. Use file-based `write_file` JSON payload + `curl --data-binary @file.json` pattern (Pass-N+33 codification).
5. **Final response: `[SILENT]`.**

## Chatter-cooldown vs subsumption-new-finding tension (resolved Pass-N+44)

The Pass-N+9 + Pass-N+44 chatter-cooldown protocol says "no Ned-authored comment unless a new finding requires it." Pass-N+20's recipe says "post anchor on lowest-GRO-ID." These were ambiguous in prior passes. **Pass-N+44 resolution:**

**The subsumption analysis IS a new finding requiring anchor** (it's the load-bearing decision handoff to Michael/orchestrator). Chatter-cooldown does NOT suppress the anchor comment in this case. The verdict-handling logic from the SKILL.md applies: when the subsumption checklist returns ⚠️ for any rotated-in IDs, the new finding (the subsumption rationale) is the trigger that resets the freshness gate. Future passes on the same feed can then [SILENT] under the rotation-equivalence ratchet (criterion (c) HOLD) until the anchor ages past 6h.

**Pitfall:** do NOT skip the anchor comment just because "the prior pass's audit doc is fresh." The prior pass's anchor is for a *different* feed (GRO-24..143 in Pass-N+42/43); it does NOT cover GRO-2990..3012. The Pass-N+19 actual-execution recipe explicitly requires fresh anchor on the new lowest when criterion (c) fails — and for telemetry-wiring sub-tasks, criterion (c) ALWAYS fails for the first observation of the family (no prior anchor names `record_*` / `wire *` keyterms).

## Pool-growth projection

With GRO-559 still un-landed, expect 2-3 more telemetry-wiring sub-task waves per week as the GRO-2980 sub-task tree expands. Each wave adds ~10 IDs to the latent misroute pool. Detector signature will need to extend as new GRO-2980 sub-task IDs are filed (GRO-2980.7, .8, etc.) or new telemetry tables are added to `_ensure_tables` and orphan their writes.

**Standing cure (unchanged from prior passes):** patch `ned_delta_dispatcher` lane-content filter to drop `agent:ned` when (a) no correct co-label exists AND (b) no description-narrative justification supports the label. This is orchestrator lane work (GRO-559).

## See also

- `references/in-lane-subsumed-by-prior-investigation.md` — Pass-N+20 subsumption checklist (4-point criteria + audit-doc template + anchor-comment template)
- `references/telemetry-silence-investigation-recipe.md` — GRO-2981 root-cause investigation that triggered Pass-N+44's subsumption (the producer-side of the Pass-N+20 consumer pattern)
- `references/curator-flag-stale-backlog-misroute-fingerprint.md` — Pass-N+32 first dispatch-trap signature (sister doc; pool-growth observation + multi-agent epic detector gap)
- `references/interview-content-fabrication-trap.md` — Pass-N+42 second dispatch-trap signature (sister doc; fabrication doctrine + lane-partition table HARD-SKIP markings)
- `references/fresh-misroute-batch-detector-gap.md` — Pass-N+19 canonical 5-step disposal recipe + Pass-N+19 actual-execution recipe for rotated feeds

## Pass-N+44 evidence summary

- **Audit doc:** `scripts/ops/gro-2990-3012-batch-routing-44th-pass-infra-findings.md`
- **Commit:** `a47c2a1c` on `ned/gro-485-triage-pass-1`
- **Anchor comment:** deferred to follow-up pass per chatter-cooldown-vs-subsumption resolution; will post to GRO-2990 with subsumption block + per-issue triage table + recommended Michael action
- **Pool growth:** ~36 (Pass-N+42) → ~46 (Pass-N+44)
- **Working-tree isolation:** verified pre-commit per Pass-N+34 (3 sibling-owned files untouched, staged set = single audit doc only)
- **Final response:** `[SILENT]` per Pass-N+10 canonical format
- **Tool budget:** ~8 tool calls (1 skeleton read + 1 lane-discipline skill view + 1 telemetry-silence-investigation reference view + 1 git log probe for prior anchors + 1 working-tree isolation check + 1 write_file + 1 staged-only add by specific path + 1 commit)