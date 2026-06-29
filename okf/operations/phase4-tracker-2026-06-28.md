# Phase 4 — Plan (Sprint 2)

**Date:** 2026-06-28
**Initiative:** Phase 4 — Operational Reality (cross-platform, self-improving)
**Sprint:** 2 of 3 (planned, not started)

---

## Sprint 2 Scope

### Gaps (planned)

| Gap | Status | Description | Tests | Owner |
|---|---|---|---|---|
| **Gap 12-full** — Tracing + dashboards | NOT STARTED | Rebuild OpenTelemetry-compatible tracer (was collapsed into single telemetry.py); add Grafana export; add `_drain_failure_counter`; consolidate `check_alerts` auto-invocation | ~30 | Fred |
| **Gap 13** — Windows + macOS compat | NOT STARTED | `pathlib.Path` refactor + `/tmp/` defaults removed; CI matrix includes macOS + Windows; 6 modules touched | ~12 | Fred |
| **Gap 14** — First real third-party plugin | NOT STARTED | `prismatic-secret-scanner-extras` package: 30+ additional secret patterns + "no print statements" check + IMPACT_TRIVIAL boost rule | ~25 | Ned |

### Sprint 2 dependency on Sprint 1

- Gap 12-full requires Sprint 1's Gap 12 telemetry tables to be stable
- Gap 14 requires Sprint 1's Gap 10 entry-points + Gap 11 hook dispatch to be live

### Sprint 2 timeline (estimated)

| Event | Wall-clock |
|---|---|
| Reconnaissance (cross-platform test environment) | ~30 min |
| Gap 12-full Sonnet implementation | ~60 min (tracer is non-trivial) |
| Gap 13 Sonnet implementation | ~90 min (refactor 6 modules + CI matrix) |
| Gap 14 Sonnet implementation (new repo) | ~120 min (new package + 25 tests) |
| Per-PR peer review (3 PRs) | ~30 min |
| Meta-review across Sprint 2 | ~15 min |
| **Total** | **~6 hours** |

### Sprint 2 acceptance criteria

- [ ] OpenTelemetry-compatible tracer exported from `prismatic.tracer` (or equivalent)
- [ ] Grafana dashboard JSON committed to OKF
- [ ] `prismatic.dispatcher` runs on Linux + macOS + Windows without modification
- [ ] CI matrix runs on all 3 OSes for `pytest prismatic/`
- [ ] `prismatic-secret-scanner-extras` package exists as a separate repo, uses `prismatic.plugins` entry-points, ships 30+ patterns
- [ ] Pattern count ceiling guard (10k-pattern DoS) — meta-review P1 carry-forward
- [ ] `_drain` failures now counted (no more silent swallowing)
- [ ] Cumulative tests: 310 + ~67 = ~377 across Sprint 2

### Sprint 2 risks (carry-forward)

- Gap 13 cross-platform compat: `os.path.join`, `/tmp/` defaults in 6 modules could break on Windows path separators
- Gap 14 first real plugin: API stability unproven until exercised
- Gap 12-full tracing: requires rebuilding what was collapsed; might surface historical bugs in the deleted-but-cached telemetry package

### Sprint 2 deferred to Sprint 3

- Gap 15 (self-improvement feedback loop) — needs production data from Sprint 1+2 to tune thresholds
- Plugin auto-update — pip does this
- Plugin hot-reload — restart required
- Plugin isolation / sandboxing — security track

---

*Planned 2026-06-28 by Fred (orchestrator). Subject to revision after Sprint 1 meta-review.*
