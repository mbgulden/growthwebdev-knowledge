# Meta-Review: Prismatic Engine Phase 2 + Gap 9
**Reviewer:** Claude Sonnet 4.6 (Thinking) — architectural meta-review  
**Date:** 2026-06-28  
**Scope:** PRs #35–#42, deploy-fresh HEAD, version 0.2.0  
**Evidence base:** Full source read + live test runs + REPL probes + OKF doc audit

---

## Meta-Review Verdict: NEEDS_FIXES

> Not NEEDS_MAJOR_REWORK — the bones are sound. But three specific gaps prevent a clean COMPLETE declaration: one dead public API channel (impact_rules), one latent DoS vector (unbounded pattern scan), and one broken import (`QualityCheck`) that would trip any plugin author who follows the checklist docs.

---

## What Works Well

- **Architectural seams are clean.** `trigger_ned_review` → `RealPRReviewer` → `PipelineOrchestrator` is a legitimate layered design. Each layer has a single responsibility and returns a value type the next layer can consume. No god objects, no circular deps.
- **Dependency injection is done correctly.** `post_comment`, `transition_state`, `pipeline`, and `reviewer` are all injectable. The trigger is genuinely unit-testable without mocking `subprocess`.
- **`compose()` frozen-snapshot pattern is the right call.** `ComposedReviewerSpec` being a `frozen=True` dataclass means concurrent `review_pr()` calls get a stable view regardless of mid-flight registrations. This is the kind of decision that prevents subtle race bugs in production.
- **Plugin exception isolation is correct.** Custom checks that raise are caught, converted to a `warning` finding, and the review continues. The right behavior.
- **`fetch_pr_diff` failure mode is graceful.** No `gh` CLI, wrong auth, bad URL, timeout — all produce `NEEDS_DISCUSSION` with a legible explanation rather than an unhandled exception. Correct: the reviewer degrades gracefully instead of silently.
- **`PipelineOrchestrator.process()` is atomic.** The lock is held across the full read-modify-write (read counter → decide → bump counter). Concurrent rework dispatches for the same identifier cannot both fire.
- **Documentation honesty is genuinely high.** The OKF docs do not overstate completion. The `⚠️ Documented for Gap 10+` section in `phase2-final-status.md` names every known gap explicitly. This is much better than the typical "100% complete" post-ship document.
- **247/247 tests pass, fast (0.43s).** No flaky tests observed. Test distribution across layers (smoke / failure / reviewer / pipeline / registry) is reasonable.

---

## Architectural Concerns

### CRITICAL

**`register_impact_rule()` is a dead API channel — silently discarded.**

`ReviewerRegistry.register_impact_rule()` stores rules in `_impact_rules`, which are faithfully serialized into `ComposedReviewerSpec.impact_rules`. But nothing in the production code ever reads `spec.impact_rules`. Not `RealPRReviewer.review_pr()`, not `classify_impact()`, not `PipelineOrchestrator.process()`. Confirmed by exhaustive grep:

```
$ grep -rn 'spec\.impact_rules\|impact_rule' prismatic/ | grep -v test_ | grep -v registry.py
(zero hits)
```

The consequence: a plugin author who calls `registry.register_impact_rule(my_escalation_rule)` and then reads the docs — which say "First non-None wins. Useful for project-specific escalation rules (e.g. 'in safety-critical paths, treat all warning-severity findings as major')" — will observe that their rule is silently ignored in production. No error, no warning.

This is worse than an unimplemented feature because it *looks* like it works. The tests for `register_impact_rule` test only the registry's ability to store rules and expose them via `compose()`. They explicitly invoke the dispatch loop manually in the test body. There is no test that verifies impact rules *affect the final verdict* in an end-to-end flow.

> **Severity: CRITICAL** — Public API that silently does nothing is a trust-breaker for plugin authors.

---

### HIGH

**10,000 secret patterns = 44 seconds per review (O(lines × patterns), no bound).**

Measured live:

