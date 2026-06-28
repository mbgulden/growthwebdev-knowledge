# Gap 11 Spec — Second-Opinion Design Review

**Reviewer:** Hermes (subagent — independent challenge pass)
**Date:** 2026-06-28
**Source spec:** `okf/operations/gap11-wire-deferrals-spec.md`
**Code base verified at:** `/home/ubuntu/work/prismatic-engine` (HEAD = c69d2167, post-PR-#43)
**Mode:** Adversarial. Goal is to find issues, not approve.

---

## Verdict: REQUEST_CHANGES

The spec closes the right gap and the public-API surface is well-defined, but it inherits a structural blind spot from Gap 9 (Lesson 10 in `gap9-implementation-lessons.md`): the new `apply_impact_rules()` test class repeats the exact "manual dispatch loop in the test body" pattern that hid the inert `register_impact_rule()` channel in the first place. Test #14 — the only one that would actually catch a wiring regression — has insufficient reach (it only verifies `classify_impact` is overridden, not the path that matters: `PipelineOrchestrator.process()` consuming `spec.impact_rules`). The breaking-change rollout for `PipelineOrchestrator(registry=...)` is also under-specified, and the `HookBus.fire()` design has three independent smell classes (reentrancy, args/kwargs polymorphism, attribution). These are fixable, but they must be fixed before Ned starts.

---

### Strengths

- **The P0 gap is correctly identified and the goal statement is honest.** The "Current State" table on lines 22–34 names exactly the 6 inert channels and only the 6. The Goal section is precise — no scope creep beyond what's needed to close P0 #2.
- **Honoring the docstring warning before wiring lands.** The spec calls out removing `.. warning:: Currently inert` from `register_impact_rule()` (line 108) and the `TODO Gap 9 / Part C` notes from each `HOOK_*` (line 110) — this matches Lesson 6's pattern of in-place honest disclosure.
- **Test #14 has the right intent.** "Register an impact rule that escalates warning → major, verify classify_impact() returns 'major'" (line 147) is the kind of end-to-end test Lesson 10 demands. The intent is right; the reach is wrong (see Concern C1 below).
- **Plugin exception isolation carried forward.** The `HookBus.fire()` docstring (lines 89–90) explicitly says handlers that raise are caught + logged + skipped. This matches the existing `RealPRReviewer.review_pr()` check-isolation pattern (lines 518–526 of `pr_reviewer_impl.py`). Good consistency.
- **File-change list is concrete and reviewable.** Seven files, each with a one-line description. No hidden cross-cutting changes.
- **Carry-forward honesty.** "End-to-end safety-escalation test — Gap 14 ships the first real plugin" (line 164) is the right admission that the plugin-real-world path is still untested after this gap.

---

### Concerns (in priority order)

#### C1 — Test #14 still goes through the wrong layer to prove impact rules are operative (severity: HIGH)

**The claim:** "test #14 — register an impact rule that escalates warning → major, verify classify_impact() returns 'major'" (spec line 147).

**The problem:** `classify_impact()` does not consume `spec.impact_rules`. After Gap 11, the call chain that *actually* applies the override will be:

```
PipelineOrchestrator.process() → apply_impact_rules(spec.impact_rules) → mutate `impact` before decide_next_action
```

The spec puts `apply_impact_rules()` after `classify_impact()` in `PipelineOrchestrator.process()` (spec line 116). So:

- A test that asserts `classify_impact(result)` returns `"major"` proves **only that the rule's body returns `"major"`**. It does **not** prove `PipelineOrchestrator.process()` calls `apply_impact_rules()`. A Ned reviewer who wires `apply_impact_rules()` into a dead function and forgets to call it from `process()` would pass test #14 with flying colors.
- This is precisely the failure mode Lesson 10 documents: lines 137–159 of `test_registry.py` already do the manual-loop dance (`for rule in spec.impact_rules: new = rule(None, current); if new is not None: current = new; break`) and the tests pass even though the production path is inert.
- Test #14 should instead assert: **construct a `PipelineOrchestrator(registry=registry_with_rule)`, call `process(identifier, pr_url, result)`, and assert `decision.impact == "major"` AND `decision.rationale` mentions the rule**.

#### C2 — Test #11 and #12 are structurally weaker than they look (severity: HIGH)

**The spec says** (lines 144–145): "register hook, run process(), verify it ran" and "register hook, verify order."

**The problem:** "verify it ran" is too loose a contract. With `HookBus.fire(args=(result,))`, a hook that does nothing observable (e.g. `lambda result: None`) makes "it ran" hard to distinguish from "no hook was registered at all" without an explicit side-effect assertion. The test needs to:
1. Set a flag in the hook body (`calls.append("before_classify")`)
2. Assert the flag was set after `process()` returned
3. AND — to prevent silent silent-skipping — register a rule that mutates `impact` and assert the mutation flowed through

The third check is what makes the test meaningful. Without it, you can ship a hook bus that registers but never fires and all 6 end-to-end tests pass.

#### C3 — Breaking-change rollout is under-specified (severity: HIGH)

**Spec line 116** says: `PipelineOrchestrator.__init__` accepts `registry` param.

**The questions not answered:**

1. **Is `registry` required, optional, or optional-with-sentinel-default?** Required = breaking change for every existing caller. Optional (default `None`) = no migration path for callers who want the wiring but accidentally omit it (silently inert — exactly the P0 #2 anti-pattern this gap exists to prevent).
2. **What happens if `registry=None` and the user calls `process()`?** Two reasonable choices:
   - Reject with `TypeError("PipelineOrchestrator requires a registry to apply impact rules")` — loud failure; conservative.
   - Silently skip `apply_impact_rules()` — backwards compatible; re-creates the "code-complete but inert" trap.
   The spec should pick one and say so explicitly. Lesson 10's anti-pattern argues for option 1 in the wired branch with a deprecation warning.
3. **What's the migration path for existing callers?** At minimum: a one-liner in the spec saying "all internal callers in this PR are updated; external callers (none exist yet per Gap 10's plugin auto-discovery status) get a `DeprecationWarning` if they pass no registry." Without this, the breaking change ships as a surprise.

#### C4 — `HookBus.fire()` reentrancy / hook-mutation invariants are unspecified (severity: HIGH)

**Spec lines 77–91** describe `HookBus.fire(hook_name, *, args=(), kwargs=None)`. Three issues:

1. **What if a handler registers/unregisters another handler mid-fire?** The spec does not say whether `fire()` iterates over a static snapshot or the live handler list. With Python 3.12+ dict ordering guarantees, iterating the live list and mutating during iteration raises `RuntimeError: dictionary changed size during iteration`. With older versions, the result is "undefined." The spec needs to specify either "handlers see a frozen snapshot" or "registering during fire is undefined behavior."

2. **What if a hook returns a non-string verdict?** Spec line 132 says test #4 covers "rule returns 'nonsense', falls back to current." But the fallback path for a non-string is not specified — does `apply_impact_rules()` type-check the return? If not, the verdict field becomes a malformed object and downstream `IMPACT_RANK` lookup raises `KeyError` (lines 50–55 of `pipeline.py`). If yes, what's the validation function?

3. **`args/kwargs` polymorphism is a smell.** Each hook has a different signature (line 102: `diff` vs `result` vs `(result, attempts)` vs `issue dict`). Using `*args`/`**kwargs` discards the type information the registry could provide. The spec should declare a per-hook signature table or use a single-`dict` payload (`fire(HOOK_BEFORE_DECIDE_ACTION, payload={"result": r, "attempts": n})`). The current design means a hook for `HOOK_BEFORE_DECIDE_ACTION` will silently receive the wrong positional args if the spec author misorders them — and no test catches this because each test #9–#13 only registers one hook per lifecycle point.

#### C5 — Concurrent invocation under shared `HookBus` is unspecified (severity: MEDIUM)

**Spec lines 18** explicitly defers "Async/threaded hook dispatch" to future work and says "performance is fine."

**The question this dodges:** `PipelineOrchestrator.process()` already holds a lock across its full body (lines 331–357 of `pipeline.py`). If `apply_impact_rules()` is called *inside* that lock, the hook handlers fire under the lock too — meaning a slow or blocking handler (e.g. an HTTP call to a remote impact-classifier) serializes every concurrent `process()` call. The spec must say:
- Hook dispatch happens inside or outside the orchestrator lock?
- If outside, what's the reentrancy story for `record_rework()` after `apply_impact_rules`?
- If inside, what's the documented SLA per handler call?

Without this, a plugin that does `import requests; requests.post(...)` in an impact rule will block the factory's rework-dispatch path for every concurrent PR.

#### C6 — `HookBus` does not currently enforce naming, and `hooks_for()` is underspecified (severity: MEDIUM)

**Spec line 119** says: "Update `register_impact_rule()` docstring; add helper method `hooks_for(name)`."

**The questions:**
- What does `hooks_for(name)` return? A list of callables filtered by name?
- What attribute on the registered check/rule stores the hook name?
- Today, `register_check(fn, *, name=None)` (registry.py line 136) does not have a `hook` parameter. So how does the bus know which checks to fire on which hook? Two options:
  - Add a `hook=HOOK_X` parameter to `register_check()` — but that conflates "check" with "hook handler."
  - Use a dedicated `register_hook(name, fn)` method — cleaner but contradicts spec line 104: "Hooks reuse the existing `register_check()` and `register_impact_rule()` channels. No new registry methods."

The spec contradicts itself. Either you add `register_hook()` (clean) or you overload `register_check()` (convoluted but matches spec). The mapping table on lines 96–102 does not actually show how a registered check's *hook name* is preserved — only what its *positional arg signature* is. This needs to be resolved.

#### C7 — Missing tests for invariants listed in the task brief (severity: MEDIUM)

The task brief asks about:
1. **Performance under load (100 impact rules fire)** — no test. The current `apply_impact_rules()` is a linear scan; with 100 rules each doing a small dict lookup, that's still microseconds, but the spec makes no claim about scalability and no test enforces it.
2. **Type safety (hook returns non-string verdict)** — test #4 covers "nonsense" string but not `42` or `["major"]` or `None` from a hook that promised a verdict. The `apply_impact_rules()` docstring says "first non-None wins" (line 56) but the test only covers None, not other non-string falsy/truthy returns.
3. **Dedup (same hook registered 50 times)** — no test. Today `register_check(fn, name=None)` (registry.py line 144) appends to `_unnamed_checks` with no dedup. So if a plugin's `register()` function is called twice (e.g. entry-point runs both `prismatic.plugins` group and a manual `registry.register(plugin.register)`), the same hook fires twice. No test, no documentation, no enforcement.

#### C8 — Order of operations: some channels are independent, some are coupled (severity: MEDIUM)

**Spec lines 96–102** map 6 hooks to 4 call sites. The wiring can land in this order:
- `HOOK_BEFORE_SECRET_SCAN` + `HOOK_BEFORE_QUALITY_CHECKS` → inside `RealPRReviewer.review_pr()` and `_detect_secrets_with_registry()` — independent of each other and of any registry-channel work.
- `HOOK_BEFORE_CLASSIFY_IMPACT` + `HOOK_BEFORE_DECIDE_ACTION` → inside `PipelineOrchestrator.process()` — requires the new `registry` param first.
- `HOOK_BEFORE_NED_REVIEW` → inside `trigger_ned_review()` — independent of registry but needs `HookBus` to exist.
- `apply_impact_rules()` → inside `PipelineOrchestrator.process()` — coupled to the `registry` param.

**The dependency:** `register_impact_rule()` *channel* (rule storage, already wired) vs `apply_impact_rules()` *function* (new code) vs `PipelineOrchestrator.process()` *call site* (new code). The tests for rules (TestApplyImpactRules 1–4) are independent of the orchestrator wiring. The tests for orchestrator wiring (TestHookWiring 11–12) depend on the `registry` param existing.

**Recommendation:** Land in three PRs or one PR with explicit commit ordering: (a) `apply_impact_rules()` function + tests 1–4, (b) `PipelineOrchestrator(registry=...)` + hook wiring + tests 11–12, (c) reviewer + trigger hook wiring + tests 9–10 + 13–14. The spec should specify this ordering or the test sequencing will be brittle.

#### C9 — `apply_impact_rules()` API surface has a redundant parameter (severity: LOW)

**Spec line 43–48:**
```python
def apply_impact_rules(
    result: PRReviewResult,
    current_impact: str,
    rules: tuple[ImpactRule, ...],
) -> str:
```

`rules` is the third arg but the spec also says `PipelineOrchestrator.process()` will pass `spec.impact_rules` (line 116). The orchestrator already has `self._registry` after the new `registry` param; passing `rules` separately means the caller is responsible for re-snapshotting the registry. Two cleaner options:
- Make `apply_impact_rules(result, current_impact, registry)` and call `registry.compose()` inside — but this re-composes per call, defeating the frozen-snapshot pattern from Lesson 5.
- Pass `(result, current_impact, spec)` — `spec` is already a frozen snapshot, so `apply_impact_rules` reads `spec.impact_rules`. The function name stays accurate; the caller passes fewer args.

The current design works but the `rules` parameter duplicates information the registry already provides.

#### C10 — Spec does not list regression-guard tests for the docstring changes (severity: LOW)

Per Gap 9 Lesson 9 ("per-PR review != meta-review"), the spec removes "Currently inert" warnings. There's no `test_register_impact_rule_docstring_does_not_warn_inert` test to prevent a future PR from re-introducing the warning language in a stale form (e.g. "Wired in Gap 11" with no actual wiring). PR #43 added `test_register_impact_rule_docstring_warns` (gap9-implementation-lessons.md line 129); the inverse test should be added now.

#### C11 — Naming consistency (severity: LOW)

`HookBus` (spec line 66) implies pub/sub semantics; the actual design is "fire all handlers, return first non-None." That's more like a `HookDispatcher` (pub/sub with priority-return) or a `HookResolver` (lookup-then-invoke). `HookBus` is fine for marketing but slightly misleading — readers expecting pub/sub semantics may misread "first non-None" as "all returned values merged." Suggest `HookDispatcher` in the docstring or a clarifying line.

---

### Recommended spec changes

1. **Replace test #14 with an end-to-end orchestrator assertion.** Register an impact rule via `ReviewerRegistry`, construct `PipelineOrchestrator(registry=registry)`, call `process(identifier, pr_url, result)`, assert `decision.impact == "major"`. Drop the bare `classify_impact()` assertion — it tests the rule, not the wiring. **(Addresses C1.)**
2. **Strengthen tests #11 and #12 to require observable side-effects AND mutation-through.** Both tests should (a) set a flag inside the hook body to prove it ran, and (b) register a rule whose return value flows into the orchestrator's decision. The flag-only assertion is too weak. **(Addresses C2.)**
3. **Add a "Migration & Default Semantics" section.** Specify: `registry` parameter is **required** (no default). Internal callers in this PR are updated. External callers (none exist) will get a `TypeError` if they pass no registry, not a silent skip. Document the deprecation policy. **(Addresses C3.)**
4. **Specify the per-hook signature contract.** Either:
   - Use a single-dict payload: `fire(name, payload={"diff": ..., "result": ..., "attempts": ..., "issue": ...})`, OR
   - Declare a per-hook arg list at module level (e.g. `HOOK_SIGNATURES = {HOOK_BEFORE_DECIDE_ACTION: ("result", "attempts"), ...}`) and validate at fire-time.
   Pick one. The current `*args` design is unsafe. **(Addresses C4.)**
5. **Specify reentrancy semantics.** "Handlers may register or unregister other handlers during fire, but those mutations take effect on the next call to `fire()`. The current invocation iterates a static snapshot of handlers." One-line addition to the `HookBus.fire()` docstring. **(Addresses C4, C5.)**
6. **Resolve the `hooks_for(name)` design contradiction.** Either:
   - Add `register_hook(name, fn)` as a new registry method (cleaner, breaks spec line 104's "no new registry methods" promise), OR
   - Extend `register_check(fn, *, name=None, hook=None)` to carry an optional `hook` discriminator (matches the existing API surface).
   Pick one and update spec lines 104 and 119 consistently. **(Addresses C6.)**
7. **Add three missing tests:**
   - `test_apply_impact_rules_handles_100_rules` — performance guard, asserts <100ms.
   - `test_hook_returning_non_string_verdict_logs_warning` — covers `42`, `["major"]`, and `None`-from-promise paths.
   - `test_same_check_registered_twice_fires_twice` (or test the inverse — explicit dedup) — codifies the current append-without-dedup behavior of `_unnamed_checks`.
   **(Addresses C7.)**
8. **Specify commit ordering.** Section "Files Changed" should specify the three-commit structure (apply_impact_rules + tests → PipelineOrchestrator(registry=...) + orchestrator hook wiring → reviewer/trigger hook wiring) or guarantee that the PR is mergeable in any commit order. **(Addresses C8.)**
9. **Update `apply_impact_rules()` signature.** Pass `spec: ComposedReviewerSpec` instead of `rules: tuple[ImpactRule, ...]`. Reduces caller error surface and matches the frozen-snapshot contract. **(Addresses C9.)**
10. **Add `test_register_impact_rule_docstring_no_longer_warns_inert`** as a regression guard for the docstring change. **(Addresses C10.)**
11. **Specify hook-dispatch lock semantics.** "Hook handlers fire under the orchestrator's `_lock` for `HOOK_BEFORE_CLASSIFY_IMPACT` and `HOOK_BEFORE_DECIDE_ACTION`. Handlers must complete in <100ms or risk factory rework-dispatch starvation." Add this to non-goals or acceptance criteria. **(Addresses C5.)**

---

### Open questions for Michael

1. **`PipelineOrchestrator(registry=...)` default:** required-with-no-default, required-with-None-rejected, or optional-with-warning? Lesson 10 argues for the loudest failure mode. Existing callers in the test suite (e.g. line 286 of `pipeline.py`'s example: `PipelineOrchestrator()`) would all need to update. Is that acceptable for an internal-class API, or do we want backwards compatibility?
2. **Hook payload shape:** dict-payload vs per-hook positional args vs namespaced Protocol types? The current `*args/**kwargs` design will cause silent misordering bugs the first time someone wires two hooks to the same lifecycle point.
3. **`hooks_for(name)` mechanism:** does it filter `register_check(fn, name="x")` by some new `hook=HOOK_Y` parameter, or by a tag on the function, or by a separate `register_hook()` registry method? Spec lines 104 and 119 disagree.
4. **Lock scope for hook handlers:** is it acceptable for a slow plugin handler to serialize concurrent `process()` calls inside `PipelineOrchestrator._lock`? If not, what is the SLA per handler and how is it enforced?
5. **Performance guard:** is "<100ms for 100 rules" the right bar, or should the spec commit to a lower number? The current spec is silent on performance.
6. **Test sequencing:** are tests 1–4 (apply_impact_rules) allowed to pass without tests 11–12 (PipelineOrchestrator wiring) passing? If yes, the spec splits naturally into 3 commits; if no, all 14 must land atomically and the PR size balloons.
7. **QualityCheck missing:** the spec doesn't address the meta-review's P0 #1 carry-forward (`QualityCheck` was fixed in PR #43; the spec should not regress it). Is there an acceptance criterion for "QualityCheck still importable from prismatic.review"?
8. **`register_check()` named-key dedup vs `register_impact_rule()` no-dedup:** today, `register_check(fn, name="x")` replaces existing; `register_impact_rule(fn)` appends with no dedup. Is that asymmetry intentional, or should both rules and checks dedup on identity? Test #14 would behave differently under each.

---

### Evidence trail

- **Inert `register_impact_rule()` confirmed live:** `grep -rn "spec.impact_rules\|impact_rule" prismatic/ | grep -v test_ | grep -v registry.py` returns zero hits in non-test code (matches meta-review claim).
- **Test-registry Lesson 10 anti-pattern confirmed:** `test_registry.py` lines 137–159 manually iterate `spec.impact_rules` to assert dispatch order — exactly the dead-API-hiding pattern Lesson 10 names.
- **`PipelineOrchestrator` lacks `registry` param confirmed:** `pipeline.py` line 291 `__init__` takes only `max_rework_attempts`. Spec's claim is accurate.
- **Orchestrator already holds lock across full body:** `pipeline.py` lines 331–357. Hook-dispatch-in-lock concern (C5) is concrete.
- **`register_check()` already wired in `RealPRReviewer`:** `pr_reviewer_impl.py` line 513 (`for check in spec.checks: try: extra = check(diff)`). Spec's "Already wired" claim is accurate.
- **Test files pre-PR-47 don't exist:** `prismatic/review/` has `test_pipeline.py`, `test_pr_reviewer_impl.py`, `test_registry.py` but no `test_wire_deferrals.py` — confirmed Gap 11 has not landed.
- **Public exports already complete (post-PR-#43):** `prismatic/review/__init__.py` lines 48–62 export `ImpactRule`, `QualityCheck`, `ReviewerRegistry`, all 5 `HOOK_*`. Spec line 153–155 acceptance criteria are partially pre-satisfied for the symbols but not for the wiring.

---

*Review written by Hermes subagent (second-opinion pass). Spec at /home/ubuntu/work/growthwebdev-knowledge/okf/operations/gap11-wire-deferrals-spec.md. Code verified at /home/ubuntu/work/prismatic-engine @ c69d2167.*