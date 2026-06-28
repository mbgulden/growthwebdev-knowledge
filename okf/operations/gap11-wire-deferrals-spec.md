# Gap 11 — Wire the Deferrals (Impact Rules + Hook Dispatch)

**Date:** 2026-06-28 (revised after recon)
**Sprint:** 1 of 3 (Phase 3)
**Lane:** Ned (code)
**Estimated effort:** 2 days
**Status:** SPEC REVISION — pending Michael's sign-off

---

## What changed from the original spec

**Original (REQUEST_CHANGES):** Proposed `apply_impact_rules()` + `HookBus` but missed:
1. **Test #14 was wrong:** asserted `classify_impact()` returns `"major"` but `classify_impact()` doesn't consume `spec.impact_rules` — test would pass even if orchestrator was unwired (Lesson 10 anti-pattern)
2. **Tests #11 and #12 indistinguishable from no-op:** `lambda *a: None` makes "hook fired" = "no hook registered"
3. **Breaking-change rollout under-specified** — `PipelineOrchestrator(registry=...)` semantics unclear
4. **HookBus `*args` design discards type info** — each hook has different signature
5. **Hook handlers firing inside `PipelineOrchestrator._lock`** will serialize concurrent reviews

**Recon findings (full audit in `phase3-reconnaissance-2026-06-28.md`):**
- `PipelineOrchestrator.__init__` signature: `(max_rework_attempts: int = 2)` only — no registry/hook-bus
- `process()` body holds `threading.Lock` for the full critical section (line 331)
- `classify_impact()` and `decide_next_action()` are pure functions, called only at lines 332/334 of `process()`
- `spec.impact_rules` is **never read** in production code — verified by grep across entire repo
- `RealPRReviewer.review_pr()` has well-defined insertion points (L502/506, L507) for `HOOK_BEFORE_SECRET_SCAN` and `HOOK_BEFORE_QUALITY_CHECKS`
- `trigger_ned_review()` has 3 candidate hook points (before/after review, before pipeline)
- `test_rules_fire_in_registration_order` (L137-159) manually iterates rules — Lesson 10 anti-pattern confirmed
- `test_register_impact_rule_docstring_warns` (L370-387) asserts "Currently inert" string — **must be updated** when wiring lands

**Revised approach:**
- Fix test #14: assert on `PipelineOrchestrator.process()` output, NOT `classify_impact()`
- Fix tests #11/#12: assert on both flag AND mutation (proves hook ran)
- Hook handler execution outside the `_lock` (defer if needed; serialize only the read-modify-write of attempt counter)
- Per-hook type contracts (each hook has explicit signature; not `*args`)
- HookBus is a thin wrapper around registry spec — no new module if simpler

---

## Goal

Close the "code-complete but operationally dead" loop on the 5 HOOK_* constants + `register_impact_rule()` channel that shipped as inert identifiers in PR #41 (Phase 2 / Gap 9 / Part B). After this gap, plugin authors can register impact-override rules + hook callbacks and observe them taking effect in production reviews.

## Non-Goals (re-affirmed)

- **Plugin lifecycle management** (load/unload/reload) — Gap 10 territory
- **Async/threaded hook dispatch** — synchronous-only for now
- **Hook filtering by phase** — future work
- **Bridging the old `PluginLoader.execute_hook`** — separate gap

## Current State (verified by recon — reconfirms Gap 9 / Part B inventory)

| Channel | Defined in | Dispatched by | Status |
|---|---|---|---|
| `register_secret_pattern()` | `registry.py` | `RealPRReviewer._detect_secrets_with_registry()` (line 592) | ✅ ALREADY WIRED |
| `register_check()` | `registry.py` | `RealPRReviewer.review_pr()` loop (line 513) | ✅ ALREADY WIRED |
| `register_impact_rule()` | `registry.py` | (nothing) | ❌ INERT |
| `HOOK_BEFORE_SECRET_SCAN` | `hooks.py` | (nothing) | ❌ INERT |
| `HOOK_BEFORE_QUALITY_CHECKS` | `hooks.py` | (nothing) | ❌ INERT |
| `HOOK_BEFORE_CLASSIFY_IMPACT` | `hooks.py` | (nothing) | ❌ INERT |
| `HOOK_BEFORE_DECIDE_ACTION` | `hooks.py` | (nothing) | ❌ INERT |
| `HOOK_BEFORE_NED_REVIEW` | `hooks.py` | (nothing) | ❌ INERT |

