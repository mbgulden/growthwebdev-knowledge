# Linear Issue Setup — Phase 3 / Sprint 1

**Date:** 2026-06-28
**Sprint:** Phase 3 / Sprint 1 (Gaps 12, 11, 10)
**Owner:** Fred (orchestrator)
**Source:** Opus plan

---

## Linear issue shape per gap

### Issue GRO-XXXX — Gap 12: Observability slice (extends TelemetryCollector)

**Title:** `[Phase 3 / Sprint 1] Gap 12 — Observability slice (extends prismatic.telemetry)`

**Labels:** `agent:fred`, `phase-3`, `sprint-1`, `gap-12`, `lane:fred`, `pr-required`, `peer-review-required`

**Priority:** High

**Estimate:** 1 day (Sonnet subagent ~30 min + integration + peer review)

**Body:**

```markdown
## Goal
Close the review-pipeline telemetry black hole by extending
`prismatic/telemetry.py` with 4 new `record_*` methods + 4 new
SQLite tables. Plus `prismatic/observability/ops_feed.py` for Linear
comments via `LinearTaskProvider` (Pattern B).

## Scope (in PR)
- prismatic/telemetry.py — 4 record_* methods, 4 tables, 4 _drain branches, 4 cleanup entries, get_dashboard_data extension
- prismatic/observability/__init__.py (NEW)
- prismatic/observability/ops_feed.py (NEW)
- prismatic/test_telemetry_extension.py (NEW)
- prismatic/observability/test_ops_feed.py (NEW)
- okf/operations/gap12-implementation-lessons.md (NEW)

## Out of scope (deferred to Gap 11 + Gap 12-full)
- prismatic/review/pr_reviewer_impl.py — Ned lane, gets telemetry param in Gap 11
- prismatic/review/pipeline.py — Ned lane, gets telemetry param in Gap 11
- prismatic/quality/gates.py — Ned lane, gets telemetry param in Gap 11
- pyproject.toml — Fred lane, separate PR if needed
- prismatic/dispatcher.py — Gap 10 calls discover_and_register_plugins from there

## Acceptance criteria
- [ ] 4 record_* methods on TelemetryCollector
- [ ] 4 tables in _ensure_tables with telemetry_ prefix
- [ ] 4 INSERT branches in _drain
- [ ] 4 entries in cleanup_expired retention map
- [ ] get_dashboard_data extended with review/hooks/plugins blocks
- [ ] prismatic.observability.ops_feed.post_review_event_to_linear() exported
- [ ] LinearTaskProvider.add_comment() used (Pattern B), NOT curl subprocess
- [ ] 23 new tests pass
- [ ] Baseline 250 → 273 total (test count arithmetic verified)
- [ ] ruff check + ruff format clean
- [ ] Sonnet peer review APPROVE
- [ ] Branch pushed to origin (pyproject.toml stays out per lane split)

## Spec
okf/operations/gap12-observability-slice-spec.md

## Recon
okf/operations/phase3-reconnaissance-2026-06-28.md (Recon 1: telemetry API map)

## Risk register
okf/operations/phase3-sprint1-plan/06-risk-register.md (R1, R4, R5, R8)
```

