# Gap 11 — Wire Deferrals Execution Plan

**Estimated Sonnet subagent time:** ~45 minutes
**Files touched:** 8 (5 modified, 2 new production, 1 new test)
**Tests added:** 16 new + 1 updated
**Exit criteria:** 290/290 tests passing (273 from Gap 12 + 17)

---

## Subagent Prompt Skeleton

### Context to Pass

```
You are implementing Gap 11 (Wire the Deferrals) for the Prismatic Engine.
Gap 12 has already landed. The test baseline is now 273/273.

READ THESE FILES FIRST (in order):
1. prismatic/review/pipeline.py — PipelineOrchestrator (you're adding registry param)
   Focus on: __init__ (L291), process() (L316-373), threading.Lock usage (L331)
2. prismatic/review/pr_reviewer_impl.py — RealPRReviewer
   Focus on: review_pr() insertion points (L502-507 for hooks)
3. prismatic/review/registry.py — ReviewerRegistry + ComposedReviewerSpec
   Focus on: register_impact_rule() docstring, compose() method
4. prismatic/review/hooks.py — HOOK_* constants (5 total)
   Focus on: module docstring (L26-31 "Dispatch code is NOT YET WIRED")
5. prismatic/quality/gates.py — trigger_ned_review()
   Focus on: L1010-1028 (before review), L1028-1035 (after review)
6. prismatic/review/test_registry.py — existing tests
   Focus on: test_register_impact_rule_docstring_warns (L370-387)

SPEC: [embed gap11-wire-deferrals-spec.md contents]

CRITICAL CONSTRAINTS:
- compose() called ONCE per process() invocation (optimization from spec review)
- apply_impact_rules is a PURE FUNCTION (no lock inside it)
- Hook handlers fire OUTSIDE the _lock (concurrency concern from recon)
- Exception isolation: handler raises → warning logged → dispatch continues
- Tests MUST go through production code paths (Lesson 10 anti-pattern fix)
- test_register_impact_rule_docstring_warns must be UPDATED (remove "Currently inert" assertion, add positive contract assertion)
```

### Rubric (verifiable handles in return)

```
RETURN FORMAT:
1. Files created/modified (with line count + diff summary)
2. apply_impact_rules() signature and location
3. fire_hook() signature and location
4. PipelineOrchestrator.__init__ new signature (show backward compat)
5. Each HOOK_* constant: where it fires, what args it gets
6. Updated docstrings: before/after for register_impact_rule()
7. Updated test: before/after for test_register_impact_rule_docstring_warns
8. Test file path + test count + test names
9. pytest output: 290 passed
10. Confirmation: 273 baseline tests still pass
```

---

## Integration Steps for Fred After Subagent Returns

1. **Verify backward compatibility:** `python -c "from prismatic.review.pipeline import PipelineOrchestrator; p = PipelineOrchestrator(); print(p)"` → must work without `registry` arg
2. **Verify compose() optimization:** Search `process()` body for `compose()` — must appear exactly once, inside the `if self._registry is not None:` block
3. **Verify hook dispatch locations:**
   - `grep -n "fire_hook\|HOOK_BEFORE" prismatic/review/pr_reviewer_impl.py` → 2 hook sites
   - `grep -n "fire_hook\|HOOK_BEFORE" prismatic/review/pipeline.py` → 2 hook sites
   - `grep -n "fire_hook\|HOOK_BEFORE" prismatic/quality/gates.py` → 1 hook site
4. **Verify docstring update:** `grep -n "Currently inert" prismatic/review/registry.py` → 0 hits
5. **Verify Lesson 10 fix:** Read tests #11, #12, #13 — each must call production code (review_pr, process), not manual dispatch
6. **Branch creation:** `ned/gap11-wire-deferrals`
7. **Push:** No `--no-verify` needed (all files in Ned lane)
8. **Peer review:** Dispatch Sonnet reviewer
9. **Merge:** Only after APPROVE

---

## Rollback Plan if PR Fails Peer Review

**Severity: MEDIUM risk.** Gap 11 introduces a breaking change (`PipelineOrchestrator(registry=...)`) and modifies 5 production files.

1. If peer review returns REQUEST_CHANGES:
   - Fix in-place; most likely issues: lock semantics, exception isolation, hook arg types
   - Re-run `pytest` to confirm 290/290
   - Re-submit
