# In-lane-but-subsumed-by-prior-investigation pattern (Pass-N+20, 2026-06-29 ~22:00Z)

**Codified from Pass-N+20.** This is a refinement of the rotation-equivalence disposal recipe in `references/fresh-misroute-batch-detector-gap.md` §"Pass-N+19 actual-execution recipe." It handles the case where the rotated-in IDs in a scanner feed are **genuinely in Ned's lane** (per their `agent:ned` + `prismatic-engine` labels), but their cures are in another lane because **a prior Ned investigation already root-caused the whole family** they belong to.

## When this pattern applies

After the manual partition walk from the 5-step disposal recipe returns **a mix of out-of-lane IDs and in-lane-but-subsumed IDs**:

- **Out-of-lane IDs:** wrong agent label, cross-profile write territory, `[MANUAL]` human-required work, Dispatcher "routed to <other lane>" ×3+. Same as prior passes.
- **In-lane-but-subsumed IDs:** labeled `agent:ned` + topic-relevant (`prismatic-engine`, `observability`, etc.), title prefixed `[Ned]`, BUT a **prior Ned investigation commit** on `ned/gro-485-triage-pass-1` (or any Ned branch) already root-caused the underlying pathology, AND the cure path is in another agent's lane (e.g. orchestrator).

This pattern is **NOT** the same as "in-lane-and-build-it." Building per-issue investigations for subsumed IDs would:
1. Duplicate the prior investigation's findings (the root cause is already documented).
2. Consume ~5-7 tool calls per issue without producing actionable in-lane code (Ned cannot write to another lane's files).
3. Spam Michael with N separate "cure is in <other lane>" handoffs when one already exists.

## Subsumption criteria (4-point checklist)

For each rotated-in ID that the partition walk flags as in-lane, apply this checklist:

1. **Prior root-cause commit exists.** A commit on `ned/<some-branch>` (typically `ned/gro-485-triage-pass-1`) addresses the **family** of issues this ID belongs to. The commit message or audit doc names the architectural root cause, not just the single issue's symptom.
2. **Prior commit is recent and In Review or Done.** Typically within 24h of the current pass. The cure is pending Michael's review, not a stale draft.
3. **This ID's acceptance criteria trace to the prior root cause.** The ID's description explicitly names a table / metric / behavior that the prior investigation already analyzed. Examples from Pass-N+20:
   - GRO-2978 ("assert >=1 row with non-null end_time in telemetry_agent_runs this week") — the 635-row set with all end_time=NULL is GRO-2981's core dataset.
   - GRO-2979 ("178 dispatches, 0 completions") — the 27 GRO-2051 retry-storm rows on 2026-06-25 are in the 635-row set.
   - GRO-2980 ("telemetry_token_metrics empty") — GRO-2981's commit message explicitly carved out "GRO-2980 territory" as related-but-distinct downstream of the same orchestrator-bypass pathology.
4. **Cure is in another lane, not Ned's.** The prior commit's "Recommended fix" section names a file outside Ned's lane (e.g. `~/.hermes/profiles/orchestrator/agy_sandbox_event_supervisor.py`). Ned cannot land the fix even with full tool budget; another agent must.

**If all 4 hold: SUPPRESS-with-subsumption.** Do not build. Do not duplicate the investigation. The subsumption analysis IS the work — it documents that the in-lane IDs are correctly recognized but correctly deferred to the prior investigation's cure.

## Audit-doc subsumption table (Pass-N+20 template)

The audit doc for a subsumption pass should include a **two-tier triage table** that distinguishes out-of-lane IDs from in-lane-but-subsumed IDs. Template:

```markdown
| # | ID | Title | Correct lane | Ned-lane? |
|---|----|-------|--------------|-----------|
| 1 | GRO-X | ... | `agent:fred` (reason) | ❌ |
| 2 | GRO-Y | ... | `agent:orchestrator` (cross-profile) | ❌ |
| 3 | **GRO-Z** | **[Ned] Some investigation** | **`agent:ned`** BUT **SUBSUMED by GRO-AAA** (one-line summary of how this ID's acceptance criteria trace to GRO-AAA's root cause) | ⚠️ in-lane-but-subsumed |
```

The ⚠️ marker is load-bearing — it tells a future reconstructor reading the audit doc that the ID is in-lane by label but not by action, with the subsumption reason inline. Reviewers can challenge the subsumption by walking back to the cited prior investigation.

## Anchor-comment subsumption block (Pass-N+20 template)

The anchor comment must include the subsumption rationale inline so Michael sees it without opening the audit doc. Template:

```markdown
- `GRO-Z` — [Ned] Some investigation → **in-lane BUT SUBSUMED by GRO-AAA** (<one-sentence pathology trace>) — *rotated IN this pass*

**Subsumption rationale (load-bearing decision):** GRO-AAA (<commit hash>, <state>, <age>) already root-caused the entire <family>. Building per-issue investigations for GRO-Z would duplicate GRO-AAA's findings AND consume ~N tool calls without producing actionable in-lane code (Ned cannot fix <other-lane> files). GRO-Z's cure is in <other-lane>.

**Recommended Michael action:** review GRO-AAA (currently <state>), approve the <other-lane> fix (<specific file + change>). Once that lands, GRO-Z closes automatically.
```

The recommended-action block converts the SUPPRESS from "Ned punted" to "Ned actively handed off to the right lane with the right prescription." Without this block, a future reconstructor reading the anchor comment sees a SUPPRESS with no actionable next step — which is the r91 anti-pattern in disguise.

## Disposal recipe (Pass-N+20 validated)

1. **Manual partition walk.** Apply the 4-point subsumption checklist above to each rotated-in ID that the partition rules flag as in-lane.
2. **Audit doc** at `prismatic-engine/scripts/ops/gro-<lowest-current-pass>-<highest-rotated-in>-batch-routing-Nth-pass-infra-findings.md`. Include the two-tier triage table with ⚠️ markers for subsumed IDs.
3. **Commit on `ned/gro-485-triage-pass-1`** with `[Ned]` prefix. Commit message should name the subsuming investigation's commit hash and the rationale (e.g. "GRO-2981 root-cause subsumes the 3 rotated-in telemetry investigations, cures in orchestrator lane").
4. **Anchor comment** to the lowest GRO-ID in the current pass's feed (NOT the prior pass's). Include the per-issue triage table with the ⚠️ subsumption markers, the subsumption rationale block, and the recommended Michael action.
5. **Final response: `[SILENT]`.** Same as the original 5-step recipe.