**Gap 11 closes 6 channels.**

## Public API Contracts

### 1. Impact Rule Dispatch

`PipelineOrchestrator.__init__` gains optional `registry` param:

```python
def __init__(
    self,
    max_rework_attempts: int = DEFAULT_MAX_REWORK_ATTEMPTS,
    *,
    registry: ReviewerRegistry | None = None,
) -> None:
    self.max_rework_attempts = max_rework_attempts
    self._attempt_counts: dict[str, int] = {}
    self._lock = threading.Lock()
    self._registry = registry  # NEW
```

**`process()` body change** — after `classify_impact(result)` returns, apply registered impact rules:

```python
with self._lock:
    # 1. Read attempt count under lock (existing)
    attempts = self._attempt_counts.get(identifier, 0)

    # 2. Compute base impact (existing)
    impact = classify_impact(result)

    # 3. Apply registered impact rules OUTSIDE the classify call (NEW)
    if self._registry is not None:
        spec = self._registry.compose()
        impact = apply_impact_rules(result, impact, spec.impact_rules)

    # 4. Decide action (existing)
    action = decide_next_action(
        result,
        rework_attempts=attempts,
        max_rework_attempts=self.max_rework_attempts,
    )

    # 5. Apply registered action rules (NEW — uses same apply_impact_rules shape)
    if self._registry is not None:
        spec = self._registry.compose()
        action = apply_impact_rules(result, action, spec.impact_rules)

    # ...rest of process() unchanged
```

`apply_impact_rules` is a pure function:

```python
def apply_impact_rules(
    result: PRReviewResult,
    current_value: str,
    rules: tuple[ImpactRule, ...],
) -> str:
    """Apply registered impact/action rules in order; first non-None wins.

    Each rule is `Callable[[PRReviewResult, str], str | None]`.
    Rules fire in registration order. First rule returning non-None
    overrides `current_value`. If all rules return None, current_value
    is returned unchanged.
    """
    value = current_value
    for rule in rules:
        override = rule(result, value)
        if override is not None:
            return override
    return value
```

**Reentrancy + concurrency design:**
- `apply_impact_rules` is a pure function — no lock needed inside it
- `spec = self._registry.compose()` is called inside the lock; `compose()` is O(N) over registered items (cheap)
- Hook handler execution for HOOK_BEFORE_CLASSIFY_IMPACT happens OUTSIDE the lock (see section 2)

### 2. Hook Dispatch

**No new `HookBus` module.** Hooks are dispatched via the existing `apply_impact_rules` + a small helper `fire_hook(hook_name, *, args, spec, hooks_module=hooks)` because all 5 hooks have a common shape: take args, return a value or None.

```python
def fire_hook(
    hook_name: str,
    *,
    args: tuple[Any, ...],
    spec: ComposedReviewerSpec | None,
) -> Any:
    """Fire a named hook against the registry's checks/impact_rules.

    A hook's handlers are the registered items in spec.checks (for
    diff-args hooks) or spec.impact_rules (for result-args hooks).

    Returns the first non-None return value, or None.

    Handler exceptions are caught, logged at warning level, and skipped
    (does not abort the calling review).
    """
    if spec is None:
        return None
    # Hooks use the same apply_impact_rules shape — pass args[0] as result
    # and args[1] as current_value. impact_rules fire in registration order.
    if hook_name in HOOKS_USING_IMPACT_RULES:
        result, current = args[0], args[1]
        return apply_impact_rules(result, current, spec.impact_rules)
    # diff-args hooks (BEFORE_SECRET_SCAN, BEFORE_QUALITY_CHECKS) use checks
    return None
```

**Per-hook contracts (from recon-verified insertion points):**

