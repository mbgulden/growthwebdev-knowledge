# Gap 10 — Plugin Auto-Discovery

**Date:** 2026-06-28
**Sprint:** 1 of 3 (Phase 3)
**Lane:** Ned (code) + Fred (infra hookup)
**Estimated effort:** 1 day
**Status:** SPEC — pending Michael's sign-off

---

## Goal

Turn Prismatic from "shippable with manual plugin wiring" into "installable with zero-config plugin activation." When a third-party plugin package is installed via `pip install`, the Prismatic Engine dispatcher automatically discovers it on next startup, calls its `register()` function against the active `ReviewerRegistry`, and uses the contributed patterns/checks/rules in every subsequent review.

## Non-Goals

- Plugin **auto-update** (pip does this; we don't manage plugin versioning)
- Plugin **hot-reload** (restart required; not in scope)
- Plugin **isolation / sandboxing** (plugins run with full Python privileges; security track deferred to Gap 15+)
- **Plugin registry UI** (command-line discovery + listing only; no admin dashboard)

## Public API Contracts

### Discovery call site

In `prismatic/dispatcher.py:main()`, after constructing the active `ReviewerRegistry` and before the first dispatch tick:

```python
from importlib.metadata import entry_points

def discover_and_register_plugins(registry: ReviewerRegistry) -> list[str]:
    """Discover installed Prismatic plugins via entry_points and register them.

    Returns:
        Sorted list of plugin entry-point names that successfully registered.
        Failed registrations are logged but do not abort the dispatcher.
    """
    discovered = entry_points(group="prismatic.plugins")
    registered: list[str] = []
    for ep in discovered:
        try:
            register_fn = ep.load()
            register_fn(registry)
            registered.append(ep.name)
        except Exception as exc:
            log.error("Plugin %s failed to register: %s", ep.name, exc)
    return sorted(registered)
```

### Dispatcher integration

`prismatic.dispatcher.main()` calls `discover_and_register_plugins(registry)` once at startup. The list of registered plugins is logged + attached to dispatcher state for `agent:ops-feed` reporting.

### Plugin author contract (unchanged from Gap 9 / Part B)

```toml
# Their pyproject.toml
[project.entry-points."prismatic.plugins"]
my_plugin = "my_pkg:register"
```

```python
# Their my_pkg/__init__.py
from prismatic.review import ReviewerRegistry

def register(registry: ReviewerRegistry) -> None:
    registry.register_check(my_check, name="my_check")
    registry.register_secret_pattern(r"FOO_[A-Z]+", "company_token", "critical")
```

## Files Changed

| File | Change |
|---|---|
| `prismatic/dispatcher.py` | Add `discover_and_register_plugins()` call in `main()` |
| `prismatic/review/plugin_discovery.py` (NEW) | `discover_and_register_plugins()` function + plugin-name resolution |
| `prismatic/review/test_plugin_discovery.py` (NEW) | Test rubrics below |
| `prismatic/review/__init__.py` | Export `discover_and_register_plugins` |

## Test Rubrics

8 tests, in `TestDiscoverAndRegisterPlugins` class:

1. `test_empty_discovery_returns_empty_list` — no plugins installed, no crash
2. `test_single_plugin_registers_successfully` — mock entry_points with one plugin, verify it was called
3. `test_multiple_plugins_register_in_sorted_order` — verify alphabetical registration order (deterministic)
4. `test_plugin_load_failure_is_logged_not_raised` — broken plugin doesn't crash dispatcher
5. `test_plugin_register_call_failure_is_logged_not_raised` — `register()` raises, dispatcher logs + continues
6. `test_duplicate_plugin_names_deduplicated` — two packages register same name, last wins (Python entry_points semantics)
7. `test_discovered_plugins_listed_in_dispatcher_state` — integration test: dispatcher.main() attaches list to state
8. `test_real_entry_points_group_resolvable` — actual `importlib.metadata.entry_points(group="prismatic.plugins")` call works (sanity check)

Plus 3 integration tests in `TestDispatcherIntegration`:

9. `test_dispatcher_main_calls_discovery_with_real_registry` — verify wiring
10. `test_dispatcher_state_attaches_registered_plugins` — verify state population
11. `test_dispatcher_continues_when_all_plugins_fail` — robustness check

**Total: 11 new tests.**

## Acceptance Criteria

- [ ] `discover_and_register_plugins()` is exported from `prismatic.review`
- [ ] Calling it with no plugins installed returns `[]` without crashing
- [ ] Calling it with a mock-installed plugin calls the plugin's `register(registry)` exactly once
- [ ] Failures (load OR register) are logged + skipped, not raised
- [ ] The result is sorted alphabetically (deterministic for ops dashboards)
- [ ] `prismatic.dispatcher.main()` calls discovery at startup and logs the registered list
- [ ] 11 new tests pass; 261/261 total (was 250)
- [ ] Peer review by claude-sonnet-4-6 returns APPROVE (or REQUEST_CHANGES → fix → APPROVE)

## Carry-Forward (not in this gap)

- **Plugin signature verification** (signed packages) — security track, Gap 15+
- **Plugin metadata schema** (name, version, author, dependencies) — Gap 14 ships first real plugin
- **Plugin enable/disable per-tenant** — Gap 12-full (observability + ops feed)

## Lane Notes

- **Ned lane:** owns the new `plugin_discovery.py` + `test_plugin_discovery.py`
- **Fred lane:** owns the `prismatic.dispatcher.main()` hookup (small change, ~10 lines)
- Two PRs expected:
  - PR #45 (Ned): plugin_discovery module + tests
  - PR #46 (Fred): dispatcher hookup

## Pattern Reference

- `okf/operations/gap9-implementation-lessons.md` — Lesson 4 (hybrid extension model) + Lesson 9 (meta-review)
- `okf/operations/phase2-meta-review-2026-06-28.md` — Section "Recommended Next Steps" item 8
- `~/.hermes/profiles/orchestrator/skills/meta-review-architecture/SKILL.md`

---

*Spec written by Fred (orchestrator) — pending Michael's sign-off before AGY delegation.*
