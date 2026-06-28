# Phase 3 Second-Opinions — Sprint 1 Spec Reviews

**Date:** 2026-06-28
**Trigger:** 3 spec-first design reviews delegated to subagents before implementation
**Verdict on all 3:** **REQUEST_CHANGES** (none approved as-is)
**Outcome:** All 3 specs need revision; Gap 12 needs major rewrite (existing telemetry infrastructure missed)

---

## Why this matters

I wrote 3 specs and asked 3 subagents to challenge them in parallel. All 3 found substantive issues. Two specs had test-coverage blind spots (Lesson 10 from Gap 9 meta-review). One spec (Gap 12) was built on a wrong premise — it invented a parallel observability system when `prismatic/telemetry.py` (905 lines, SQLite-backed, queue+daemon-thread) already exists.

This is the meta-review-architecture skill working as designed: review BEFORE code, not after.

---

## Gap 10 — Plugin Auto-Discovery

**Verdict:** REQUEST_CHANGES

**Critical findings (2):**
1. **Ship-then-validate ordering inversion** — my spec said Gap 12 ships FIRST to validate Gap 10. Subagent caught this: Gap 12's stated purpose (per the spec itself) is to validate Gap 10, which means it ships AFTER, not before. The current ordering in Phase 3 sprint numbering has Gap 10/11/12 as parallel; the dependency is real but I had it backwards.
2. **10k-pattern DoS becomes reachable** — meta-review P1 explicitly said "before plugin auto-discovery is wired in Gap 10." My spec wires discovery without the ceiling. Any `pip install` of a malicious or buggy plugin can now make every review take minutes.

**High findings (4):**
- Test count baseline wrong (claimed 261, actual is 249)
- Rubric misses end-to-end coverage — would have caught the Lesson 10 failure mode
- Missing public-import regression test (would have caught QualityCheck regression)
- Spec silent on ordering dependency with Gap 11

**Medium findings (4):** pattern ceiling, idempotency, heavy imports, version pinning, conflicting pattern registrations

**Low findings (3):** function signature clarity, ops-feed stub vs Gap 12, `QualityCheck` in example imports, test placement

**Verdict subagent's exact words:** "the spec is structurally sound but carries forward the meta-review patterns' most painful lessons in two new ways."

---

## Gap 11 — Wire the Deferrals (Impact Rules + Hook Dispatch)

**Verdict:** REQUEST_CHANGES

**Critical/High findings (4):**
1. **Test #14 is structurally wrong** — asserts `classify_impact()` returns `"major"` but `classify_impact()` does NOT consume `spec.impact_rules`. The consuming function is `apply_impact_rules()` called from `PipelineOrchestrator.process()`. Test would pass even if Ned forgot to wire the orchestrator.
2. **Tests #11 and #12 (hook firing)** — "verify it ran" with `lambda *a: None` is indistinguishable from "no hook registered." Need both a flag assertion AND a mutation-through assertion.
3. **Breaking-change rollout under-specified** — `PipelineOrchestrator(registry=...)` as required vs optional vs optional-with-warning. The choice recreates P0 #2 if "optional with silent skip."
4. **HookBus `*args` design discards type info** — each hook has different signature; `(args, kwargs)` is not enough.

**Medium findings (4):**
- Hook handlers firing inside `PipelineOrchestrator._lock` will serialize concurrent reviews
- Spec contradicts itself: line 104 "no new registry methods" vs line 119 `hooks_for(name)` method
- Missing performance/type-safety/dedup tests
- Three logical PRs bundled into one; commit ordering implicit

**Low findings (3):** redundant parameter, no docstring-regression-guard, naming

**Verdict subagent's exact words:** "the spec closes the right gap but inherits the exact structural blind spot that created the original P0 #2 (Lesson 10)."

---

## Gap 12 — Observability Slice (Counters + Linear Ops Feed)

**Verdict:** REQUEST_CHANGES — **MASSIVE REWRITE REQUIRED**

**Critical findings (3):**
1. **`prismatic/telemetry.py` already exists** — 905 lines, queue+daemon-thread, SQLite-backed persistence. My spec reinvented it badly (in-memory, single-Lock, no persistence). The subagent verified this by reading the codebase; I missed it entirely when writing the spec.
2. **`GRO-OPS` Linear issue is invented** — `grep -rn 'GRO-OPS'` across the entire okf tree returns zero hits outside my spec. The "existing ops-feed target" doesn't exist.
3. **Test #13 swallows failures without verifying swallow behavior** — same Lesson 10 anti-pattern: tests assert against mocks that don't fail in a way that proves end-to-end non-crash.

**High findings (5):**
- "10K increments/sec, lock uncontended" is fiction — factory cron is 0.003/sec per Gap 9 Lesson 1; lock is over-engineered AND under-engineered for actual burst case
- In-memory counters reset on dispatcher restart — recreates the "259 NHR tasks piled up" blind spot
- Linear API rate limits ignored (60 req/min free, 1500 paid; spec emits 6 events per review)
- `dispatcher_integration.py` is invented — no existing precedent in the codebase
- Test count arithmetic based on undefined baseline (claimed 279, actual is 249)

**Medium findings (4):**
- Missing histogram/percentile support for latency
- Missing sampling strategy for high-volume events
- Missing file/syslog export (Linear is human-consumption only)
- `ReviewMetrics` scope ambiguity (singleton vs per-dispatcher)

**Low findings (2):**
- Non-serializable payload edge cases
- OTel-shape vs dataclass-shape for future extension

**Verdict subagent's exact words:** "the spec reinvents [TelemetryCollector] badly (in-memory, single-Lock, no persistence). This is silent re-invention — the exact failure mode Gap 9 Lesson 1 was written to prevent."

---

## Common pattern across all 3 specs

The subagent reviewers all found the same class of issue: **spec-level assumptions that aren't validated against the actual codebase**. This is what spec-first review is for. Going forward, every spec I write should include:
- A "Search the codebase first" section at the top, listing what existing modules/classes/infrastructure I verified
- A "Verify these claims" section listing the test counts, line numbers, and external dependencies I claim exist
- A "What this spec does NOT touch" section listing the meta-review carry-forwards and adjacent systems

## What changes next

Per the user's questions:
1. (Pending) Reconnaissance pass vs just-revise — TBD with Michael
2. (Pending) Gap 12 strategy — extend TelemetryCollector vs keep as separate gap vs skip

The second-opinion skill worked. The cost was 3 × 60 seconds of subagent time. The benefit was catching 3 specs' worth of issues BEFORE writing 43 tests + 3 modules + 3 PRs. Worth it.

---

*Audit trail for Phase 3 Sprint 1. Filed 2026-06-28 by Fred (orchestrator).*