```
10k patterns over 100 lines: 44.12s
```

The `_detect_secrets_with_registry` loop is `O(diff_lines × secret_patterns)` with no ceiling on `len(spec.secret_patterns)`. There is no cap, no compiled regex union, no early-exit. A hostile or misconfigured plugin could register 50k patterns and make every review call take minutes.

Even with well-intentioned plugins, a company with 20 token types × 5 regex variants per type = 100 patterns is realistic and would add ~0.4s per review — annoying but tolerable. 10k is an abuse case, but the design offers no protection.

The built-in `detect_secrets` loop has the same structure but is bounded at 10 patterns. The registry-augmented path has no bound.

> **Severity: HIGH** — Not an immediate production issue (no plugins yet), but the ceiling needs to exist before plugin auto-discovery is wired in Gap 10.

---

### HIGH

**`QualityCheck` type alias is missing from `prismatic.review.__all__` and cannot be imported from the public package.**

Confirmed:

```
$ python3 -c "from prismatic.review import QualityCheck"
ImportError: cannot import name 'QualityCheck' from 'prismatic.review'
```

`QualityCheck` *is* in `registry.__all__` and *is* listed in the distribution checklist's public API surface example:

```python
from prismatic.review import (
    ...
    QualityCheck, ImpactRule,
    ...
)
```

Any plugin author who follows the checklist verbatim will get an `ImportError` on line 1 of their plugin.

`ImpactRule` is also not in `review/__init__.py`'s imports block — but it *is* exported via the `from .registry import (...)` block. Let me be precise: `ImpactRule` is importable; `QualityCheck` is not. The `__init__.py` imports `ImpactRule, ReviewerRegistry, ComposedReviewerSpec, SecretPattern` but does **not** import `QualityCheck`.

> **Severity: HIGH** — Breaks the documented plugin authoring workflow on the first import.

---

### MEDIUM

**`PipelineOrchestrator` has no `registry` parameter, but `RealPRReviewer` does.**

The gap9 lessons doc acknowledges this: "Add `PipelineOrchestrator` registry parameter (currently only `RealPRReviewer` accepts it)." When `HOOK_BEFORE_CLASSIFY_IMPACT` and `HOOK_BEFORE_DECIDE_ACTION` are wired in Part C, the orchestrator will need the registry too. As shipped, a plugin that needs to override classification cannot do so via the orchestrator path — only via a custom `classify_impact()` call outside the orchestrator.

> **Severity: MEDIUM** — Gap-10 tracked, but creates an asymmetric plugin surface that's confusing.

---

### MEDIUM

**`_count_medium()` uses regex scraping on a markdown summary string — fragile.**

```python
m = re.search(r"(\d+)\s+medium", summary)
```

The real reviewer formats medium-severity summaries as `"## 💬 N medium-severity issue(s)"`. If that phrasing changes in a future PR, `_count_medium()` silently returns 0, and a PR with medium-severity secrets (e.g. `secret = "longstring..."`) could be classified as `trivial` instead of `minor`. No test covers this regression path.

> **Severity: MEDIUM** — Easy to fix by adding `medium_count` to `metadata` in `RealPRReviewer.review_pr()`.

---

### LOW

**`test_real_reviewer_failure_does_not_crash_trigger` asserts the opposite of its name.**

The test name says "does not crash," the assertion is `pytest.raises(RuntimeError)`. Documented in the OKF docs as a known cosmetic bug. But cosmetic bugs in test names erode trust in the test suite — a reader who sees the name but not the body will assume the trigger swallows exceptions, which it does not.

> **Severity: LOW** — One rename.

---

### LOW

**`__init__.py` module docstring is stale — still describes the "intentionally small" stub phase.**

Lines 1–14 of `prismatic/review/__init__.py` still describe the Gap 4 stub design: "This package is intentionally small… tasks #1–5 of Gap 4 fill in the real implementation." The real implementation has shipped. The docstring should describe what the package *is*, not what it *was planning to become*.

