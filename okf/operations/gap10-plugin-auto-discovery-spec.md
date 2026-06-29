# Gap 10 — Plugin Auto-Discovery

**Date:** 2026-06-28 (revised after recon)
**Sprint:** 1 of 3 (Phase 3)
**Lane:** Ned (code) + Fred (dispatcher hookup)
**Estimated effort:** 1 day
**Status:** SPEC REVISION — pending Michael's sign-off

---

## What changed from the original spec

**Original (REQUEST_CHANGES):** Proposed `discover_and_register_plugins()` but missed:
1. Two parallel plugin systems coexist (`PluginLoader` filesystem-based + `ReviewerRegistry` entry-points-based)
2. `register_impact_rule` is currently inert — must NOT advertise as working until Gap 11
3. Test count baseline wrong (claimed 261, actual is 250)
4. Rubric missed end-to-end coverage (Lesson 10 anti-pattern)
5. Ship-then-validate ordering wrong (Gap 12 must land AFTER, not before)

**Recon findings (full audit in `phase3-reconnaissance-2026-06-28.md`):**
- `prismatic.plugins` entry-point group declared in pyproject.toml:73 but **zero calls to `entry_points()` in any .py file**
- Verified live: `entry_points(group="prismatic.plugins")` returns `[]` — no plugins installed
- 3 pip-installed prismatic packages, none register under the group
- 11+ gaps in the distribution checklist for real plugin authors
- `ReviewerRegistry` has 8 gaps (no unregister, no plugin-source tagging, etc.)
- Old `PluginLoader` (filesystem) is **not called from production** — out of scope

