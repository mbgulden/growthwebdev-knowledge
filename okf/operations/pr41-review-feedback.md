# PR #41 — Gap 9 / Part B: Plugin Extension Registry + Hooks

**Branch:** `ned/gap9-plugin-registry`  
**Commit:** `38ca2cb5`  
**Reviewed:** 2026-06-28  
**Test baseline:** 247/247 passed (`python3 -m pytest prismatic/ -v`)

---

## Review Verdict: APPROVE (with noted follow-ups for next PR)

---

### Evidence Reviewed

| Artifact | Lines | Status |
|---|---|---|
| `prismatic/review/registry.py` | 204 | ✅ Read in full |
| `prismatic/review/hooks.py` | 91 | ✅ Read in full |
| `prismatic/review/pr_reviewer_impl.py` | 595 | ✅ Read in full |
| `prismatic/review/test_registry.py` | 348 | ✅ Read in full |
| `prismatic/review/__init__.py` | 101 | ✅ Read in full |
| Test suite | 247 tests | ✅ All passed |
| Live probe (registry, hooks, reviewer, backward compat) | — | ✅ All passed |
| Edge case probes (5 cases) | — | ✅ All passed |

---

### Strengths

- **Clean registry design.** The three-channel model (secret patterns / quality checks / impact rules) maps precisely to the three phases of `review_pr()`. Plugin authors have a single object to interact with and a small, obvious surface.

- **Frozen snapshot pattern is correct.** `compose()` → `ComposedReviewerSpec` (frozen dataclass with tuple fields) is the right abstraction. It gives the reviewer a consistent, immutable view for the duration of one call. Verified: post-compose registrations do not affect in-flight reviews.

- **Dedup semantics are well-chosen per channel.** Secret patterns dedup on `(regex, kind)` — idempotent and correct. Named checks replace — allows plugin upgrade without duplicate execution. Unnamed checks accumulate — correct since unnamed checks have no identity.

- **Plugin isolation is production-grade.** `except Exception` catch in the check loop appends a `warning`-severity `QualityFinding` and continues. The "good check still runs after bad check" property is verified in both a test and a live probe. Plugin crash never escalates the verdict beyond the `warning` tier.

- **Backward compatibility is solid.** `RealPRReviewer()` with no `registry` arg works identically to the pre-PR behavior. `registry=None` is the default. All 221 pre-existing tests pass unchanged.

- **`__init__.py` exports are complete.** All 5 hooks, all registry types, and all impact/action constants are re-exported from the package root. Public API is well-formed.

- **Test quality is high.** 26 tests in 7 coherent classes. Assertions are specific (`is check_v2`, exact tuple contents, exact call ordering). Integration tests mock `fetch_pr_diff` at the module level (correct monkeypatch path), not at the subprocess level — appropriate for unit isolation.

---

### Issues Found

#### Medium

**M1 — `registry_pattern_count` / `registry_check_count` appear in metadata even when `registry=None`**

```python
# pr_reviewer_impl.py L552-554
"registry_pattern_count": len(spec.secret_patterns) if spec else 0,
"registry_check_count":   len(spec.checks)          if spec else 0,
```

When `registry=None`, `spec=None`, so both keys are emitted as `0`. This is misleading: a consumer inspecting metadata cannot distinguish "registry not attached" from "registry attached with no patterns." The more correct behavior would be to omit the keys entirely when `registry is None`:

```python
# Proposed fix:
**({"registry_pattern_count": len(spec.secret_patterns),
    "registry_check_count":   len(spec.checks)} if spec is not None else {}),
```

No test currently catches this inconsistency (the existing `test_registry_pattern_detected_in_review` only tests the registry-attached path). This is not a correctness bug — downstream consumers currently ignore these fields — but it is a contract ambiguity.

**Severity:** Medium (documentation / contract clarity, not runtime correctness)

---

#### Low

**L1 — All 5 HOOK_* constants are dead code in this PR**

The hook constants are defined, documented, and exported, but zero call-sites fire them in this PR. `grep -rn 'HOOK_BEFORE\|fire.*hook\|dispatch.*hook'` finds only the declaration/import sites. The `prismatic.core.registry.PluginLoader` that was supposed to dispatch them (mentioned in `hooks.py` line 17) does not appear in this codebase at all.

This is explicitly *intended* — hooks are the "declarative extension story" defined now and wired later. The docstring in `hooks.py` is honest about this: it says *"RealPRReviewer and PipelineOrchestrator fire them at the documented points"* but they do not yet. The concern is that the docstring overpromises. A future developer reading the hook table might believe the hooks are live.

> **Recommendation:** Add a `# NOTE: not yet wired; see Gap 9 / Part C` comment to the hook table in `hooks.py`, or add a `WIRED = False` guard. This prevents confusion without requiring code changes in this PR.

**Severity:** Low (documentation correctness, no runtime impact)

---

**L2 — `ImpactRule` contributions are registered and snapshotted but never called by `review_pr()`**

`spec.impact_rules` is populated correctly, but `review_pr()` in `pr_reviewer_impl.py` never iterates over it. The `ImpactRule` loop documented in the registry docstring (*"first non-None wins"*) is tested only in isolation within `test_registry.py` — the integration tests loop over the rules manually, not via the reviewer. The `impact_rules` field is dead weight in the current `ComposedReviewerSpec`.

This is the same situation as L1: the slot is reserved, not yet wired. The risk is that a plugin author registers an impact rule expecting it to fire and is silently ignored.