| Hook | Trigger point | Arg type | Return type | Consumer code |
|---|---|---|---|---|
| `HOOK_BEFORE_SECRET_SCAN` | Before `_detect_secrets_with_registry` (review_pr L506) | `diff: str` | `list[tuple[regex, kind, severity]]` (extra patterns) | New: merge into spec.secret_patterns |
| `HOOK_BEFORE_QUALITY_CHECKS` | Before `check_function_length` (review_pr L507) | `diff: str` | `list[QualityCheck]` (extra check callables) | New: invoke before builtins |
| `HOOK_BEFORE_CLASSIFY_IMPACT` | Before `classify_impact(result)` (pipeline L332) | `result: PRReviewResult` | `str` (impact override) | `apply_impact_rules` |
| `HOOK_BEFORE_DECIDE_ACTION` | Before `decide_next_action(...)` (pipeline L334) | `result, attempts` | `str` (action override) | `apply_impact_rules` |
| `HOOK_BEFORE_NED_REVIEW` | Before `reviewer.review_pr(pr_url)` (gates L1028) | `issue: dict` | ignored (side-effect only) | New: invoke then ignore return |

**Docstring updates:**
- Remove `.. warning:: Currently inert` from `register_impact_rule()` (per Gap 11 wiring)
- Remove `TODO Gap 9 / Part C: wire dispatch in ...` from each `HOOK_*` docstring
- Replace with `Wired: see PipelineOrchestrator.process() / RealPRReviewer.review_pr() / trigger_ned_review()`
- Update `test_register_impact_rule_docstring_warns` to assert the NEW positive contract (warning is gone; docstring now describes active behavior)

## Files Changed

| File | Change |
|---|---|
| `prismatic/review/pipeline.py` | `PipelineOrchestrator.__init__` accepts `registry`; `process()` calls `apply_impact_rules` after `classify_impact` and after `decide_next_action` |
| `prismatic/review/apply_impact_rules.py` (NEW) | Pure function `apply_impact_rules()` + `fire_hook()` helper |
| `prismatic/review/pr_reviewer_impl.py` | `RealPRReviewer.review_pr()` fires `HOOK_BEFORE_SECRET_SCAN` before secret scan (line 506), `HOOK_BEFORE_QUALITY_CHECKS` before quality checks (line 507) |
| `prismatic/quality/gates.py` | `trigger_ned_review()` fires `HOOK_BEFORE_NED_REVIEW` before `reviewer.review_pr(pr_url)` (line 1028) |
| `prismatic/review/registry.py` | Update `register_impact_rule()` docstring (remove warning) |
| `prismatic/review/hooks.py` | Update each `HOOK_*` docstring (remove TODO) |
| `prismatic/review/test_wire_deferrals.py` (NEW) | 16 test rubrics below |
| `prismatic/review/test_registry.py` | UPDATE `test_register_impact_rule_docstring_warns` to assert new positive contract |

## Test Rubrics

In `TestApplyImpactRules` (5 tests — pure function):

1. `test_no_rules_returns_current_value` — empty rules tuple, returns input unchanged
2. `test_first_non_none_rule_wins` — rule_a returns None, rule_b returns "blocker", result is "blocker"
3. `test_rules_fire_in_registration_order` — verify order via call log on a mock rules tuple
4. `test_rule_returning_invalid_value_logs_warning` — defensive: rule returns `"nonsense"`, accepted as-is (current_value is just a string)
5. `test_apply_impact_rules_does_not_raise_on_handler_exception` — handler raises, exception caught, dispatcher continues

