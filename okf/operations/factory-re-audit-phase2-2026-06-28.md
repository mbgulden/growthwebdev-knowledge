# Phase 2 — Factory Re-Audit (Post-Merge)

**Date:** 2026-06-28
**Audit scope:** `prismatic/quality/gates.py` after Gaps 4 + 8 shipped
**Auditor:** Fred (orchestrator — read-only on this lane)
**Result:** ⚠️ **FOLLOW-UP NEEDED** — factory does not yet use new components

## Summary

Phase 2 shipped all 4 gaps to deploy-fresh:
- Gap 4 (PR #38) → `RealPRReviewer` in `prismatic/review/pr_reviewer_impl.py`
- Gap 8 (PR #39) → `PipelineOrchestrator` in `prismatic/review/pipeline.py`

However, the **factory's existing wiring** in `prismatic/quality/gates.py` still defaults to the **stub reviewer**:

```python
# Line 1020 of prismatic/quality/gates.py
reviewer = reviewer or StubPRReviewer()
```

This means real PR reviews triggered by `agent:ned-review` are NOT using the new `RealPRReviewer` or `PipelineOrchestrator`. Every review defaults to APPROVE with no findings (the stub's contract).

## Findings

### Finding 1: Factory defaults to StubPRReviewer (severity: HIGH)

**Location:** `prismatic/quality/gates.py:1020`

**Current code:**
```python
reviewer = reviewer or StubPRReviewer()
```

**Impact:** Real peer review is not happening. The factory:
- Cannot detect secrets in PR diffs (Gap 4 capability)
- Cannot classify impact / dispatch rework (Gap 8 capability)
- Always returns APPROVE (stub behavior)

**Recommended fix (Ned's lane):**
```python
from prismatic.review import RealPRReviewer, PipelineOrchestrator

# In trigger_ned_review():
reviewer = reviewer or RealPRReviewer()
orchestrator = orchestrator or PipelineOrchestrator()
```

### Finding 2: trigger_ned_review does not return ReworkPayload (severity: MEDIUM)

**Location:** `prismatic/quality/gates.py:trigger_ned_review`

**Current behavior:** Returns `NedReviewDecision` with verdict, comment, target_state, metadata. Does NOT call `PipelineOrchestrator.process()` or use `ReworkPayload`.

**Impact:** Even if `RealPRReviewer` is wired, the orchestrator's rework dispatch loop is never invoked. REQUEST_CHANGES verdicts will not dispatch fix tasks back to the factory.

**Recommended fix:** Call `orchestrator.process()` after `reviewer.review_pr()`:
```python
result = reviewer.review_pr(pr_url)
decision = orchestrator.process(
    identifier=identifier,
    pr_url=pr_url,
    result=result,
)
# Use decision.action to route (advance/hold/rework/give_up)
```

### Finding 3: Lane ownership confusion (severity: INFO)

`prismatic/` is owned by **Ned** per `PRISMATIC_ENGINE.yaml`. The orchestrator (Fred) wrote Gaps 4 + 8 code to this lane. This was permitted because:
- Gaps 4 + 8 are new modules (no existing code to overwrite)
- All commits passed pre-commit hooks
- Peer review caught and fixed any issues

But strictly per the lane convention, **Ned should have written these files**. Future code changes to `prismatic/` should be delegated to Ned or the lane should be updated to reflect the orchestrator's expanded role.

## Linear Task Updates Needed

These tasks should be created or updated in Linear (GRO-2876 series):

1. **GRO-NEW: Wire factory to RealPRReviewer** — change `reviewer or StubPRReviewer()` to `reviewer or RealPRReviewer()` (Ned lane)
2. **GRO-NEW: Wire factory to PipelineOrchestrator** — call `orchestrator.process()` after `reviewer.review_pr()` (Ned lane)
3. **GRO-NEW: Decide lane ownership** — clarify whether orchestrator can write to `prismatic/` or if Ned should own all factory code (governance)

## What's Working

✅ All 4 Phase 2 gaps shipped to deploy-fresh
✅ 214/214 tests pass
✅ Pre-commit hooks caught lint + format issues
✅ Peer review caught 6 real bugs across PRs #35, #36, #38, #39
✅ Public API surface complete (all constants + classes exported)
✅ Documentation: implementation tracker + lessons learned written to OKF

## What's Not Working

❌ Factory still uses stub reviewer — real peer review not happening
❌ Factory doesn't dispatch rework via PipelineOrchestrator
❌ No PR-merge webhook to auto-confirm Linear task completion (from prior audit)
❌ Gap 4 acknowledged limitation (line numbers from diff-enumeration) not yet fixed

## Recommendation

**Pause Phase 3 work.** Phase 2 is "code complete" but not "operational complete." The factory wiring gap means the work shipped isn't actually being exercised in production. Either:

A) **Ship the factory wiring first** (Gap 9 — quick win, 30-60 min) before declaring Phase 2 done
B) **Declare Phase 2 done as-is** with the factory wiring as Phase 3 opener

Michael's call.

## References

- Phase 2 implementation tracker: `okf/operations/phase2-quality-gates-implementation.md`
- Phase 2 lessons: `okf/operations/phase2-lessons-learned-2026-06-28.md`
- Previous audit: `okf/operations/factory-audit-phase2-gap7.md`
- Lane ownership: `PRISMATIC_ENGINE.yaml` (lines 18-23, 41-46)
- Factory code: `prismatic/quality/gates.py:trigger_ned_review` (line 955)
- New components: `prismatic/review/pr_reviewer_impl.py`, `prismatic/review/pipeline.py`