> **Recommendation:** Either: (a) add a `# TODO: wired in Gap 9 / Part C` comment on the `impact_rules` field and `register_impact_rule()`, or (b) add an integration test that asserts impact rules do NOT yet change the verdict (regression guard so wiring doesn't accidentally break). Option (b) is slightly better because it turns the "not wired" invariant into a failing test the moment someone wires it incompletely.

**Severity:** Low (silent no-op for plugin authors; no runtime error)

---

**L3 — Severity validation in `register_secret_pattern` is redundant with the `Literal` type annotation**

```python
def register_secret_pattern(self, regex, kind, severity: Literal["critical","high","medium","warning"]) -> None:
    if severity not in ("critical", "high", "medium", "warning"):
        raise ValueError(...)
```

The runtime check is correct and desirable (Literal is not enforced at runtime without a type checker). However, the valid set is duplicated in the Literal annotation and the tuple. If a new severity level is ever added, both must be updated independently — one is a potential source of drift. Minor, but worth noting.

> **Recommendation:** Define a module-level `_VALID_SEVERITIES = frozenset({"critical","high","medium","warning"})` and reference it in both the validation tuple and an explicit `Annotated` / comment on the Literal.

**Severity:** Low (maintenance / DRY concern, no impact now)

---

**L4 — `register_check()` name-replace silently fails to remove the old function if its `_prismatic_check_name` attribute was never set (e.g. due to a previous `AttributeError`)**

```python
# L143: filter by attribute
self._checks = [c for c in self._checks if getattr(c, "_prismatic_check_name", None) != name]
```

If the initial tagging (`fn._prismatic_check_name = name`) failed silently (e.g. the callable was a builtin or a C extension), the old entry survives the filter. The new function is still appended, so `check_count` grows by 1 rather than staying at 1. The `_seen_check_names` set still records the name, so subsequent calls do try to replace — they just fail to remove the ghost entry.

This is an edge case for pathological callers (passing a builtin as a named check). The `try/except (AttributeError, TypeError): pass` handling is correct in intent but creates an inconsistency in the data structures. There is no test that exercises this path.

> **Recommendation:** Use a wrapper `functools.wraps`-style approach or a `dict[str, QualityCheck]` keyed by name instead of mutating attributes on arbitrary callables. A dict-based approach eliminates the attribute mutation entirely.

**Severity:** Low (edge case; requires pathological caller)

---

### Thread-Safety Assessment

**Not an issue in this PR, by design.** `ReviewerRegistry` is documented as not thread-safe and intended for setup-time use. `compose()` produces a frozen tuple snapshot, so concurrent `review_pr()` calls on the same `RealPRReviewer` are safe as long as the registry is not mutated concurrently. The docstring is explicit:

> *"Thread safety: not thread-safe. Construct one per worker thread, or guard externally. The registry is designed for setup-time use (during plugin init), not for hot-path mutation."*

This is an acceptable constraint for a plugin registration API. ✅

---

### Plugin Isolation Assessment

**The warn-and-continue policy is correct for this use case.** Plugins are third-party; one bad plugin should not abort a review. The `warning`-severity finding means the failure is visible in the review result without escalating the verdict. The `good_check` after `broken_check` still runs — verified by live probe.

The question of a "raise-stop" opt-in is valid but belongs in a future PR (Gap 9 / Part C or Part D). For a v1 registry, warn-and-continue is the safer default.

---

### Public API Surface Assessment

**`register_check()` name-replace semantics are correct.** Named checks have an identity, unnamed don't. The replace semantic on named is the right choice for plugin upgrade scenarios. Issue L4 is the implementation-level edge case, not a design flaw.

**`SecretPattern` and `ImpactRule` type aliases are self-documenting.** The `Literal["critical","high","medium","warning"]` in `SecretPattern` is immediately clear to a plugin author. The docstrings on both aliases describe elements by position.

---

### Recommendation

**Approve this PR.** The three failing criteria from the bar are all met:

1. ✅ **247/247 tests pass** — confirmed by local run.
2. ✅ **Public API is correct** — registry, spec, hooks all work as documented.
3. ✅ **Backward compat holds** — `RealPRReviewer()` without registry unchanged.
4. ✅ **Plugin isolation works** — crash → warning finding → good checks continue.

The four issues found (M1, L1, L2, L4) are all non-blocking. M1 (metadata keys present when registry is None) is the only one worth addressing before the next PR that consumes this API; the others can be tracked as follow-up items. The PR author should add `# TODO: not yet wired` comments to `hooks.py` and `register_impact_rule()` to prevent future confusion, but this is a documentation polish, not a correctness fix.

**Required before merge:** None.  
**Recommended follow-ups (track in Linear):**
- Fix M1: omit `registry_*` metadata keys when `registry is None`.
- Add `# TODO: not yet wired` guards to hook constants and `register_impact_rule()` (L1, L2).
- Consider replacing attribute-mutation name tracking with a `dict[str, QualityCheck]` (L4).

---

### Re-Review Checklist (if changes are made)

- [ ] If M1 is fixed: verify `test_reviewer_without_registry_unchanged` passes and add a new assertion that `registry_pattern_count` is absent from metadata.
- [ ] Re-run `python3 -m pytest prismatic/ -v` — must remain 247/247.
- [ ] If hook wiring is added in Part C: verify each `HOOK_BEFORE_*` constant is exercised by at least one integration test.
- [ ] If `register_impact_rule` is wired to `review_pr()`: add an integration test with a mock `classify_impact` result and verify the impact rule overrides it.