## Relationship to existing references

- **Extends** `references/fresh-misroute-batch-detector-gap.md` §"Pass-N+19 actual-execution recipe" — same disposal shape, additional subsumption layer for rotated-in in-lane IDs.
- **Complements** `references/telemetry-silence-investigation-recipe.md` — the prior investigation that triggered subsumption in Pass-N+20. The subsumption pattern is the *consumer* of investigation recipes; investigation recipes are the *producer* of subsumption-eligible state.
- **Codifies** the recurring pattern where one Ned investigation root-causes a family of N issues, and subsequent cron passes get rotated-in family members that are all subsumed by that investigation.

## Pass-log entry (add to `references/pass-log-2026-06.md`)

```
- **Pass-N+20 (2026-06-29 ~22:00Z)** — Detector verdict: `FULL_REPORT`
  (rotated feed, no registered signature). Manual partition walk + 4-point
  subsumption checklist returned 0/10 in Ned's lane + 3/10 in-lane-but-
  subsumed-by-GRO-2981. Disposition: SUPPRESS-with-subsumption. Audit doc:
  `scripts/ops/gro-1662-2978-batch-routing-20th-pass-infra-findings.md`.
  Commit `ae007b28` on `ned/gro-485-triage-pass-1`. Anchor comment ID
  `566903ae-2f32-40e7-890b-7f88029edb4d` on GRO-1662 at 22:03:00Z (still
  lowest-GRO-ID; Pass-N+19 anchor `a6ec4bf2` is on the same issue, ~17 min
  old). Probe-skip per Pass-12 protocol. Rotation delta vs Pass-N+19:
  GRO-2978/2979/2980 swapped in for GRO-502/593/594. See
  `references/in-lane-subsumed-by-prior-investigation.md`. Final
  response: `[SILENT]`.
```

## See also

- `references/fresh-misroute-batch-detector-gap.md` — parent disposal recipe, rotation-equivalence ratchet, latent misroute pool.
- `references/telemetry-silence-investigation-recipe.md` — the producer-side recipe that creates subsumption-eligible state in Pass-N+20's case.
- `references/recurring-misroute-batch-playbook.md` — sub-case A (recurring) and sub-case B (first-sighting zero-comments).
- `scripts/suppress_class_detect.py` — detector that flags fresh-misroute batches; does NOT detect subsumption (manual walk required).