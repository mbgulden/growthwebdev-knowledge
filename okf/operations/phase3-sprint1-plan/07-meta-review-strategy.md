# Meta-Review Strategy — Phase 3 / Sprint 1

**Date:** 2026-06-28
**Sprint:** Phase 3 / Sprint 1 (Gaps 12, 11, 10)
**Owner:** Fred (orchestrator)
**Source:** Opus plan + meta-review-architecture skill

---

## When to run meta-review

**After all 3 gaps merge to deploy-fresh.** Not after each gap — Sprint 1 is a tightly-coupled initiative (Gap 12 lays telemetry foundation, Gap 11 wires hooks that emit telemetry, Gap 10 enables plugins that register hooks). Running meta-review between gaps would miss the cross-PR drift that emerges from the coupling.

## Model routing

**Sonnet by default** (per the meta-review-architecture skill). Escalate to **Opus** if:
1. Sonnet tried and missed a multi-file bug in per-PR peer review
2. The meta-review spans >5 PRs with cross-cutting architectural risk (Sprint 1 = 3-4 PRs, so probably stays at Sonnet)
3. A reviewer flags security-sensitive behavior (secrets, billing, plugin isolation)

## Specific things the meta-review should look for

Per the meta-review-architecture skill, the meta-review prompt must enumerate these categories. Subagent will grade each on "PASS / CONCERN / FAIL" and provide evidence.

### Category 1: Cross-PR scope drift

- **Question:** Did any gap ship changes outside its spec?
- **Method:** Compare PR diffs to the 3 approved specs; flag anything that wasn't promised.
- **Example:** Did Gap 11 also add a `shutdown()` method to TelemetryCollector that wasn't in the Gap 12 spec?

### Category 2: API surface consistency

- **Question:** Are new public symbols importable from `prismatic.review` / `prismatic` / `prismatic.observability`?
- **Method:** Import each new symbol in a Python REPL; verify no ImportError.
- **Example:** `from prismatic.review import apply_impact_rules` — must work (it's a Gap 11 export)

### Category 3: Dead channel check (Lesson 10 anti-pattern)

- **Question:** Did any new code register a callback that's never invoked?
- **Method:** For every new `register_*` method, find at least one production code path that calls it. Flag if any callback list is populated but never consumed.
- **Example:** Are `register_impact_rule()` registrations actually changing `PipelineOrchestrator.process()` decisions?

### Category 4: Test coverage integrity

- **Question:** Do the new tests exercise real production code paths, or do they test internal helpers / mock the system under test?
- **Method:** For each new test, read the test body. If it mocks the function being tested or iterates manually, flag.
- **Example:** Test `test_full_review_through_real_reviewer_pipeline_orchestrator_with_registry` (Gap 11 test #16) must actually run `RealPRReviewer.review_pr()` and `PipelineOrchestrator.process()` end-to-end, not mock them.

### Category 5: Spec assumption verification

- **Question:** Did the assumptions in the specs hold up in implementation?
- **Method:** Each spec lists assumptions; check the implementation against each.
- **Example:** Gap 12 assumes `LinearTaskProvider.add_comment()` exists with the documented signature. If the actual signature is different, flag.

### Category 6: Performance regression

- **Question:** Did any gap introduce a performance regression?
- **Method:** Run `pytest --durations=20` on Sprint 1 deploy-fresh vs Phase 2 baseline; flag any new slow tests.
- **Example:** Gap 11's `apply_impact_rules` inside the lock — is the per-review cost acceptable?

### Category 7: Documentation accuracy

- **Question:** Are the docs (distribution checklist, OKF specs) still accurate after the implementation?
- **Method:** Compare OKF docs to actual implementation; flag any contradiction.
- **Example:** Distribution checklist must be updated to reflect the actual `register(registry)` signature and load-order/error-isolation contract.

### Category 8: Production-readiness signals

- **Question:** Is the code ready for the factory cron to actually use it?
- **Method:** Check that:
  - No new silent failure paths
  - Telemetry integration works end-to-end (record → table → dashboard → ops_feed)
  - Hook dispatch is exception-isolated
  - Plugin auto-discovery is idempotent
- **Example:** If Gap 12's `_drain` swallows an exception, no one notices until Sprint 2 review.

## Verdict scale

- **COMPLETE:** All categories PASS. Sprint 1 ships as Phase 3 first installment.
- **NEEDS_FIXES:** 1-3 categories FAIL or 4+ categories CONCERN. Open a P0/P1 follow-up gap (Phase 3 Sprint 2).
- **NEEDS_MAJOR_REWORK:** 4+ categories FAIL. Roll back the last PR or revert to deploy-fresh HEAD before Sprint 1.

## Output format

The meta-review subagent returns a markdown artifact with one section per category, each containing:
- Verdict (PASS / CONCERN / FAIL)
- Evidence (file:line + REPL probe output)
- Recommended fix (if not PASS)

Saved to `okf/operations/phase3-sprint1-meta-review-<date>.md`.

---

## What the meta-review is NOT

- **Not a re-do of per-PR review** — if Sonnet already APPROVE'd a PR, the meta-review shouldn't re-litigate it. Focus on cross-PR concerns.
- **Not a code-quality audit** — that's the per-PR review's job. The meta-review looks at the cross-cutting story.
- **Not a performance benchmark** — flag regressions but don't try to characterize them. That's a Sprint 2 task.

---

## Timing

After Gap 10 merges, before declaring Sprint 1 complete, Fred:
1. Runs `pytest prismatic/` to verify 302/302 (or whatever the actual count is)
2. Writes a meta-review prompt covering the 8 categories above
3. Fires Sonnet with `--dangerously-skip-permissions`, 7-min timeout
4. Reads the verdict
5. If COMPLETE: write final status doc, update memory, done
6. If NEEDS_FIXES: open follow-up gaps, document, continue
7. If NEEDS_MAJOR_REWORK: revert the last PR, regroup

---

*Filed 2026-06-28 by Fred (orchestrator). Continuation of Opus's interrupted plan output.*