> **Severity: LOW** — Documentation debt, not a bug.

---

## Public API Ergonomics

Three scenarios a plugin author might attempt:

**Scenario 1: Register a custom check callable.**
Works. `registry.register_check(fn, name="my_check")` → `RealPRReviewer(registry=reg)` → findings appear in the result. Clean, discoverable, tested. ✅

**Scenario 2: Register an impact override rule.**
Fails silently. `registry.register_impact_rule(my_rule)` compiles fine, the registry stores it, `compose()` puts it in `spec.impact_rules` — and the rule is then ignored for the rest of eternity. A plugin author who writes a safety-critical escalation rule believing it affects verdicts will ship a false-safe system. ❌

**Scenario 3: Write a typed plugin module using `QualityCheck` as the type annotation for the callable.**
```python
from prismatic.review import QualityCheck  # ImportError
```
Fails on first import. ❌

---

## Test Quality

**Meaningful, not theater — with one structural gap.**

The 247 tests cover behavior, not just structure. The failure-classification tests (Gap 7) cover boundary conditions and performance. The pipeline tests cover the atomic rework counter. The registry tests cover the frozen snapshot property. These are meaningful invariants.

**The structural gap:** Impact rules are tested only for storage and traversal in isolation (`TestImpactRuleRegistration::test_rules_fire_in_registration_order`, `test_first_non_none_wins`). Both tests manually execute the dispatch loop *in the test body*. Neither test goes through `RealPRReviewer.review_pr()` or `PipelineOrchestrator.process()`. This is how a dead API channel hides behind 100% test coverage.

