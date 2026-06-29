# Phase 3 / Sprint 1 — Goal & Critical Path

**Date:** 2026-06-28
**Sprint window:** ~3 days wall-clock (Gap 12: 1d, Gap 11: 2d, Gap 10: 1d — partially overlapping peer review)
**Test baseline:** 250/250 on `deploy-fresh`
**Sprint exit target:** 302/302 (Gap 12: +23, Gap 11: +16, Gap 10: +13)

---

## Sprint Goal

Close the "code-complete but operationally dead" loop on the Prismatic Engine's review pipeline by shipping three gaps in strict sequence: observability infrastructure first (Gap 12, 4 new telemetry tables + ops feed), then wiring the 6 inert channels that shipped as dead API in Phase 2 (Gap 11, impact rules + hook dispatch), then plugin auto-discovery (Gap 10, entry-points consumer + reference plugin). After Sprint 1, a pip-installed plugin's `register()` function fires real hooks, overrides real impact classifications, and emits structured telemetry events to SQLite — provable by querying `event_router.db`.

---

## Acceptance Criteria

1. **Observability foundation live:** 4 new `record_*` methods on `TelemetryCollector` write to 4 new `telemetry_*` tables; `get_dashboard_data()` returns `review`, `hooks`, and `plugins` blocks; `post_review_event_to_linear()` posts via Pattern B (`LinearTaskProvider.add_comment`) when `PRISMATIC_OPS_FEED_ISSUE_ID` is set.
2. **Inert channels wired:** All 6 channels listed as ❌ INERT in the Gap 11 spec (`register_impact_rule`, 5× `HOOK_*`) dispatch in production code paths; `register_impact_rule()` docstring no longer says "Currently inert."
3. **Plugin auto-discovery operational:** `discover_and_register_plugins(registry)` called at dispatcher startup; `prismatic-hello-world` reference plugin installs via `pip install -e` and contributes a check visible in the registry.
4. **Test count 302/302:** Gap 12 adds 23 tests, Gap 11 adds 16 + updates 1, Gap 10 adds 13. No existing tests broken. One updated test (`test_register_impact_rule_docstring_warns`) asserts the new positive contract.
5. **Per-PR peer review APPROVE:** Each gap's PR(s) pass Sonnet peer review before merge. Escalation to Opus only if Sonnet returns NEEDS_MAJOR_REWORK or flags an architectural concern.
6. **Meta-review APPROVE:** Post-sprint meta-review covers the combined 3-gap surface for cross-PR drift, dead channels, and Lesson 10 anti-patterns.
7. **OKF documentation shipped:** Implementation lessons, updated distribution checklist, and sprint retrospective committed in the same session as the final merge.

---

## Total Estimated Wall-Clock Time

| Phase | Duration | Notes |
|---|---|---|
| Gap 12 implementation (Sonnet subagent) | ~30 min | ~150 lines of code; 1 file + 2 new modules + 2 test files |
| Gap 12 peer review (Sonnet) | ~10 min | Automated |
| Gap 12 Fred integration (Fred pushes) | ~15 min | 2 PRs (Fred lane + Ned lane) |
| Gap 11 implementation (Sonnet subagent) | ~45 min | More complex; touches 6 files; breaking change on `PipelineOrchestrator` |
| Gap 11 peer review (Sonnet) | ~10 min | |
| Gap 11 Fred integration | ~15 min | 1 PR (Ned lane) |
| Gap 10 implementation (Sonnet subagent) | ~30 min | Discovery module + reference plugin + dispatcher hookup |
| Gap 10 peer review (Sonnet) | ~10 min | |
| Gap 10 Fred integration | ~15 min | 2 PRs (Ned + Fred lane) |
| Meta-review (Sonnet, Opus escalation if needed) | ~20 min | Combined 3-gap review |
| OKF docs + memory updates | ~15 min | |
| **Total** | **~3.5 hours** | Sequential; no parallelism between gaps |

---

## Critical Path

```
START
  │
  ▼
┌─────────────────────────────────────────────┐
│ Gap 12: Observability (Sonnet subagent)      │
│ • telemetry.py extension (+4 methods/tables) │
│ • ops_feed.py (Pattern B Linear)             │
│ • 23 tests                                   │
│ • Peer review → APPROVE                      │
│ • Fred merges 2 PRs                          │
│ EXIT: 273/273                                │
└─────────────┬───────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────┐
│ Gap 11: Wire Deferrals (Sonnet subagent)     │
│ • apply_impact_rules.py (pure function)      │
│ • PipelineOrchestrator(registry=...) change  │
│ • Hook dispatch at 5 insertion points        │
│ • Update docstrings (remove "inert" warning) │
│ • 16 tests + 1 updated                       │
│ • Peer review → APPROVE                      │
│ DEPENDS ON: Gap 12 telemetry params in       │
│   pipeline.py and pr_reviewer_impl.py        │
│ EXIT: 289/290 (expect 290, allow -1 for      │
│   updated docstring test)                    │
└─────────────┬───────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────┐
│ Gap 10: Plugin Auto-Discovery (Sonnet)       │
│ • plugin_discovery.py                        │
│ • prismatic-hello-world reference plugin     │
│ • dispatcher.py hookup                       │
│ • 13 tests                                   │
│ • Peer review → APPROVE                      │
│ DEPENDS ON: Gap 11 (impact_rule must be      │
│   wired before docs advertise it)            │
│ EXIT: 302/302                                │
└─────────────┬───────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────┐
│ Meta-Review (Sonnet; Opus if escalated)      │
│ • Cross-PR drift check                       │
│ • Lesson 10 anti-pattern scan                │
│ • Dead channel audit                         │
│ DEPENDS ON: All 3 gaps merged                │
│ EXIT: APPROVE or NEEDS_FIXES + action items  │
└─────────────┬───────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────┐
│ OKF Docs + Memory + Skills                   │
│ • gap12-implementation-lessons.md            │
│ • gap11-implementation-lessons.md            │
│ • gap10-implementation-lessons.md            │
│ • sprint1-retrospective.md                   │
│ • Memory entries for carry-forward items     │
└─────────────────────────────────────────────┘
              │
              ▼
            DONE
```

### Parallelism Opportunities

None between gaps — strict serial dependency. However, within each gap:
- Sonnet implementation and test writing can be a single subagent call
- Peer review runs immediately after implementation (no human gate)
- Fred integration (branch creation, push, merge) is a 5-minute operation

### Critical Path Bottleneck

Gap 11 is the bottleneck: 2-day estimated effort, most complex change (touching 6 files with a breaking change to `PipelineOrchestrator.__init__`), and the most likely to need peer-review rework. If Gap 11 slips, Gap 10 cannot start.

---

*Filed 2026-06-28 by Opus (claude-opus-4-6-thinking). Phase 3 / Sprint 1 execution plan.*