2. If peer review flags the `PipelineOrchestrator(registry=...)` breaking change:
   - The `registry` param is keyword-only with default `None` → backward compatible
   - If reviewer disagrees: add a deprecation path where `PipelineOrchestrator` auto-discovers registry from a module-level singleton (NOT preferred, but possible escape hatch)
3. If peer review returns NEEDS_MAJOR_REWORK on hook dispatch design:
   - Escalate to Opus
   - If Opus recommends a different dispatch pattern (e.g., separate HookBus class), implement the alternative
   - This is the most likely rework scenario — the `fire_hook()` design is simple but may be too simplistic
4. **Nuclear rollback:** If Gap 11 cannot ship, Gap 10 can still land WITHOUT advertising `register_impact_rule()` as functional — the "Currently inert" docstring stays, and Gap 10's distribution checklist explicitly warns plugin authors

---

## Risks

### R11-1: `PipelineOrchestrator._lock` serializes reviews if hook handlers are slow

**File:line:** `prismatic/review/pipeline.py:331` — `with self._lock:`
**Likelihood:** Low (hooks are synchronous, no I/O expected in current use)
**Impact:** High if triggered — concurrent reviews queue behind slow hook handlers
**Mitigation:** Spec mandates hook handlers fire OUTSIDE the lock. The implementation must:
  1. Acquire lock → read attempt counter → compute base impact → release lock
  2. Fire hooks (outside lock) → apply impact rules
  3. Re-acquire lock → decide action → bump counter → release lock
**Escape hatch:** If the split-lock approach is too complex for Sprint 1, accept serialization and add a `# TODO: move hook dispatch outside lock` comment. At current load (~0.003 events/sec), serialization is not a problem.

### R11-2: `apply_impact_rules` called twice but spec says compose() once

**File:line:** `prismatic/review/pipeline.py:332-338` (process() body)
**Likelihood:** Medium — subagent may miss the optimization note
**Mitigation:** The subagent prompt explicitly states "compose() called ONCE per process() invocation." The rubric requires confirmation of compose() call count. Fred verifies in integration step #2.
**Escape hatch:** If compose() is called twice, it's a ~3-line fix (hoist spec = self._registry.compose() above both apply calls).

### R11-3: `test_register_impact_rule_docstring_warns` fails after docstring update

**File:line:** `prismatic/review/test_registry.py:370-387`
**Likelihood:** High — this test WILL fail after the docstring change (by design)
**Impact:** Low — it's a meta-test, not a behavior test
**Mitigation:** Subagent prompt explicitly requires updating this test. The rubric checks before/after assertion text. Fred verifies in integration step #4.
**Escape hatch:** If the subagent forgets, Fred can fix the test in ~2 minutes.

---

## File Paths and Line Numbers (from recon)

| Target | File | Key Lines | What to Do |
|---|---|---|---|
| PipelineOrchestrator.__init__ | `prismatic/review/pipeline.py` | L291 | Add `registry: ReviewerRegistry \| None = None` kwarg |
| process() critical section | `prismatic/review/pipeline.py` | L316-373 | Insert `apply_impact_rules` after `classify_impact` (L332) and after `decide_next_action` (L334) |
| threading.Lock | `prismatic/review/pipeline.py` | L331 | Consider split-lock for hook dispatch |
| review_pr() hook sites | `prismatic/review/pr_reviewer_impl.py` | L502-507 | Fire HOOK_BEFORE_SECRET_SCAN, HOOK_BEFORE_QUALITY_CHECKS |
| register_impact_rule docstring | `prismatic/review/registry.py` | ~L155-169 | Remove "Currently inert" warning, add positive contract |
| HOOK_* constants | `prismatic/review/hooks.py` | L43-82 | Update docstrings (remove TODO) |
| Module docstring | `prismatic/review/hooks.py` | L26-31 | Update "Dispatch code is NOT YET WIRED" → "Dispatched by..." |
| trigger_ned_review hook | `prismatic/quality/gates.py` | L1010-1028 | Fire HOOK_BEFORE_NED_REVIEW before `reviewer.review_pr()` |
| Docstring meta-test | `prismatic/review/test_registry.py` | L370-387 | Update assertion from "Currently inert" to positive contract |
| Impact rules manual test | `prismatic/review/test_registry.py` | L137-159 | DO NOT modify — these still test the registry, not the pipeline |

---

*Filed 2026-06-28 by Opus (claude-opus-4-6-thinking). Gap 11 execution detail.*