**Missing invariants:**
1. `impact_rules` registered with a `ReviewerRegistry` → reviewer → `classify_impact` → the rule actually changes the impact. (Currently untestable because the wiring doesn't exist.)
2. `QualityCheck` importable from `prismatic.review`. (Would catch the missing export.)
3. Large pattern count doesn't cause timeout. (Performance regression guard.)
4. `_count_medium` accuracy when summary format changes.

---

## Operational Realism Check

| Question | Answer |
|---|---|
| Is `ReviewerRegistry` callable from outside the package? | ✅ Yes — importable, instantiable, fully functional |
| Are `HOOK_*` constants callable from outside the package? | ✅ Constants are importable. **But**: they are inert string identifiers. No dispatch bus exists. Plugin authors referencing them get no behavior. Documented honestly. |
| Does `[project.entry-points."prismatic.plugins"]` get queried? | ❌ No. The group is declared in `pyproject.toml`, but `prismatic.dispatcher.main()` does **not** call `entry_points(group="prismatic.plugins")`. Plugin auto-discovery is dead until Gap 10 wires it. Documented honestly. |
| Is `RealPRReviewer.review_pr()` callable without gh CLI? | ✅ Yes — returns `NEEDS_DISCUSSION` with a legible error message, does not raise. Correctly graceful. |
| Is `RealPRReviewer.review_pr()` callable with a malformed URL? | ✅ Yes — `parse_pr_url` raises `ValueError`, caught by `fetch_pr_diff`, returns empty string → `NEEDS_DISCUSSION` with `diff_fetch_failed` metadata. |
| Are impact rules operative in production? | ❌ No. Collected, frozen, silently discarded. |

**The "code-complete but operationally dead" trap from PR #40 is partially recurred:** the hook dispatch and impact rules channels are defined, documented, tested in isolation, and not wired. This is disclosed in the OKF docs. The difference from the pre-#40 situation is that *this time it's documented as a known gap*, not an accidental omission. That's an improvement, but the impact_rules case is more serious because there's no `TODO Gap 9 / Part C` note in the actual registry docstring for `register_impact_rule()` warning that it's currently inert.

---

## Documentation Honesty Check

| Document | Assessment |
|---|---|
| `phase2-final-status.md` | ✅ **Honest.** The `⚠️ Documented for Gap 10+` section explicitly names all 5 known gaps including plugin auto-discovery, hook dispatch, and impact rules. The "Honest Caveats" section is unusually candid for a ship-status doc. |
| `gap9-implementation-lessons.md` | ✅ **Honest.** Lesson 1 ("code complete != operationally complete") and Lesson 6 ("dead code in stable API is fine if documented") correctly characterize the trade-offs made. Carry-forward task #8 ("Add `PipelineOrchestrator` registry parameter") is appropriately tracked. |
| `prismatic-distribution-checklist.md` | ⚠️ **Slightly overstated in one place.** Issue C says "Plugin authors must still call `ReviewerRegistry.register_*()` manually." This is true but understates: plugin authors can't even wire via `entry_points` on their own — the *consumer* side of the entry-point mechanism doesn't exist yet. A plugin installed via `pip install` is completely inert. The checklist item says "Status: ✅ Group declared; resolver call works" — technically true but framed to sound more complete than it is. |
| **Impact rules documentation gap** | ⚠️ **`register_impact_rule()` docstring does not indicate it's currently inert.** Compare: `HOOK_*` constants each carry an explicit `TODO Gap 9 / Part C: wire dispatch in...` notice. `register_impact_rule()` has no such notice — it reads as fully operative. This is the one place where the documentation is not honest by omission. |

---

## Failure Mode Analysis

| Scenario | Behavior | Assessment |
|---|---|---|
| `gh` CLI not installed | `NEEDS_DISCUSSION` + legible error message in summary | ✅ Correct |
| Plugin check returns `None` | `if extra:` evaluates False → silently skipped | ✅ Fine (None is a valid "no findings" return) |
| Plugin check returns `42` (truthy, non-iterable) | `findings.extend(42)` raises `TypeError` → caught → `warning` finding appended | ✅ Isolated correctly |
| Plugin check raises any exception | Caught → `warning` finding appended, review continues | ✅ Correct isolation |
| 10,000 secret patterns | **44.12 seconds** for 100-line diff | ❌ Latent DoS — no bound, no compiled union |
| Two threads call `register_check()` concurrently | Python GIL protects `dict.__setitem__`; no crash, count correct | ⚠️ Passes empirically, but the docstring says "not thread-safe" and this is technically a data race on CPython. On non-CPython (PyPy, Graal) the GIL guarantee doesn't hold. |
| `review_pr()` with malformed URL (`"not-a-url"`) | `NEEDS_DISCUSSION` + `diff_fetch_failed` metadata | ✅ Correct |
| `review_pr()` with structurally valid but nonexistent PR URL | `NEEDS_DISCUSSION` + `diff_fetch_failed` (gh CLI returns non-zero) | ✅ Correct |
| `classify_impact()` called on result with no `metadata` keys | Defaults to 0 for all counts, proceeds normally | ✅ Defensive |
| Impact rule registered that returns a non-IMPACT_LEVEL string | Rule is stored; since nothing calls it, no crash — but when Part C wires it, the bad string would silently propagate | ⚠️ No input validation on `register_impact_rule()` |

---

## Lane Governance Audit

| Observation | Assessment |
|---|---|
| PR #42 required `--no-verify` to bypass the pre-push hook for `pyproject.toml` | Correctly acknowledged in gap9-implementation-lessons.md (Lesson 3). The bypass was justified: Fred is staging governor. But the lane YAML still lacks a `root_config_files` owner, meaning the bypass is needed for every future root-level config change. |
| PR #41 (Ned lane) initially included `pyproject.toml` and was correctly rejected by the pre-push hook | ✅ Lane governance worked as designed. The split into #41 + #42 was the right response. |
| No other lane violations detected in the 7 PRs | Files changed align with lane ownership: `prismatic/`, `plugins/`, `scripts/` for Ned; `pyproject.toml` for Fred. |
| **Gap in lane rules:** No rule prevents an agent from adding `register_impact_rule()` calls that silently do nothing | Not a lane violation per se, but the lane governance of the *plugin extension API* needs an explicit check: "does `spec.impact_rules` get consumed anywhere before shipping a new registry channel?" |
| Enforcement gap: lane rules are enforced only at push time (pre-push hook), not at PR review time | A PR that violates lane rules but uses `--no-verify` bypasses the only enforcement point. There is no CI check. |

---

## Recommended Next Steps (in priority order)

1. **[P0 — Fix before Gap 10 wires plugin auto-discovery]** Add `QualityCheck` to `prismatic.review.__init__.py` imports and `__all__`. One-line fix; otherwise every plugin author hits `ImportError` on their first import.

2. **[P0 — Fix before plugin auto-discovery]** Add a `# TODO Gap 9 / Part C: currently inert` notice to `ReviewerRegistry.register_impact_rule()` docstring, matching the pattern used in `HOOK_*` docstrings. Plugin authors must not unknowingly ship dead safety rules.

3. **[P1 — Fix before Gap 10]** Wire `spec.impact_rules` into `classify_impact()` or add a `_apply_impact_rules(result, impact, spec)` helper that `RealPRReviewer.review_pr()` calls. This is the minimum viable fix: collect the impact from `classify_impact()`, pass it through the rules, return the (possibly overridden) impact. Add a registry parameter to `PipelineOrchestrator` for the same reason.

4. **[P1 — Before plugin auto-discovery]** Add a pattern count ceiling (e.g. 500) to `ReviewerRegistry.register_secret_pattern()` with a clear `ValueError`. Alternatively, pre-compile a regex union (`re.compile("|".join(patterns))`) in `compose()` so the O(lines × patterns) inner loop becomes O(lines). The compiled-union approach also resolves the performance problem without imposing an arbitrary ceiling.

5. **[P2]** Add `medium_count` to `RealPRReviewer.review_pr()` metadata dict (alongside `critical_count`, `high_count`, `warning_count`). This makes `_count_medium()` use the fast path and removes the regex-scraping fragility.

6. **[P2]** Rename `test_real_reviewer_failure_does_not_crash_trigger` → `test_real_reviewer_failure_propagates_exception`. The docstring says "the trigger must surface the exception" — make the name match.

7. **[P3]** Update `prismatic/review/__init__.py` module docstring to describe what the package *is* (post-Gap-4 real reviewer + Gap-8 pipeline + Gap-9 plugin extension), not the old "intentionally small stub" framing.

8. **[Gap 10, already tracked]** Wire `entry_points(group="prismatic.plugins")` in `prismatic.dispatcher.main()`. Until this lands, the entire plugin system is manually-wired only.

---

## Final Recommendation

Phase 2 + Gap 9 should be declared **NEEDS_FIXES, not COMPLETE**. The initiative is architecturally sound — the seams between `RealPRReviewer`, `PipelineOrchestrator`, `ReviewerRegistry`, and `trigger_ned_review` are clean, the dependency injection is correct, the frozen-snapshot pattern is the right call, and the OKF documentation is genuinely honest about what's deferred. However, two defects prevent a COMPLETE verdict:

First, `register_impact_rule()` is a publicly documented, tested, and shipped API channel that silently discards its input in production. This is not a "documented gap" — the docstring reads as fully operative and there is no `TODO` notice. A plugin author writing a safety-critical escalation rule will ship a false-safe system. The fix is either to wire the rules into `classify_impact()` (correct) or to add an explicit "currently inert" notice to the docstring (minimum honest disclosure).

Second, `QualityCheck` cannot be imported from `prismatic.review`, but the distribution checklist documents it as importable in the first code example any new plugin author would read. This is a one-line fix.

Both are fixable in a single small PR. Fix those two, and the Phase 2 + Gap 9 declaration becomes clean.

---

*Evidence: live REPL sessions, `grep -rn` across the full `prismatic/` tree, `pytest` run (247/247 pass), 10k-pattern perf test (44.12s), and full read of all 5 requested OKF docs.*