**Cross-gap dependencies:** Blocks Gap 11 (Gap 11 wires telemetry into the review pipeline; needs Gap 12's record_* methods).

---

### Issue GRO-XXXX — Gap 11: Wire the deferrals (impact rules + hook dispatch)

**Title:** `[Phase 3 / Sprint 1] Gap 11 — Wire the deferrals (impact rules + hook dispatch)`

**Labels:** `agent:fred`, `phase-3`, `sprint-1`, `gap-11`, `lane:ned`, `pr-required`, `peer-review-required`, `breaking-change`

**Priority:** High (highest risk gap — breaking change + Lesson 10 anti-pattern risk)

**Estimate:** 2 days

**Body:**

```markdown
## Goal
Close 6 inert channels (HOOK_* constants + register_impact_rule)
that shipped in PR #41 / Phase 2. After this gap, plugin authors
register impact rules + hook callbacks that take effect in production
reviews.

## Scope (in PR)
- prismatic/review/pipeline.py — PipelineOrchestrator.__init__ accepts registry=
- prismatic/review/apply_impact_rules.py (NEW)
- prismatic/review/pr_reviewer_impl.py — RealPRReviewer fires HOOK_BEFORE_SECRET_SCAN + HOOK_BEFORE_QUALITY_CHECKS
- prismatic/quality/gates.py — trigger_ned_review fires HOOK_BEFORE_NED_REVIEW
- prismatic/review/registry.py — register_impact_rule docstring updated (remove "Currently inert")
- prismatic/review/hooks.py — each HOOK_* docstring updated (remove TODO)
- prismatic/review/test_wire_deferrals.py (NEW)
- prismatic/review/test_registry.py — UPDATE test_register_impact_rule_docstring_warns

## Acceptance criteria
- [ ] apply_impact_rules() exported from prismatic.review
- [ ] PipelineOrchestrator(registry=...) accepts registry; old signature still works
- [ ] Each HOOK_* constant fires when its trigger condition is met
- [ ] Hook failure isolated (warning logged, dispatch continues)
- [ ] register_impact_rule() docstring no longer says "Currently inert"
- [ ] test_register_impact_rule_docstring_warns updated to assert positive contract
- [ ] Test #14 asserts on decision.impact from process(), NOT classify_impact() (Lesson 10 fix)
- [ ] Tests #11/#12 use mutation-through assertions, NOT lambda *a: None (Lesson 10 fix)
- [ ] 16 new tests pass + 1 updated test passes
- [ ] Baseline 273 (post-Gap-12) → 290 total
- [ ] Sonnet peer review APPROVE

## Spec
okf/operations/gap11-wire-deferrals-spec.md

## Risk register
okf/operations/phase3-sprint1-plan/06-risk-register.md (R2, R6, R7, R11)
```

**Cross-gap dependencies:** Depends on Gap 12 (uses telemetry.record_pipeline_action). Blocks Gap 10 (Gap 10's discover_and_register_plugins surfaces plugins that register the now-live hooks).

---

### Issue GRO-XXXX — Gap 10: Plugin auto-discovery

**Title:** `[Phase 3 / Sprint 1] Gap 10 — Plugin auto-discovery (entry_points group)`

**Labels:** `agent:fred`, `phase-3`, `sprint-1`, `gap-10`, `lane:ned`, `lane:fred`, `pr-required`, `peer-review-required`, `distribution-impact`

**Priority:** High (turns "shippable" into "installable")

**Estimate:** 1 day

**Body:**

```markdown
## Goal
Turn Prismatic from "shippable with manual plugin wiring" into
"installable with zero-config plugin activation." When a third-party
plugin is installed via pip, dispatcher auto-discovers it on next
startup and uses its contributions.

## Scope (in PR)
- prismatic/review/plugin_discovery.py (NEW)
- prismatic/review/test_plugin_discovery.py (NEW)
- prismatic/review/__init__.py — export discover_and_register_plugins
- prismatic/dispatcher.py — call discover_and_register_plugins(registry) at startup
- plugins/prismatic-hello-world/ (NEW — reference plugin: pyproject.toml + src/ + README)
- okf/operations/gap10-implementation-lessons.md (NEW)
- okf/operations/prismatic-distribution-checklist.md — full overhaul

## Acceptance criteria
- [ ] discover_and_register_plugins() exported from prismatic.review
- [ ] Empty entry_points → empty list, no crash
- [ ] Mock-installed plugin → its register(registry) called exactly once
- [ ] Failure (load timeout, register exception) logged + skipped, not raised
- [ ] Returned list sorted alphabetically
- [ ] prismatic.dispatcher.main() calls discovery at startup + logs list
- [ ] prismatic-hello-world ships in plugins/ directory
- [ ] Test #9 verifies real installed plugin in real registry (Lesson 10 fix)
- [ ] 13 new tests pass
- [ ] Baseline 290 (post-Gap-11) → 303 total
- [ ] Sonnet peer review APPROVE

## Spec
okf/operations/gap10-plugin-auto-discovery-spec.md

## Risk register
okf/operations/phase3-sprint1-plan/06-risk-register.md (R3, R11)
```

**Cross-gap dependencies:** Depends on Gap 11 (surfaces hooks that plugins register).

---

## Issue assignment

- **Gap 12:** `agent:fred` (orchestrator owns the integration across all 3 gaps; Sonnet subagent does the implementation)
- **Gap 11:** `agent:fred` (same — orchestrator owns)
- **Gap 10:** `agent:fred` (same)
- **Subagent implementations:** Fired by Fred, not assigned to AGY directly
- **Peer review per PR:** Sonnet subagent (via agy --model claude-sonnet-4-6)
- **Meta-review across Sprint 1:** Sonnet subagent (escalate to Opus only if Sonnet tried and missed)

## Sprint 1 milestones (Linear projects)

Use Linear's project feature (or a tag) to group the 3 issues:
- Project: `Phase 3 / Sprint 1 — Factory Observability + Plugin Extensibility`
- Milestone: `Sprint 1 complete (target: ~4.5 hours wall-clock)`

---

*Filed 2026-06-28 by Fred (orchestrator). Continuation of Opus's interrupted plan output.*
