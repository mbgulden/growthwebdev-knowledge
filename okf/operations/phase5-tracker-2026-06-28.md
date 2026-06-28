# Phase 5 — Plan (Sprint 3)

**Date:** 2026-06-28
**Initiative:** Phase 5 — Self-Improvement (the factory learns)
**Sprint:** 3 of 3 (planned, not started)

---

## Sprint 3 Scope

### Gaps (planned)

| Gap | Status | Description | Tests | Owner |
|---|---|---|---|---|
| **Gap 15** — Production feedback loop | NOT STARTED | Telemetry data feeds back into pattern prioritization + threshold tuning; weekly review of `telemetry_review_completed` shows false-positive patterns; auto-tune `classify_impact()` thresholds based on real distribution | ~18 | Fred + Ned |
| **Gap 16** — Plugin marketplace | NOT STARTED | Public registry of plugins; PR-discovery workflow; reputation system (post-PR-merger reviews rated) | ~25 | Ned + Fred |

### Sprint 3 dependency on Sprint 1 + 2

- Gap 15 requires Sprint 2's Gap 12-full observability + Sprint 1's review telemetry tables
- Gap 16 requires Sprint 1's Gap 10 plugin auto-discovery + Sprint 2's Gap 14 real plugin

### Sprint 3 deferred

- Plugin versioning SemVer policy enforcement (was deferred from Gap 10)
- Plugin hot-reload — restart required for now
- Plugin isolation / sandboxing — security track
- Distributed factory (multi-node, not single-machine)

---

## 5 Horizons Status (per north-star doc)

Per `okf/vision/prismatic-north-star.md`:

### Horizon 1: Coding (in progress)
- Phase 1: ✅ Quality Gates shipped (250+ tests, 8 PRs)
- Phase 2: ✅ Quality Gates Phase 2 shipped (Gaps 4, 5, 7, 8, 9)
- Phase 3: 🔄 **In progress** — Gaps 10, 11, 12 (Sprint 1)
- Phase 4: 📋 Planned — Gaps 12-full, 13, 14 (Sprint 2)
- Phase 5: 📋 Planned — Gaps 15, 16 (Sprint 3)

### Horizon 2: Business
- Active Oahu Tours: ✅ Production (130 pages with schema, 83 Japanese pages)
- HD Engine: ✅ Phase 1 shipped (4-channel bodygraph)
- AI Consulting: ⏸ Paused (high-ticket but episodic)

### Horizon 3: Creative
- Asset Forge 3D: ⏸ Paused
- Interview content pipeline: ✅ Active (6 scripts waiting on Michael for recording)

### Horizon 4: Knowledge
- OKF: ✅ Active (16+ ops docs, 10 docs added today for Phase 3)
- Memory: ✅ Active (4 entries, Opus chunking lesson + Phase 2+3 history)

### Horizon 5: Dream
- Prismatic as portable-core engine that ships to anyone: 🚧 In progress
- North star: "Help others build their dreams" — Open Source phase still years away

---

## Sprint 3 timeline (estimated)

| Event | Wall-clock |
|---|---|
| Reconnaissance + spec authoring | ~60 min |
| Gap 15 Sonnet implementation (production data analysis) | ~90 min |
| Gap 16 Sonnet implementation (marketplace prototype) | ~120 min |
| Per-PR peer review (2 PRs) | ~20 min |
| Meta-review across Sprint 3 + Phase 3/4/5 retrospective | ~30 min |
| **Total** | **~5 hours** |

### Sprint 3 acceptance criteria

- [ ] `prismatic.feedback` module exported; weekly review report auto-generated
- [ ] `classify_impact()` thresholds auto-tune based on real production distribution
- [ ] Plugin marketplace prototype (CLI to browse + install plugins)
- [ ] Phase 3-5 retrospective doc + memory entries
- [ ] Cumulative tests across all 3 sprints: 310 + 67 + 43 = ~420

### Sprint 3 risks

- Gap 15 feedback loop could cause cascading changes to thresholds that break reviews in unexpected ways (mitigation: dry-run mode + manual approval)
- Gap 16 marketplace is a new surface area; security + trust model need careful design

---

## Beyond Sprint 3 (next quarter)

### Open horizons
- Plugin sandboxing (security track)
- Multi-node distributed factory
- Plugin marketplace public launch
- Phase 6: customer-facing dashboards

### Things we don't know yet
- Real production load at scale (the factory has never been hit with >1000 reviews/hour)
- Plugin ecosystem growth (will third parties actually ship?)
- AI cost trajectory (Claude API prices may drop, may rise; budget model assumes current prices)

---

*Planned 2026-06-28 by Fred (orchestrator). Subject to revision after Sprint 1+2 meta-reviews.*