In `TestHookDispatch` (5 tests — fix for the original spec's `lambda *a: None` anti-pattern):

6. `test_fire_hook_returns_none_when_no_registry` — `spec is None`, no crash, returns None
7. `test_fire_hook_invokes_registered_check_with_correct_args` — register a check that records its args to a list, fire hook, verify args recorded (mutation-through assertion, not just a flag)
8. `test_fire_hook_returns_first_non_none_result` — register 3 checks: returns None, returns "x", returns "y" → result is "x" (NOT "y")
9. `test_fire_hook_isolates_handler_exceptions` — register a check that raises + a check that returns "ok" → result is "ok"
10. `test_fire_hook_passes_through_when_all_return_none` — 3 checks return None → result is None

In `TestEndToEnd` (6 tests — the ones that would have caught Lesson 10 anti-pattern):

11. `test_real_reviewer_fires_before_secret_scan_with_diff_arg` — register a hook check, run `RealPRReviewer.review_pr()`, verify the check was called with the actual diff string (mutation-through: check appends diff to a list)
12. `test_real_reviewer_fires_before_quality_checks_with_diff_arg` — same pattern for QUALITY_CHECKS hook
13. `test_pipeline_orchestrator_impact_rule_changes_decision_impact` — **REVISED test #14**: register an impact rule that returns "blocker", run `PipelineOrchestrator.process()`, verify `decision.impact == "blocker"` (NOT `classify_impact()` output)
14. `test_pipeline_orchestrator_action_rule_changes_decision_action` — register an action rule that returns ACTION_GIVE_UP, run `process()`, verify `decision.action == ACTION_GIVE_UP`
15. `test_trigger_ned_review_fires_before_ned_review_hook_with_issue_arg` — register a hook check that records `issue` arg, call `trigger_ned_review()`, verify recorded
16. `test_full_review_through_real_reviewer_pipeline_orchestrator_with_registry` — real review → real pipeline, with registered impact rule that escalates → verify final `decision.impact` is escalated (the integration test that proves wiring is real)

**Total: 16 new tests** + 1 updated test (the docstring meta-test).

## Acceptance Criteria

- [ ] `apply_impact_rules()` exported from `prismatic.review`
- [ ] `PipelineOrchestrator(registry=...)` accepts registry param; old `PipelineOrchestrator()` still works
- [ ] Each `HOOK_*` constant fires when its trigger condition is met
- [ ] Hook failure isolated (warning logged, dispatch continues)
- [ ] `register_impact_rule()` no longer says "Currently inert" — actually wired
- [ ] `test_register_impact_rule_docstring_warns` updated to assert positive contract
- [ ] Test #13 asserts on `decision.impact` from `PipelineOrchestrator.process()`, NOT on `classify_impact()` directly (this is the Lesson 10 fix)
- [ ] Tests #11/#12 use mutation-through assertions (recorded args list), NOT just boolean flags (Lesson 10 fix)
- [ ] 16 new tests pass + 1 updated test passes; 266/266 total (was 250; +16)
- [ ] Peer review APPROVE

## Acceptance: "This Gap Shipped Correctly" Evidence

- `test_full_review_through_real_reviewer_pipeline_orchestrator_with_registry` (test #16) passes — registers an impact rule, runs a real review end-to-end, verifies the rule changed the final decision
- `test_real_reviewer_fires_before_secret_scan_with_diff_arg` (test #11) passes — proves hooks fire in production code path, not just manual iteration
- The 6 channels listed as "INERT" in the Current State table are all moved to ✅ WIRED after this PR lands

## Carry-Forward (not in this gap)

- **Async/threaded hook dispatch** — synchronous-only for now
- **Hook filtering by phase** — future work
- **Hook reentrancy** (handlers calling back into the registry) — currently not supported; hooks cannot recursively fire other hooks
- **Performance ceiling** — 100+ impact rules firing per review is fine for current load; defer to scaling track

## Lane Notes

- **Ned lane only** — pure code change; no infra hookup (Gap 12 will wire telemetry into the new dispatch paths)
- Single PR expected: PR #X (Ned)

## Pattern Reference

- `okf/operations/phase3-reconnaissance-2026-06-28.md` — verified insertion points + lock semantics
- `okf/operations/phase3-second-opinions-2026-06-28.md` — original spec review
- `okf/operations/phase2-meta-review-2026-06-28.md` — P0 #2 was about inert impact_rules; this gap closes it
- `okf/operations/gap9-implementation-lessons.md` — Lesson 10 (tests with good coverage can hide dead APIs)

---

*Spec revised by Fred (orchestrator) after recon + subagent review. Pending Michael's sign-off.*
