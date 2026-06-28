# Gap 11 — Wire the Deferrals (Impact Rules + Hook Dispatch)

**Date:** 2026-06-28
**Sprint:** 1 of 3 (Phase 3)
**Lane:** Ned (code)
**Estimated effort:** 2 days
**Status:** SPEC — pending Michael's sign-off

---

## Goal

Close the "code-complete but operationally dead" loop on the 5 HOOK_* constants + 3 registry channels that shipped as inert identifiers in PR #41 (Phase 2 / Gap 9 / Part B). After this gap, plugin authors can register impact-override rules + hook callbacks and observe them taking effect in production reviews.

## Non-Goals

- **Plugin lifecycle management** (load/unload/reload) — Gap 10 territory
- **Async/threaded hook dispatch** — synchronous-only for now; performance is fine
- **Hook filtering by phase** (e.g. "only fire HOOK_BEFORE_NED_REVIEW for issue type X") — future work

## Current State (inert from Gap 9 / Part B)

| Channel | Defined in | Dispatched by | Status |
|---|---|---|---|
| `register_secret_pattern()` | `registry.py` | `RealPRReviewer._detect_secrets_with_registry()` | ✅ ALREADY WIRED (PR #41) |
| `register_check()` | `registry.py` | `RealPRReviewer.review_pr()` | ✅ ALREADY WIRED (PR #41) |
| `register_impact_rule()` | `registry.py` | (nothing) | ❌ INERT |
| `HOOK_BEFORE_SECRET_SCAN` | `hooks.py` | (nothing) | ❌ INERT |
| `HOOK_BEFORE_QUALITY_CHECKS` | `hooks.py` | (nothing) | ❌ INERT |
| `HOOK_BEFORE_CLASSIFY_IMPACT` | `hooks.py` | (nothing) | ❌ INERT |
| `HOOK_BEFORE_DECIDE_ACTION` | `hooks.py` | (nothing) | ❌ INERT |
| `HOOK_BEFORE_NED_REVIEW` | `hooks.py` | (nothing) | ❌ INERT |

**Gap 11 closes 6 channels** (register_impact_rule + 5 hooks).

## Public API Contracts

### 1. Impact Rule Dispatch

Add to `prismatic/review/pipeline.py`:

```python
def apply_impact_rules(
    result: PRReviewResult,
    current_impact: str,
    rules: tuple[ImpactRule, ...],
) -> str:
    """Apply registered impact rules in order; first non-None wins.

    Args:
        result: The PRReviewResult that was classified.
        current_impact: The impact computed by classify_impact().
        rules: Frozen tuple from ComposedReviewerSpec.impact_rules.

    Returns:
        The (possibly overridden) impact string. If no rule returns a
        non-None value, returns current_impact unchanged.
    """
```

### 2. Hook Bus

New module `prismatic/review/hook_bus.py`:

```python
class HookBus:
    """Registry-attached dispatch bus for HOOK_* lifecycle points.

    Hooks are registered against a ReviewerRegistry via the registry's
    existing check/rule channels. The bus resolves the right hook for a
    given lifecycle point and invokes it.
    """

    def __init__(self, registry: ReviewerRegistry) -> None:
        self._registry = registry

    def fire(
        self,
        hook_name: str,
        *,
        args: tuple[Any, ...] = (),
        kwargs: dict[str, Any] | None = None,
    ) -> Any:
        """Fire the named hook with the given args.

        Returns the first non-None return value from any registered handler.
        Returns None if no handler was registered or all returned None.

        Isolation: handlers that raise are caught, logged as a warning,
        and skipped. Hook failure never aborts the calling review.
        """
```

### 3. Hook-to-Registry Channel Mapping

| Hook | Registry channel | Wired into |
|---|---|---|
| `HOOK_BEFORE_SECRET_SCAN` | `register_check()` (first arg = `diff`) | `RealPRReviewer._detect_secrets_with_registry()` |
| `HOOK_BEFORE_QUALITY_CHECKS` | `register_check()` (post-builtins) | `RealPRReviewer.review_pr()` |
| `HOOK_BEFORE_CLASSIFY_IMPACT` | `register_impact_rule()` | `PipelineOrchestrator.process()` (before classify_impact) |
| `HOOK_BEFORE_DECIDE_ACTION` | `register_impact_rule()` (but action-shaped return) | `PipelineOrchestrator.process()` (after classify) |
| `HOOK_BEFORE_NED_REVIEW` | `register_check()` (first arg = `issue dict`) | `trigger_ned_review()` in `prismatic/quality/gates.py` |

**Design choice:** Hooks reuse the existing `register_check()` and `register_impact_rule()` channels. No new registry methods. Plugins that want to participate in a hook just register a check/rule whose return value is interpreted per the hook's contract.

### 4. Docstring Updates

Remove the `.. warning:: Currently inert` from `register_impact_rule()` (PR #43 left it there). Add a single-line "Wired in Gap 11" note.

Remove the `TODO Gap 9 / Part C: wire dispatch in ...` notes from each `HOOK_*` docstring. Replace with `Wired: see prismatic.review.hook_bus.dispatch(HOOK_X, ...)`.

## Files Changed

| File | Change |
|---|---|
| `prismatic/review/pipeline.py` | Add `apply_impact_rules()` function; `PipelineOrchestrator.__init__` accepts `registry` param; `process()` calls `apply_impact_rules` after `classify_impact` |
| `prismatic/review/hook_bus.py` (NEW) | `HookBus` class with `fire()` method |
| `prismatic/review/pr_reviewer_impl.py` | `RealPRReviewer.__init__` already accepts `registry`; add hook firing at 2 points |
| `prismatic/review/registry.py` | Update `register_impact_rule()` docstring (remove warning); add helper method `hooks_for(name)` |
| `prismatic/review/hooks.py` | Update each `HOOK_*` docstring (remove TODO) |
| `prismatic/quality/gates.py` | `trigger_ned_review()` fires `HOOK_BEFORE_NED_REVIEW` before `reviewer.review_pr()` |
| `prismatic/review/test_wire_deferrals.py` (NEW) | 14 test rubrics below |

## Test Rubrics

In `TestApplyImpactRules` (4 tests):

1. `test_no_rules_returns_current_impact` — empty rules, returns input unchanged
2. `test_first_non_none_rule_wins` — rule_a returns None, rule_b returns "blocker", result is "blocker"
3. `test_rules_fire_in_registration_order` — verify order via call log
4. `test_rule_returning_invalid_impact_logs_warning` — defensive: rule returns "nonsense", falls back to current

In `TestHookBus` (4 tests):

5. `test_fire_with_no_handlers_returns_none` — empty registry, no crash
6. `test_fire_calls_all_matching_handlers` — verify all registered handlers invoked
7. `test_fire_returns_first_non_none` — handler A returns None, handler B returns "x", result "x"
8. `test_fire_isolates_handler_exceptions` — broken handler doesn't abort caller

In `TestHookWiring` (6 tests, end-to-end):

9. `test_real_reviewer_fires_before_secret_scan_hook` — register hook, run review, verify hook ran
10. `test_real_reviewer_fires_before_quality_checks_hook` — register hook, verify order: hook → builtins → registry checks
11. `test_pipeline_orchestrator_fires_before_classify_impact` — register hook, run process(), verify it ran
12. `test_pipeline_orchestrator_fires_before_decide_action` — register hook, verify order
13. `test_trigger_ned_review_fires_before_ned_review_hook` — register hook, call trigger, verify fired
14. `test_end_to_end_safety_escalation_rule_changes_verdict` — register an impact rule that escalates warning → major, verify classify_impact() returns "major"

**Total: 14 new tests.**

## Acceptance Criteria

- [ ] `apply_impact_rules()` exported from `prismatic.review`
- [ ] `HookBus` class exported from `prismatic.review`
- [ ] `PipelineOrchestrator(registry=...)` accepts registry param (was missing in PR #41)
- [ ] Each `HOOK_*` constant fires when its trigger condition is met
- [ ] `register_impact_rule()` no longer says "Currently inert" — actually wired
- [ ] Hook failure isolated (warning logged, dispatch continues)
- [ ] 14 new tests pass; 275/275 total (was 261 after Gap 10)
- [ ] Peer review APPROVE

## Carry-Forward

- **End-to-end safety-escalation test** — Gap 14 ships the first real plugin that exercises impact rules
- **Hook filter by phase** — future work
- **Async hook dispatch** — performance track

## Lane Notes

- **Ned lane only.** Pure code change; no infra hookup.
- Single PR expected: PR #47 (Ned).

## Pattern Reference

- `okf/operations/phase2-meta-review-2026-06-28.md` — P0 #2 fix in PR #43 set the contract for honesty about inert channels; this gap honors it
- `okf/operations/gap9-implementation-lessons.md` — Lesson 10 (tests with good coverage can hide dead APIs) — every test in this spec verifies **end-to-end** behavior, not just structural storage

---

*Spec written by Fred (orchestrator) — pending Michael's sign-off before AGY delegation.*
