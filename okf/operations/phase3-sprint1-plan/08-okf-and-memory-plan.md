# OKF Documentation + Memory Plan — Phase 3 / Sprint 1

**Date:** 2026-06-28
**Sprint:** Phase 3 / Sprint 1
**Owner:** Fred (orchestrator)
**Source:** Opus plan + standard protocol for every major cycle

---

## OKF docs to write per gap

### After Gap 12 lands
- `okf/operations/gap12-implementation-lessons.md` — what worked, what didn't, what to carry forward. ~150-200 lines.
- Update `okf/operations/prismatic-distribution-checklist.md` — add `PRISMATIC_OPS_FEED_ISSUE_ID` env var + new telemetry tables in the "what observability is available" section.

### After Gap 11 lands
- `okf/operations/gap11-implementation-lessons.md` — hook dispatch lessons, `apply_impact_rules` lessons, integration test lessons. ~150-200 lines.
- Update `okf/operations/gap11-wire-deferrals-spec.md` — mark "Status: SHIPPED" at the top.

### After Gap 10 lands
- `okf/operations/gap10-implementation-lessons.md` — entry-points discovery lessons, reference plugin packaging lessons, distribution checklist update lessons. ~150-200 lines.
- Update `okf/operations/prismatic-distribution-checklist.md` — full overhaul now that the entry-points system is real. Add: `register(registry)` signature contract, load-order spec, error-isolation contract, reference plugin author quickstart, Windows/macOS caveats for plugin packaging.

### After meta-review
- `okf/operations/phase3-sprint1-meta-review-<date>.md` — meta-review verdict + 8-category evaluation.
- `okf/operations/phase3-sprint1-final-status.md` — aggregate ship status doc, mirroring Phase 2's structure.
- `okf/operations/phase3-sprint1-master-plan/` directory cleanup — leave the Opus plan files as historical record.

## Commit cadence

Per gap + per meta-review. 5 OKF commits total in Sprint 1:
1. After Gap 12: `OKF: Gap 12 lessons + distribution checklist update`
2. After Gap 11: `OKF: Gap 11 lessons + spec status`
3. After Gap 10: `OKF: Gap 10 lessons + distribution checklist overhaul`
4. After meta-review: `OKF: Phase 3 Sprint 1 meta-review + final status`
5. End of sprint: `OKF: Sprint 1 retrospective + Phase 3 north star update`

## Memory entries to add

### After Gap 12 lands
```
GAP 12 SHIPPED (Jun 28 2026): extends prismatic/telemetry.py with 4 record_* methods + 4 tables + LinearTaskProvider ops_feed. 23 new tests, total 273/273. Spec-driven with recon + Opus plan + Sonnet implementation. Key lesson: existing infrastructure was the right extension point — don't reinvent observability when TelemetryCollector already does it.
```

### After Gap 11 lands
```
GAP 11 SHIPPED (Jun 28 2026): 6 inert channels (HOOK_* + impact_rules) now live. PipelineOrchestrator gains registry= kwarg. 16 new tests + 1 updated docstring test, total 290/290. Lesson 10 fix: tests assert on process() decision not classify_impact() raw output; mutation-through assertions not lambda *a: None flags.
```

### After Gap 10 lands
```
GAP 10 SHIPPED (Jun 28 2026): plugin auto-discovery via entry_points(group="prismatic.plugins"). 13 new tests + prismatic-hello-world reference plugin. Total 303/303. Lesson: third-party plugins are real now — distribution checklist overhaul required.
```

### After meta-review
```
PHASE 3 SPRINT 1 SHIPPED + META-REVIEWED (Jun 28 2026): 3 gaps shipped, ~52 new tests, factory observability + plugin extensibility complete. Opus plan + Sonnet implementation + Sonnet meta-review per opus-plans-sonnet-implements routing rule. Sprint 2 next.
```

## New skills to create or update

### Existing skills to update

- `~/.hermes/profiles/orchestrator/skills/meta-review-architecture/SKILL.md` — Sprint 1 outcome reference added
- `~/.hermes/profiles/orchestrator/skills/second-opinion-on-design.md` — Recon Step pattern (already updated; add Sprint 1 outcome reference)
- `~/.hermes/profiles/orchestrator/skills/opus-plans-sonnet-implements.md` (NEW from Sprint 1) — add Sprint 1 outcome reference

### New skills to consider

- `prismatic-extension-authoring.md` — if Sprint 3 ships the first real third-party plugin (Gap 14), capture the author experience as a skill
- `linear-ops-feed-pattern.md` — if Gap 12 ops_feed is used in production, capture the Linear-as-event-bus pattern
- `prismatic-plugin-debugging.md` — if Gap 10 + Gap 14 surface debugging patterns (how to verify a plugin was loaded, why a hook didn't fire, etc.)

Defer new skills to Sprint 2/3 unless Sprint 1 produces a clear pattern worth capturing immediately.

## When to write each doc

| Doc | When |
|---|---|
| Gap N implementation lessons | Same day as Gap N PR merges |
| Spec status update | Same day as Gap N PR merges |
| Distribution checklist update | Same day as Gap N PR merges (Gap 10 only) |
| Meta-review artifact | Same day as meta-review verdict |
| Sprint final status | Day after meta-review completes |
| Memory entries | End of sprint, after all docs committed |
| Skill updates | End of sprint, before next sprint planning |

## OKF directory structure after Sprint 1

```
okf/operations/
├── phase2-meta-review-2026-06-28.md
├── phase2-final-status.md
├── phase2-quality-gates-implementation.md
├── phase2-lessons-learned-2026-06-28.md
├── phase3-reconnaissance-2026-06-28.md
├── phase3-second-opinions-2026-06-28.md
├── phase3-sprint1-opus-plan-2026-06-28.md
├── phase3-sprint1-plan/                    # NEW (Opus's 10-file plan)
│   ├── 01-sprint-goal.md
│   ├── 02-gap12-execution.md
│   ├── ...
│   └── 10-honest-caveats.md
├── phase3-sprint1-meta-review-2026-06-28.md  # NEW (meta-review verdict)
├── phase3-sprint1-final-status.md           # NEW
├── gap10-plugin-auto-discovery-spec.md
├── gap10-implementation-lessons.md          # NEW
├── gap11-wire-deferrals-spec.md
├── gap11-implementation-lessons.md          # NEW
├── gap12-observability-slice-spec.md
├── gap12-implementation-lessons.md          # NEW
├── prismatic-distribution-checklist.md
└── ... (existing docs)
```

---

*Filed 2026-06-28 by Fred (orchestrator). Continuation of Opus's interrupted plan output.*