**Revised approach:** Scope to the new entry-points system explicitly. Leave the old `PluginLoader` alone (it's already uncoordinated; bridging is a separate, larger gap). Include a `prismatic-hello-world` reference plugin as part of the PR to validate end-to-end.

---

## Goal

Turn Prismatic from "shippable with manual plugin wiring" into "installable with zero-config plugin activation." When a third-party plugin package is installed via `pip install`, the Prismatic Engine dispatcher automatically discovers it on next startup, calls its `register()` function against the active `ReviewerRegistry`, and uses the contributed patterns/checks/rules in every subsequent review.

## Non-Goals (re-affirmed)

- Plugin **auto-update** (pip does this; we don't manage plugin versioning)
- Plugin **hot-reload** (restart required)
- Plugin **isolation / sandboxing** (plugins run with full Python privileges; deferred to security track)
- **Plugin registry UI** (command-line discovery + listing only)
- **Bridging the old `PluginLoader` system** — leave it alone; bridging is Gap 10.5+

## Public API Contracts

### Discovery call site (Ned lane)

New module `prismatic/review/plugin_discovery.py`:

```python
from importlib.metadata import entry_points

def discover_and_register_plugins(
    registry: ReviewerRegistry,
    *,
    timeout_seconds: float = 5.0,
) -> list[str]:
    """Discover installed Prismatic plugins via entry_points and register them.

    For each plugin entry_point under group "prismatic.plugins":
        1. Load with a per-plugin timeout (default 5s). Timeout = warning logged, plugin skipped.
        2. Call register(registry). Exceptions = warning logged, plugin skipped.
        3. Append plugin name to the returned list on success.

    Args:
        registry: The ReviewerRegistry to populate.
        timeout_seconds: Per-plugin load timeout (defense against stuck imports).

    Returns:
        Sorted list of plugin entry-point names that successfully registered.
        Failed registrations are logged but do not abort the dispatcher.
    """
```

**Error isolation contract:**
- `entry_points()` failure → log error, return `[]`
- Per-plugin `ep.load()` timeout (>= `timeout_seconds`) → log warning, skip
- Per-plugin `register()` exception → log warning, skip
- Per-plugin import error → log warning, skip

### Dispatcher integration (Fred lane)

In `prismatic/dispatcher.py:main()`, after constructing the active `ReviewerRegistry` and before the first dispatch tick:

```python
from prismatic.review.plugin_discovery import discover_and_register_plugins

registry = ReviewerRegistry()
discover_and_register_plugins(registry)
# Then continue with existing dispatch loop.
```

No dispatcher-state attachment needed — Gap 12 provides observability. Gap 10 just registers + logs the discovered plugin list at INFO level.

### Reference plugin (Ned lane — INCLUDED IN THIS PR)

New directory `plugins/prismatic-hello-world/` (lives in repo, not installed by default):

```toml
# plugins/prismatic-hello-world/pyproject.toml
[project]
name = "prismatic-hello-world"
version = "0.1.0"

[project.entry-points."prismatic.plugins"]
hello = "prismatic_hello_world:register"
```

```python
# plugins/prismatic-hello-world/src/prismatic_hello_world/__init__.py
from prismatic.review import ReviewerRegistry, QualityFinding

def say_hello(diff: str) -> list[QualityFinding]:
    """Example check: flag any line containing 'hello' as a warning."""
    findings = []
    for i, line in enumerate(diff.splitlines()):
        if line.startswith("+") and "hello" in line.lower():
            findings.append(QualityFinding(
                path="<diff>",
                line=i,
                severity="warning",
                message="Reference plugin: 'hello' found in diff",
            ))
    return findings

def register(registry: ReviewerRegistry) -> None:
    registry.register_check(say_hello, name="hello_world_greeting")
```

The reference plugin:
- Lives in `plugins/` directory (not in main package)
- Is **NOT installed by default** — only installed when explicitly tested (`pip install -e plugins/prismatic-hello-world`)
- Exists to provide a real-plugin-in-real-registry test target

## Files Changed

| File | Change |
|---|---|
| `prismatic/review/plugin_discovery.py` (NEW) | `discover_and_register_plugins()` function |
| `prismatic/review/test_plugin_discovery.py` (NEW) | Test rubrics below |
| `prismatic/review/__init__.py` | Export `discover_and_register_plugins` |
| `prismatic/dispatcher.py` | Call `discover_and_register_plugins(registry)` at startup |
| `plugins/prismatic-hello-world/pyproject.toml` (NEW) | Reference plugin manifest |
| `plugins/prismatic-hello-world/src/prismatic_hello_world/__init__.py` (NEW) | Reference plugin implementation |
| `plugins/prismatic-hello-world/README.md` (NEW) | Plugin author quickstart |
| `okf/operations/prismatic-distribution-checklist.md` | Update with `register(registry)` signature contract + load-order/error-isolation/duplicate-resolution spec |

## Test Rubrics

In `TestDiscoverAndRegisterPlugins` (8 tests):

1. `test_empty_discovery_returns_empty_list` — no plugins installed, no crash
2. `test_single_plugin_registers_successfully` — mock entry_points with one plugin, verify it was called
3. `test_multiple_plugins_register_in_sorted_order` — verify alphabetical registration order
4. `test_plugin_load_failure_is_logged_not_raised` — broken plugin doesn't crash dispatcher
5. `test_plugin_register_call_failure_is_logged_not_raised` — `register()` raises, dispatcher logs + continues
6. `test_plugin_load_timeout_is_logged_not_raised` — stuck plugin import, dispatcher times out, continues
7. `test_duplicate_plugin_names_deduplicated_via_entry_points` — Python entry_points semantics: last wins
8. `test_real_entry_points_group_is_resolvable` — actual `importlib.metadata.entry_points(group="prismatic.plugins")` call works (smoke check, returns `[]` since no plugins installed)

In `TestRealPluginEndToEnd` (3 tests — the ones that would have caught Lesson 10 anti-pattern):

9. `test_reference_plugin_loads_into_real_registry` — install `prismatic-hello-world` in temp env, run discovery, verify `registry.check_count == 1` and the registered check is named `hello_world_greeting`
10. `test_reference_plugin_check_runs_against_real_diff` — invoke the registered check against a fixture diff containing "hello", verify QualityFinding is returned with the right severity
11. `test_reference_plugin_remove_pattern_does_not_affect_registry` — uninstall plugin, re-run discovery, verify the previously registered check is no longer in the registry (proves discovery is per-startup, not persistent)

In `TestDispatcherIntegration` (2 tests):

12. `test_dispatcher_main_calls_discovery_with_real_registry` — verify wiring via mock
13. `test_dispatcher_continues_when_discovery_raises` — `entry_points()` raises, dispatcher continues

**Total: 13 new tests.**

## Acceptance Criteria

- [ ] `discover_and_register_plugins()` exported from `prismatic.review`
- [ ] Calling it with no plugins installed returns `[]` without crashing
- [ ] Calling it with a mock-installed plugin calls the plugin's `register(registry)` exactly once
- [ ] Failures (load timeout, register call) are logged + skipped, not raised
- [ ] The result is sorted alphabetically
- [ ] `prismatic.dispatcher.main()` calls discovery at startup and logs the registered list
- [ ] Reference plugin (`prismatic-hello-world`) ships in `plugins/` directory
- [ ] Test #9 verifies a real installed plugin's contributions appear in the registry (catches Lesson 10 anti-pattern)
- [ ] 13 new tests pass; 263/263 total (was 250)
- [ ] Peer review by claude-sonnet-4-6 returns APPROVE

## Acceptance: "This Gap Shipped Correctly" Evidence

- A real plugin can be installed via `pip install -e plugins/prismatic-hello-world` and contribute a check to the next review tick
- The discovery loop is observable: `prismatic.review.plugins_discovered_total` counter (Gap 12) shows the registered count
- Test #9 (real plugin in real registry) passes — this is the test that would have caught Phase 2 Lesson 10

## Carry-Forward (not in this gap)

- **Plugin auto-update** — pip does this
- **Plugin hot-reload** — restart required
- **Plugin isolation / sandboxing** — security track, Gap 15+
- **Bridging old `PluginLoader`** — Gap 10.5+ (separate, larger initiative)
- **Conflict resolution policy** — current design is "last-wins with silent override" via `register_check(name=...)`. Documented in distribution checklist. Alternative policies (per-plugin namespace, warn-on-conflict) deferred to Gap 14 when first real third-party plugin hits a conflict.
- **Pattern count ceiling** (10k-pattern DoS) — meta-review P1 carry-forward; **MUST be addressed before Gap 14 ships first real third-party plugin with patterns**, but not blocking for Gap 10
- **Plugin API stability SemVer policy** — Gap 14 includes the first third-party plugin; we'll know what we need then
- **`register_impact_rule` advertisement** — explicitly documented as inert in distribution checklist until Gap 11 lands

## Lane Notes

- **Ned lane:** `plugin_discovery.py`, `test_plugin_discovery.py`, reference plugin (3 files)
- **Fred lane:** dispatcher hookup (10 lines), distribution checklist update
- Two PRs expected:
  - PR #X (Ned): plugin_discovery module + reference plugin + tests
  - PR #Y (Fred): dispatcher hookup + checklist update

## Pattern Reference

- `okf/operations/phase3-reconnaissance-2026-06-28.md` — entry-points landscape + ReviewerRegistry gaps
- `okf/operations/phase3-second-opinions-2026-06-28.md` — original spec review
- `okf/operations/gap9-implementation-lessons.md` — Lesson 4 (hybrid extension model) + Lesson 10 (tests with good coverage can hide dead APIs)
- `prismatic-distribution-checklist.md` — what plugin authors see today (will be updated)

---

*Spec revised by Fred (orchestrator) after recon + subagent review. Pending Michael's sign-off.*
