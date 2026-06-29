---
title: "Gap 10 — Plugin Discovery Hardening + prismatic-hello-world Reference"
sprint: 1
status: SPEC
created: 2026-06-28
linear: GRO-1218
---

# Gap 10 — Plugin Discovery Hardening + `prismatic-hello-world` Reference

## Status: SPEC (Sprint 1)

## Context

The Prismatic Engine has working plugin discovery (`PluginLoader` in
`prismatic/core/registry.py`, 212 lines, scans `$PRISMATIC_HOME/plugins/`
for `plugin-manifest.yaml` files, validates version constraints,
dynamically imports modules, exposes loaded plugins to the dispatcher).

It also has an `example_plugin` stub (`plugins/example_plugin/`, 2 files,
`personas: []`, no real registration patterns).

What it DOESN'T have:

1. A **canonical reference plugin** that demonstrates ALL the new
   registration patterns introduced in Sprint 1:
   - `register_secret_pattern()`
   - `register_check()`
   - `register_impact_rule()`
   - `register_action_rule()`
2. **Integration tests** proving `PluginLoader.scan_and_load_plugins()`
   actually picks up a real-world plugin and wires its registrations
   through to `PipelineOrchestrator`.
3. A **canonical manifest example** showing the full Sprint 1 manifest
   schema (the `plugin.yaml` doc covers each field in isolation but no
   one real example ties them together).
4. **Docs link** from `README.md` to the canonical example (so plugin
   authors have a working starting point).

## What Ships

### A. `plugins/prismatic-hello-world/` — Canonical Reference Plugin

```
plugins/prismatic-hello-world/
├── plugin-manifest.yaml   # Full schema, all fields populated
├── plugin.py              # HelloWorldPlugin class
├── README.md              # "How to copy this plugin" walkthrough
└── tests/
    └── test_hello_world.py # Plugin-level tests proving registrations work
```

`HelloWorldPlugin` registers ONE example of each pattern:

```python
def register(self, context):
    registry = context.review_registry

    # 1. Custom secret pattern
    registry.register_secret_pattern(
        regex=r"hello_[a-z0-9]{16}",
        kind="hello_world_token",
        severity="warning",
    )

    # 2. Custom quality check
    def no_hello_comments(check_diff: str) -> list:
        # Returns a QualityFinding if the diff has "# hello" comments
        ...
        return []

    registry.register_check(no_hello_comments, name="hello.no_comments")

    # 3. Impact override rule
    def escalate_when_hello(r, current):
        # Treat hello-world PRs as minor instead of trivial
        return "minor" if "hello" in r.summary else None

    registry.register_impact_rule(escalate_when_hello)

    # 4. Action override rule
    def force_rework_when_hello(r, current):
        # Force a rework pass for any hello-world plugin usage
        return "rework" if "hello_world" in r.summary else None

    registry.register_action_rule(force_rework_when_hello)
```

### B. Integration Test — PluginLoader to PipelineOrchestrator

In `tests/test_plugin_loader_pipeline.py`:

```python
def test_plugin_loader_wires_through_to_pipeline():
    # PluginLoader must call register() on discovered plugins with a
    # PluginContext that exposes the review_registry, and the registered
    # rules must actually fire during PipelineOrchestrator.process().
    # 1. Create a temp dir with a minimal valid plugin manifest
    # 2. Run PluginLoader.scan_and_load_plugins(context)
    # 3. Assert registry has the expected registrations
    # 4. Run PipelineOrchestrator(registry=...).process() with a hello PR
    # 5. Assert decision.impact was overridden by the plugin rule
    pass
```

### C. README Link + Manifest Example

- Add a "Building your first plugin" section to `README.md` pointing
  to `plugins/prismatic-hello-world/` as the canonical example.
- The plugin own `README.md` is the entry point — it explains the
  copy-paste workflow: "Duplicate this directory, rename, edit
  `plugin-manifest.yaml` and `plugin.py`."

### D. Test Count Target

| Component | Tests |
|---|---|
| `plugins/prismatic-hello-world/tests/test_hello_world.py` | 5 |
| `tests/test_plugin_loader_pipeline.py` | 4 |
| `tests/test_plugin_loader_capability_validation.py` (new) | 4 |
| **Total new** | **13** |

Sprint 1 target after Gap 10: 307 + 13 = **320 tests**.

## Out of Scope (Sprint 2+)

- Auto-install of pip dependencies declared in `dependencies.pip`
- Plugin signing / verification
- Hot-reload on manifest change
- Plugin marketplace / remote registry

## Why This Gap Matters

Right now there is no working example plugin that exercises the
registration patterns Sprint 1 added. A new plugin author reading the
manifest schema would have to mentally compose all the pieces. The
`prismatic-hello-world` plugin is the copy-paste-friendly entry point
that ties everything together — without it, Sprint 1 plugin API is
documented but not discoverable in practice.

## Risk

LOW. This is additive (new directory, new test file, README link). No
existing files modified except a small README addition.

## Verification

```bash
cd ~/work/prismatic-engine
python3 -m pytest tests/ prismatic/ --tb=short -q 2>&1 | tail -3
# EXPECT: 320 passed (was 307, +13 from Gap 10)
ruff check plugins/prismatic-hello-world/
ruff format --check plugins/prismatic-hello-world/
```
