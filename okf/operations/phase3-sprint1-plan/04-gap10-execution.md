# Gap 10 — Plugin Auto-Discovery Execution Plan

**Estimated Sonnet subagent time:** ~30 minutes
**Files touched:** 8 (2 modified, 5 new production, 1 new test)
**Tests added:** 13
**Exit criteria:** 302/302 tests passing (290 from Gap 11 + 12 new, accounting for test #11 needing `pip install -e`)

---

## Subagent Prompt Skeleton

### Context to Pass

```
You are implementing Gap 10 (Plugin Auto-Discovery) for the Prismatic Engine.
Gap 12 and Gap 11 have already landed. Test baseline is 290/290.
register_impact_rule() is NOW WIRED (Gap 11 shipped).

READ THESE FILES FIRST (in order):
1. prismatic/review/registry.py — ReviewerRegistry you'll call discover against
2. prismatic/review/__init__.py — verify QualityCheck is exported (PR #43 fix)
3. prismatic/dispatcher.py — main() where you'll add the discovery call
4. pyproject.toml — line 73 where prismatic.plugins group is declared

SPEC: [embed gap10-plugin-auto-discovery-spec.md contents]

CONSTRAINTS:
- Two plugin systems coexist (PluginLoader + ReviewerRegistry). You ONLY touch the new entry-points system. Leave PluginLoader alone.
- register_impact_rule() IS NOW WIRED — you can advertise it in docs
- Reference plugin prismatic-hello-world goes in plugins/ directory (not installed by default)
- Error isolation: any plugin failure = warning log + skip, never crash dispatcher
- Per-plugin timeout defense (5s default) for stuck imports
- Discovery result is sorted alphabetically
```

### Rubric (verifiable handles in return)

```
RETURN FORMAT:
1. Files created/modified (line count, diff summary)
2. discover_and_register_plugins() exact signature
3. Error isolation: how each failure mode is handled (entry_points failure, load timeout, register exception, import error)
4. Reference plugin: pyproject.toml entry-points declaration + register() function
5. Dispatcher hookup: exact location in main() and the code added
6. Test file + test count + test names
7. pytest output: 302 passed (or 301 if test #9 requires pip install -e)
8. Confirmation: 290 baseline tests still pass
```

---

## Integration Steps for Fred After Subagent Returns

1. **Verify discovery function:** `python -c "from prismatic.review.plugin_discovery import discover_and_register_plugins; print('OK')"` → must import cleanly
2. **Verify empty discovery:** `python -c "from prismatic.review import ReviewerRegistry; from prismatic.review.plugin_discovery import discover_and_register_plugins; r = ReviewerRegistry(); print(discover_and_register_plugins(r))"` → expect `[]`
3. **Verify reference plugin structure:**
   - `ls plugins/prismatic-hello-world/` → pyproject.toml, src/, README.md
   - `grep "prismatic.plugins" plugins/prismatic-hello-world/pyproject.toml` → entry-point declaration
4. **Verify dispatcher hookup:** `grep -n "discover_and_register_plugins" prismatic/dispatcher.py` → 1 call site
5. **Test reference plugin end-to-end (manual):**
   - `pip install -e plugins/prismatic-hello-world`
   - `python -c "from prismatic.review import ReviewerRegistry; from prismatic.review.plugin_discovery import discover_and_register_plugins; r = ReviewerRegistry(); print(discover_and_register_plugins(r))"` → expect `['hello']`
   - `pip uninstall prismatic-hello-world -y`
6. **Branch creation:**
   - `ned/gap10-plugin-discovery` for Ned-lane files (plugin_discovery.py, reference plugin, tests)
   - `feature/gap10-dispatcher-hookup` for Fred-lane files (dispatcher.py, distribution checklist)
7. **Push + peer review + merge**

---

## Rollback Plan if PR Fails Peer Review

**Severity: LOW risk.** Gap 10 is additive — new module, new reference plugin, one call-site addition.

1. If peer review returns REQUEST_CHANGES:
   - Most likely: timeout implementation, error isolation edge cases
   - Fix in-place, re-test, re-submit
2. If reference plugin `prismatic-hello-world` trips a security scanner:
   - The plugin searches for "hello" in diffs — benign, but `QualityFinding` with `severity="warning"` might confuse scanners
   - **Mitigation:** Use a clearly synthetic check name (`hello_world_greeting`) and document in README that this is a reference-only plugin
   - **Escape hatch:** Ship Gap 10 without the reference plugin; use a mock-only test approach for test #9-11. This weakens Lesson 10 coverage but doesn't block the gap.
3. If `pip install -e plugins/prismatic-hello-world` fails in the test environment:
   - Check if `src/` layout is correct (must match `pyproject.toml`'s `[tool.setuptools.packages.find]`)
   - If env is too constrained: mark tests #9-11 as `@pytest.mark.skipif` with a descriptive reason

---

## Risks

### R10-1: `prismatic-hello-world` could trip GitHub push protection or secret scanner

**File:line:** `plugins/prismatic-hello-world/src/prismatic_hello_world/__init__.py` (new file)
**Likelihood:** Low — no actual secrets, no credential patterns
**Impact:** Low — would block the push, not the feature
**Mitigation:** Review the reference plugin source for anything that looks like a secret pattern. The `say_hello` function checks for "hello" in diffs, which is benign. Ensure no test fixtures contain strings matching common secret patterns (AWS keys, API tokens).
**Escape hatch:** If push protection blocks, rename the check to something clearly non-secret-like and re-push.

### R10-2: `entry_points(group="prismatic.plugins")` behavior differs across Python versions

**File:line:** `prismatic/review/plugin_discovery.py` (new file, ~line 5)
**Likelihood:** Low — project targets Python 3.10+ where `importlib.metadata.entry_points(group=...)` is stable
**Impact:** Medium — discovery silently returns empty if API differs
**Mitigation:** Test #8 (`test_real_entry_points_group_is_resolvable`) is an explicit smoke test. If it fails, we know the API call itself is broken.
**Escape hatch:** Fall back to `importlib_metadata` backport (third-party package).

### R10-3: `discover_and_register_plugins` timeout mechanism may be unreliable

**File:line:** `prismatic/review/plugin_discovery.py` (new file, ~line 15)
**Likelihood:** Medium — Python's `signal.alarm` doesn't work on Windows; `threading.Timer` + `_thread.interrupt_main()` is fragile
**Impact:** Low — stuck import would block dispatcher startup, but current deployment is Linux-only
**Mitigation:** Use `concurrent.futures.ThreadPoolExecutor` with `future.result(timeout=timeout_seconds)` — reliable on all platforms, clean timeout semantics.
**Escape hatch:** If timeout mechanism is too complex, ship without per-plugin timeout and add a `# TODO: per-plugin load timeout` comment. At current plugin count (0), this is safe.

---

## File Paths and Line Numbers (from recon)

| Target | File | Key Lines | What to Do |
|---|---|---|---|
| Entry-point group declaration | `pyproject.toml` | L73 | Already exists — DO NOT modify |
| ReviewerRegistry | `prismatic/review/registry.py` | Full file (215 lines) | DO NOT modify (Gap 10 only consumes it) |
| ReviewerRegistry.__init__.py export | `prismatic/review/__init__.py` | Imports block | Add `discover_and_register_plugins` to exports |
| Dispatcher main() | `prismatic/dispatcher.py` | `main()` function | Add discovery call after registry construction |
| PluginLoader (OLD system) | `prismatic/core/registry.py` | Full file (212 lines) | DO NOT TOUCH — explicitly out of scope |
| Existing plugins directory | `plugins/` | 12 dirs | Add `prismatic-hello-world/` alongside existing |
| Zero callers of entry_points | (all .py files) | — | Confirmed by recon: zero calls before Gap 10 |

---

*Filed 2026-06-28 by Opus (claude-opus-4-6-thinking). Gap 10 execution detail.*
