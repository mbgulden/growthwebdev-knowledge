---
title: "Gap 13 — Ship-Time Plugin Load Verification Gate"
sprint: 2
status: SPEC
created: 2026-06-29
trigger: "Gap 10 PR #47 shipped a plugin with core_version_constraint incompatible with engine version. Sonnet peer review caught it AFTER PR opened; this gate catches it BEFORE."
---

# Gap 13 — Ship-Time Plugin Load Verification Gate

**Status:** SPEC
**Sprint:** 2 (Quality Gates, continued)
**Date:** 2026-06-29
**Owner:** Fred (orchestrator)
**Trigger:** Gap 10 PR #47 shipped a `prismatic-hello-world` plugin with
`core_version_constraint: ">=1.0.0"` incompatible with engine v0.2.0.
Sonnet peer review caught it AFTER the PR was opened. The failsafe
architecture should have caught it BEFORE.

## The Problem

Prismatic Engine's plugin model lets third parties drop directories
into `plugins/` and have them auto-loaded on startup. The
`PluginLoader` validates each plugin's manifest against the runtime
environment (core version, capabilities, provider constraints).

But there's no **ship-time check** that ensures a newly-added plugin
will actually load in the current environment. The current workflow:

1. Subagent writes plugin files
2. Tests pass (but tests use synthetic `tmp_path` plugins, not the real
   shipped plugin)
3. PR opened
4. Peer review happens AFTER, often finding the version mismatch
5. Fix landed, re-review, merge

The bug ships because **none of the pre-merge steps actually load the
plugin against the real engine version**.

## What Gap 13 Ships

A new gate in `prismatic/quality/plugin_load.py` (parallel to
`prismatic/quality/smoke.py`) that:

1. Discovers every plugin in `plugins/*/plugin-manifest.yaml`
2. Reads the actual core version from `pyproject.toml`
3. Constructs a real `PluginLoader(core_version=<real>, plugins_dir=<repo>/plugins)`
4. Calls `loader.scan_and_load_plugins(context)`
5. Verifies every shipped plugin appears in `loader.loaded_plugins`
6. For each shipped plugin NOT loaded, captures WHY (version mismatch,
   missing manifest, broken entry_point, capability rejection, etc.)
7. Returns `PluginLoadResult(passed, findings=[...])` — same dataclass
   pattern as `SmokeTestResult`

### Architecture

```python
@dataclass
class PluginLoadFinding:
    plugin_name: str
    manifest_path: Path
    status: str  # "loaded" | "version_mismatch" | "missing_manifest" |
                 # "broken_entry_point" | "capability_rejected" |
                 # "provider_blocked" | "unknown_error"
    detail: str = ""

@dataclass
class PluginLoadResult:
    passed: bool
    plugins_dir: Path
    core_version: str
    findings: list[PluginLoadFinding] = field(default_factory=list)
    loaded_count: int = 0
    failed_count: int = 0
    reason: str = ""

    def to_dict(self) -> dict: ...
    def to_markdown(self) -> str: ...


def verify_shipped_plugins_load(
    plugins_dir: Path | None = None,
    core_version: str | None = None,
) -> PluginLoadResult:
    """Load every shipped plugin via real PluginLoader and verify all loaded."""
```

### Integration Points

1. **CI workflow:** `.github/workflows/plugin-load.yml`
   - Runs on every PR that touches `plugins/**` or `prismatic/core/registry.py`
   - Exits non-zero if any plugin fails to load
   - Posts result as PR comment

2. **Pre-commit hook:** `.pre-commit-config.yaml` addition
   - Runs `verify_shipped_plugins_load()` before any commit that
     touches `plugins/**`
   - Same as `ruff format` and `ruff check` gates already there

3. **Manual CLI:** `python3 -m prismatic.quality.plugin_load`
   - For ad-hoc local verification
   - Prints markdown report

4. **Linear comment template:** When the gate fails, generate a
   Linear-comment-ready markdown snippet that can be posted as a PR
   comment explaining what failed and how to fix

### Why a New Module, Not Extension of `smoke.py`

`smoke.py` verifies filesystem claims (agent said "I wrote X" → does X
exist). That's a different concern from "does the shipped artifact
behave correctly at load time". Mixing them would conflate two
verification contracts.

Same dataclass pattern, same `passed: bool` API, same `to_markdown()`
output format → drop-in compatible with any pipeline that consumes
`smoke.SmokeTestResult`.

### Test Coverage (5 tests)

`tests/test_plugin_load_gate.py`:

1. `test_gate_passes_when_all_plugins_load` — happy path: 1 valid
   plugin + real engine version → result.passed == True
2. `test_gate_fails_on_version_mismatch` — regression: plugin with
   `core_version_constraint: ">=99.0.0"` against engine 0.2.0 →
   result.passed == False, finding.status == "version_mismatch"
3. `test_gate_fails_on_missing_manifest` — `plugins/bad/` exists but
   no `plugin-manifest.yaml` → result.passed == False
4. `test_gate_fails_on_broken_entry_point` — manifest points to
   `nonexistent.module:Class` → result.passed == False
5. `test_gate_includes_core_version_in_result` — verify the gate
   surfaces the actual engine version, not a hardcoded string

### Acceptance Criteria

- Gate FAILS PR #47's exact bug pattern (`>=1.0.0` against 0.2.0)
- Gate runs in <5 seconds for current plugin count (10 plugins)
- Gate is opt-in via pre-commit (doesn't break existing workflows)
- Gate provides actionable error messages (not just "load failed")

## Out of Scope (Sprint 3+)

- Runtime plugin health monitoring (separate concern)
- Plugin signing / verification
- Plugin marketplace / remote registry
- Hot-reload on manifest change

## Risk

LOW. This is additive — new module + new test file + new CI workflow.
No existing files modified except `.pre-commit-config.yaml` (additive
hook entry) and `.github/workflows/` (new file).

## Verification

```bash
cd ~/work/prismatic-engine
# Confirm the gate catches Gap 10's bug:
git checkout deploy-fresh  # 0.2.0
python3 -m prismatic.quality.plugin_load --plugin-dir plugins/
# EXPECT: prismatic-hello-world: loaded (after the gap-10-fix)

git checkout feature/gap10-buggy  # hypothetical branch with >=1.0.0
python3 -m prismatic.quality.plugin_load --plugin-dir plugins/
# EXPECT: prismatic-hello-world: version_mismatch (>=1.0.0 vs 0.2.0)

# Tests
python3 -m pytest tests/test_plugin_load_gate.py -v
# EXPECT: 5 passed
ruff check prismatic/quality/plugin_load.py tests/test_plugin_load_gate.py
ruff format --check prismatic/quality/plugin_load.py tests/test_plugin_load_gate.py
```
