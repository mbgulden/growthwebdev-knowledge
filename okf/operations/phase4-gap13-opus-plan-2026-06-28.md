# Phase 4 / Gap 13 — Windows + macOS Compatibility — Opus Plan

**Date:** 2026-06-28
**Author:** Opus (planning), on behalf of Fred (orchestrator)
**Sprint:** 2 of 3
**Status:** READY FOR IMPLEMENTATION
**Estimated implementation effort:** ~90 min (Sonnet)
**Estimated peer review effort:** ~30 min (Sonnet)
**Target test count:** ~12 new tests, bringing repo from 297 → ~309 + the existing test surfaces

---

## 0. Scope Concerns (Read First)

The spec is **directionally correct but under-specified in two places and over-scoped in one**. Calling them out up front so Sonnet doesn't waste cycles:

### 0a. Over-scope — "6 modules" is a guess
The prompt says *"`os.path.join` / string concatenation in 6 modules: identify all `os.path` usages in `prismatic/`"*. That bullet is misleading because:

- `prismatic/` has **~80 occurrences** of `os.path` across **~30 files**, not 6.
- Most of them are correct usages (state-dir joins, db paths) and are already env-overridable via `PRISMATIC_STATE_DIR`.
- The real Linux-only bugs are concentrated in **6 modules** that hardcode `/tmp/...` literals for *scratch* (not state):

| Module | Hardcoded Linux-only paths |
|---|---|
| `prismatic/dispatcher.py` | `NUDGE_DIR=/tmp/prismatic`, `PIPELINE_METRICS_PATH=/tmp/pipeline_metrics.jsonl` |
| `prismatic/distributed_watchdog.py` | `NODE_ROSTER=/tmp/prismatic/swarm_nodes.json`, `HEALTH_STATE_PATH=/tmp/prismatic/distributed_watchdog_state.json`, `VRAM_MARKER_DIR=/tmp/prismatic/vram` |
| `prismatic/providers/signals/file.py` | `__init__(directory="/tmp/prismatic")` default + docstring `/tmp/prismatic/nudge-{target}` |
| `prismatic/providers/signals/__init__.py` | Three config-template defaults of `/tmp/prismatic` |
| `prismatic/quality/failure.py` | `COUNTER_PATH = "/tmp/failure_counter.json"` |
| `prismatic/journal.py` | `Path(f"/tmp/antigravity_{issue_identifier}.log")` fallback (only when `log_path=None` AND `issue_identifier` provided) |

**The plan targets these 6 modules, not "all os.path usages".** Touching the other ~24 files (`prismatic/billing/*`, `prismatic/gateway/*`, etc.) is a separate refactor that would explode scope into a 6-hour PR with no functional change on Linux. If Fred wants the full audit, that's a different gap (call it Gap 13.5 or roll into Gap 12-full's quality sweep).

### 0b. Under-spec — the "6 modules" pathlib conversion needs a target style
Two reasonable options, with very different diff sizes. I recommend **Option B** (see §1). The spec doesn't pick.

### 0c. Under-spec — `/tmp/` default replacement
The spec says `tempfile.gettempdir()`. That's correct *mechanically* but wrong *semantically*:
- `tempfile.gettempdir()` is **per-process ephemeral** by design (cleared on reboot, often `/tmp` on Linux but `%TEMP%` on Windows which is user-scoped).
- Six of the seven paths here are **durable state** (failure counter, swarm roster, signal nudges) that survive restarts and must be shared across processes.
- The right answer is `tempfile.gettempdir() / "prismatic"` for scratch (e.g. `antigravity_<id>.log` journal fallback) and an **explicit `PRISMATIC_RUNTIME_DIR` env var** with `tempfile.gettempdir() / "prismatic"` as the default for the durable state.

The plan encodes this distinction (see §1 Decision #2).

### 0d. Missing — what "cross-platform smoke test" actually means
The spec says *"single test that boots the engine on each OS, runs a trivial plugin, and exits cleanly"*. The engine (`prismatic.dispatcher`) is a long-running polling daemon — you don't "boot and exit" it. The right interpretation:

- **Module-level smoke**: import every `prismatic.*` submodule on each OS, instantiate the small public objects, verify no `FileNotFoundError`/`OSError`/`PermissionError` from path operations.
- **End-to-end smoke**: start the file-signal provider in a temp dir, send a nudge, poll it back, ack it, verify state. This is what "runs a trivial plugin" maps to in this codebase (the signal provider is the closest thing to a "trivial plugin" already shipped).

The plan uses the second interpretation (it tests real behavior), but only at module-import smoke if the first one turns out to be heavyweight. See §3 acceptance test.

---

## 1. Architectural Decisions

### Decision 1 — Pathlib refactor scope: **minimal targeted, not blanket**

**Options:**
- **(A) Blanket** — convert every `os.path.join` / `os.path.exists` / `os.path.dirname` to `pathlib` across all 30 files. ~80 sites, ~400 LOC diff, high risk of regression, no functional benefit on Linux.
- **(B) Targeted** — convert only the 6 modules identified in §0a, and only where it enables cross-platform correctness (joining env-driven paths, validating directories before file ops). Touch ~25 sites across 6 files. Low risk, ships the user-visible bug fix.
- **(C) Module-by-module, all usages** — same as (B) but exhaustively (every `os.path.join` → `Path / "x"`, every `os.path.exists(p)` → `Path(p).exists()`). Doubles the diff size with no test-coverage gain.

**Recommendation: (B) Targeted.**
**Why:**
- Linux CI keeps passing (regression test surface is ~297 tests + smoke).
- macOS/Windows CI flips from red → green on the actual bugs.
- Reviewer can read every diff line and reason about it.
- The other 24 files already use env-driven `PRISMATIC_STATE_DIR` paths — they work on macOS/Windows today; they just look like Linux code.

**Trade-off accepted:** `prismatic/` will continue to mix `os.path` and `pathlib`. That's fine — the codebase already does (`admin.py` uses `Path`, `state_machine.py` uses `os.path`). Style mixing is the cost of not rewriting the world.

### Decision 2 — Runtime dir resolution: **explicit env var + `tempfile.gettempdir()` fallback, with scratch vs durable split**

**Options:**
- **(A) Pure `tempfile.gettempdir()` everywhere** — wrong because state-bearing paths (failure counter, swarm roster, nudge dir) need a stable, non-ephemeral location.
- **(B) Pure `PRISMATIC_RUNTIME_DIR` env var, fail if unset** — breaks every existing deploy that doesn't set it.
- **(C) Env var with `tempfile.gettempdir() / "prismatic"` default** — best of both: works out of the box, overridable, cross-platform. Subdivides into:
  - `SCRATCH_DIR = PRISMATIC_RUNTIME_DIR / "scratch"` — for genuinely ephemeral files (e.g. `antigravity_<id>.log`).
  - `STATE_DIR = PRISMATIC_RUNTIME_DIR / "state"` — for durable cross-process state (failure counter, swarm roster, nudge dir, pipeline metrics).

**Recommendation: (C) with the scratch/state split.**
**Why:**
- The 6 problem paths split cleanly: 5 are durable state (counter, roster, health state, vram markers, nudge dir, pipeline metrics), 1 is scratch (journal log fallback).
- Operators on Windows get `%TEMP%\prismatic\` instead of the missing `/tmp/`, with no manual config.
- Existing `PRISMATIC_STATE_DIR` env var stays untouched — that one's for **persisted engine state** (dbs, configs), a different concept.
- macOS sandboxing: `/var/folders/...` (what `tempfile.gettempdir()` returns) is user-scoped and writable; `/tmp/prismatic` is *not* user-scoped on macOS by default — current code is actually broken on a default macOS install.

**Trade-off accepted:** introduces a new env var (`PRISMATIC_RUNTIME_DIR`). Mitigation: default value means nothing changes for current Linux deploys that write to `/tmp/prismatic/...` — those continue to work because `tempfile.gettempdir()` on Linux is `/tmp`.

**Concrete shape:**
```python
# prismatic/runtime_paths.py (new file, ~50 LOC)
from __future__ import annotations
import os
import tempfile
from pathlib import Path

def _runtime_dir() -> Path:
    env = os.environ.get("PRISMATIC_RUNTIME_DIR")
    if env:
        return Path(env)
    return Path(tempfile.gettempdir()) / "prismatic"

RUNTIME_DIR: Path = _runtime_dir()
SCRATCH_DIR: Path = RUNTIME_DIR / "scratch"
STATE_DIR: Path = RUNTIME_DIR / "state"

# Pre-create so first-write doesn't race
for _d in (RUNTIME_DIR, SCRATCH_DIR, STATE_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# Named locations (the 6 problem paths)
PIPELINE_METRICS_PATH: Path = STATE_DIR / "pipeline_metrics.jsonl"
SWARM_NODE_ROSTER: Path = STATE_DIR / "swarm_nodes.json"
WATCHDOG_HEALTH_STATE: Path = STATE_DIR / "distributed_watchdog_state.json"
VRAM_MARKER_DIR: Path = STATE_DIR / "vram"
NUDGE_DIR: Path = STATE_DIR / "nudge"
FAILURE_COUNTER_PATH: Path = STATE_DIR / "failure_counter.json"
JOURNAL_LOG_DIR: Path = SCRATCH_DIR  # antigravity_<id>.log goes here
```

### Decision 3 — CI matrix: **add jobs, not expand the existing one**

**Options:**
- **(A) Single matrix job** — `runs-on: ${{ matrix.os }}` with `os: [ubuntu-latest, macos-latest, windows-latest]`. Faster (parallel), but a single failure blocks all OSes and the matrix hides Linux-specific failures.
- **(B) Three named jobs** — `test-linux`, `test-macos`, `test-windows`. Slower (3× runner spin-up), but each OS gets its own status badge, its own log, and a clear "passes here, fails here" surface. Failure in one OS doesn't noise the others.

**Recommendation: (B) Three named jobs.**
**Why:**
- This is the first time we're testing on these OSes. We **expect** at least one OS to fail on first run. Matrix jobs hide the per-OS signal.
- macOS runners cost more; we want to be able to disable macOS temporarily without losing Linux coverage.
- README badge can show "CI: passing on 3 OSes" with three green checks.

**Trade-off accepted:** ~3× the runner minutes for the CI workflow. Acceptable — this is a single workflow that runs on PR + push.

### Decision 4 — CI bootstrap: **pip-install only, no system packages, no shell scripts beyond what's strictly needed**

**Options:**
- **(A) Replicate the full dev setup** — install OS packages, set up Hermes profiles, seed state dirs.
- **(B) Minimal: `pip install -e ".[dev]"`, run pytest, done.** Anything that needs `~/.antigravity/...` gets a fixture in tests that monkeypatches the path.

**Recommendation: (B) Minimal.**
**Why:**
- 6 modules' worth of cross-platform bugs are all *path bugs* that surface as `OSError`/`FileNotFoundError` at import time or first call. Pure pytest catches them.
- CI doesn't need a working Hermes profile; tests that need one should be skipped on CI (or the path monkeypatched).
- macOS runners default to zsh + system Python; we need to explicitly invoke `python3` and not assume `python` exists (verified: `python` is not on this Linux box either, only `python3`).

**Trade-off accepted:** CI doesn't validate the full Hermes integration stack. That's fine — that's what staging deploys are for. CI validates "the code paths import and run on this OS without OSError".

---

## 2. File Inventory

### Source code (`prismatic/`)

| File | Action | Purpose | LOC |
|---|---|---|---|
| `prismatic/runtime_paths.py` | **CREATE** | Central runtime-dir resolution (Decision #2). Single source of truth for `/tmp/prismatic/...` replacements. | ~55 |
| `prismatic/dispatcher.py` | **MODIFY** | Replace `NUDGE_DIR` and `PIPELINE_METRICS_PATH` defaults to import from `runtime_paths`. Use `pathlib` for `os.path.dirname` / `os.makedirs` calls near those two (~5 sites). | ~25 |
| `prismatic/distributed_watchdog.py` | **MODIFY** | Replace `NODE_ROSTER` / `HEALTH_STATE_PATH` / `VRAM_MARKER_DIR` defaults to import from `runtime_paths`. Use `Path.mkdir(parents=True, exist_ok=True)` instead of `os.makedirs` (~3 sites). | ~20 |
| `prismatic/providers/signals/file.py` | **MODIFY** | `FileSignalProvider.__init__` default → `"nudge"` (relative) with module-level constant imported from `runtime_paths.NUDGE_DIR`. Update docstrings that hardcode `/tmp/prismatic/nudge-{target}` → reference the constant. | ~15 |
| `prismatic/providers/signals/__init__.py` | **MODIFY** | Two config-template defaults (`/tmp/prismatic` literal in dicts) → use the module-level constant. | ~5 |
| `prismatic/quality/failure.py` | **MODIFY** | `COUNTER_PATH` → import from `runtime_paths.FAILURE_COUNTER_PATH` (kept as `str` for backward-compat with the test that does `monkeypatch.setattr("...COUNTER_PATH", ...)` — we coerce to `str()`). | ~5 |
| `prismatic/journal.py` | **MODIFY** | `Path(f"/tmp/antigravity_{issue_identifier}.log")` → `runtime_paths.JOURNAL_LOG_DIR / f"antigravity_{issue_identifier}.log"`. | ~5 |
| `prismatic/agents/hermes.py` | **MODIFY** | `PRISMATIC_NUDGE_DIR` env var default in the agent config → fall back to `runtime_paths.NUDGE_DIR`. | ~3 |

**Total source LOC delta:** ~133 (mostly the new `runtime_paths.py`).

### Tests (`tests/`)

| File | Action | Purpose | LOC |
|---|---|---|---|
| `tests/test_runtime_paths.py` | **CREATE** | Unit tests for `prismatic.runtime_paths`. 4 tests. | ~60 |
| `tests/test_cross_platform_smoke.py` | **CREATE** | The cross-platform smoke test. Imports each of the 6 modified modules, exercises the file-path code path, verifies no `OSError`. This is the test that gates the CI matrix green. | ~80 |
| `tests/test_pipeline_metrics_path.py` | **CREATE** | Verifies `PIPELINE_METRICS_PATH` is writable, parent dir auto-created. | ~25 |
| `tests/test_distributed_watchdog_paths.py` | **CREATE** | Verifies `NODE_ROSTER`, `HEALTH_STATE_PATH`, `VRAM_MARKER_DIR` honor env-override + sane defaults. Reuses existing `tmp_path` fixtures. | ~60 |
| `tests/test_file_signal_provider_path.py` | **CREATE** | Verifies `FileSignalProvider` works with `tmp_path` directory (not `/tmp/prismatic`). | ~40 |
| `tests/test_failure_counter_path.py` | **CREATE** | Verifies `COUNTER_PATH` is now under `tempfile.gettempdir()` (or env override). | ~30 |

**Total test LOC:** ~295 new.

### Specs/docs (`okf/`)

| File | Action | Purpose | LOC |
|---|---|---|---|
| `okf/operations/phase4-gap13-shipped-2026-06-28.md` | **CREATE** | Ship log: what landed, what was deferred, deviations from this plan. | ~40 |

### Config (`.github/`, `pyproject.toml`)

| File | Action | Purpose | LOC |
|---|---|---|---|
| `.github/workflows/ci.yml` | **CREATE** | New CI workflow: 3 named jobs (Linux, macOS, Windows). Triggers on PR + push to `main`/`deploy-fresh`. Runs `pytest tests/` (Linux only runs full suite including plugin-load; macOS/Windows run the smoke + runtime-path tests since plugin-load currently checks Linux-only paths — see §3 note). | ~70 |
| `.github/workflows/plugin-load.yml` | **MODIFY** | Add a single line documenting that it only runs on Linux (plugin-load gate is a Linux runtime feature; cross-platform plugin load is out of scope for Gap 13). Actually: leave untouched — it's Linux-only by design (Ubuntu runner). Add a comment to the workflow file. | ~3 |
| `pyproject.toml` | **MODIFY** | No changes needed for runtime, but add a comment near `dependencies` noting `tempfile` is stdlib (no new dep). Add `pytest>=7` to `[project.optional-dependencies].dev` if not already there. | ~5 |

**Total config LOC:** ~78.

### Files NOT touched (deliberate)

- `prismatic/admin.py` — already uses `pathlib.Path`; `os.path.expanduser("~")` works on all 3 OSes.
- `prismatic/billing/*`, `prismatic/gateway/*`, `prismatic/state_machine.py`, `prismatic/credit_tracker.py`, `prismatic/telemetry.py`, `prismatic/vertex_telemetry.py`, `prismatic/dispatcher.py:668+` (most of dispatcher) — use `PRISMATIC_STATE_DIR` env var; already cross-platform. Not in scope.
- `prismatic/quality/smoke.py:163,176` — the `Path(path) if os.path.isabs(path) else Path(workdir) / path` pattern is already cross-platform-correct. Not in scope.
- `prismatic/quality/gates.py:191,632` — `Path(os.path.normpath(f)).resolve()` is fine on all OSes. Not in scope.

---

## 3. Test Plan

**Target: ~12 new tests, organized as follows.** Total: **13 tests** (one over because the smoke test naturally splits into "import smoke" and "end-to-end smoke").

### Unit tests (`tests/test_runtime_paths.py`, `tests/test_pipeline_metrics_path.py`, `tests/test_failure_counter_path.py`)

| Test | Verifies | LOC |
|---|---|---|
| `test_runtime_dir_uses_tempdir_by_default` | With no env vars set, `RUNTIME_DIR` is a child of `tempfile.gettempdir()`. | ~10 |
| `test_runtime_dir_respects_env_override` | With `PRISMATIC_RUNTIME_DIR=/foo` set, all derived paths live under `/foo`. | ~10 |
| `test_scratch_and_state_dirs_created` | `SCRATCH_DIR` and `STATE_DIR` exist after import (idempotent). | ~8 |
| `test_pipeline_metrics_path_under_state_dir` | `PIPELINE_METRICS_PATH` is under `STATE_DIR`, parent auto-created on first write. | ~15 |
| `test_failure_counter_path_under_state_dir` | `COUNTER_PATH` is under `STATE_DIR` (or `PRISMATIC_RUNTIME_DIR`). | ~12 |
| `test_journal_log_dir_under_scratch_dir` | `JOURNAL_LOG_DIR` is under `SCRATCH_DIR`. | ~8 |

### Per-module tests (`tests/test_distributed_watchdog_paths.py`, `tests/test_file_signal_provider_path.py`)

| Test | Verifies | LOC |
|---|---|---|
| `test_distributed_watchdog_state_path_writable` | `HEALTH_STATE_PATH` is writable via `tmp_path` override. | ~15 |
| `test_distributed_watchdog_vram_marker_dir_writable` | `VRAM_MARKER_DIR` accepts a temp dir; cleanup works. | ~20 |
| `test_distributed_watchdog_creates_parent_dirs` | First-write to `HEALTH_STATE_PATH` succeeds even when `STATE_DIR` doesn't pre-exist. | ~15 |
| `test_file_signal_provider_send_poll_ack_in_tmpdir` | Full `send → poll → ack` round-trip with `FileSignalProvider(directory=tmp_path)`. Proves nudge mechanism works in any temp dir, not just `/tmp/prismatic`. | ~30 |

### Integration tests

| Test | Verifies | LOC |
|---|---|---|
| `test_dispatcher_nudge_dir_resolves_cross_platform` | With `PRISMATIC_RUNTIME_DIR` unset, `NUDGE_DIR` is under `tempfile.gettempdir()`. With it set, `NUDGE_DIR` honors the override. | ~20 |

### Acceptance test (`tests/test_cross_platform_smoke.py`)

| Test | Verifies | LOC |
|---|---|---|
| `test_cross_platform_smoke` | **Single end-to-end smoke.** (1) Imports all 6 modified modules without `OSError`. (2) Calls the public entry point of each (`FileSignalProvider(...).send/poll/ack`, `log_completed_pipeline_metrics(...)`, `NodeRegistry.register_node(...)`, `_load_counter()` / `_save_counter()`, `validate_agent_output(issue_identifier="smoke-test")`). (3) Verifies exit with no exceptions, all temp files cleaned up or located under `tmp_path`. This is the test the CI matrix runs on all 3 OSes. | ~60 |

**Total: 13 tests, ~243 LOC.**

### Note on which tests run on which OS

- All tests run on Linux (existing CI).
- All tests **except** plugin-load run on macOS + Windows.
- The plugin-load gate (`.github/workflows/plugin-load.yml`) stays Linux-only because the `prismatic-hello-world` plugin doesn't have Windows-path-tested paths. Adding cross-platform plugin load is Gap 13.5.

---

## 4. Implementation Sequencing

Four phases. Each is independently shippable as one PR, each has its own tests, and the order is chosen so earlier phases enable later ones to be reviewed against a working baseline.

### Phase 1: Foundation — `runtime_paths.py` + its tests

**Files touched:**
- `prismatic/runtime_paths.py` (CREATE, ~55 LOC)
- `tests/test_runtime_paths.py` (CREATE, ~60 LOC)
- `tests/test_pipeline_metrics_path.py` (CREATE, ~25 LOC)
- `tests/test_failure_counter_path.py` (CREATE, ~30 LOC)
- `tests/test_journal_log_dir_under_scratch_dir` is in `test_runtime_paths.py`

**Tests added:** 6 unit tests
**Approx duration:** ~20 min (Sonnet)
**PR title:** `Gap 13 Phase 1: introduce prismatic.runtime_paths module`
**Risk:** None — adds a new module, doesn't change behavior of anything yet.

### Phase 2: Wire `runtime_paths` into the 6 modules

**Files touched:**
- `prismatic/dispatcher.py` (MODIFY, ~25 LOC)
- `prismatic/distributed_watchdog.py` (MODIFY, ~20 LOC)
- `prismatic/providers/signals/file.py` (MODIFY, ~15 LOC)
- `prismatic/providers/signals/__init__.py` (MODIFY, ~5 LOC)
- `prismatic/quality/failure.py` (MODIFY, ~5 LOC)
- `prismatic/journal.py` (MODIFY, ~5 LOC)
- `prismatic/agents/hermes.py` (MODIFY, ~3 LOC)
- `tests/test_distributed_watchdog_paths.py` (CREATE, ~60 LOC)
- `tests/test_file_signal_provider_path.py` (CREATE, ~40 LOC)
- `tests/test_cross_platform_smoke.py` (CREATE, ~80 LOC)

**Tests added:** 5 unit + integration + 1 acceptance = 7 tests
**Approx duration:** ~45 min (Sonnet)
**PR title:** `Gap 13 Phase 2: replace /tmp/ defaults with runtime_paths; cross-platform smoke`
**Risk:** Medium. Backward-compat check needed for `COUNTER_PATH` (test_failure.py does `monkeypatch.setattr` on the string). See §5.

### Phase 3: CI matrix

**Files touched:**
- `.github/workflows/ci.yml` (CREATE, ~70 LOC)
- `.github/workflows/plugin-load.yml` (MODIFY, +3 LOC comment)

**Tests added:** None (config only)
**Approx duration:** ~15 min (Sonnet)
**PR title:** `Gap 13 Phase 3: CI matrix for Linux + macOS + Windows`
**Risk:** Low. Workflow YAML is easy to verify. macOS/Windows runners may surface Linux-only behavior we missed (e.g. `signal.SIGTERM` handling differences); budget for one round-trip fix.

### Phase 4: Ship log + meta-review

**Files touched:**
- `okf/operations/phase4-gap13-shipped-2026-06-28.md` (CREATE, ~40 LOC)
- `phase4-tracker-2026-06-28.md` (MODIFY, mark Gap 13 row as ✅)

**Tests added:** None
**Approx duration:** ~10 min
**PR title:** `Gap 13 Phase 4: ship log + tracker update`

---

## 5. Risks and Mitigations

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| **R1** | `COUNTER_PATH` is currently a `str`. The test file does `monkeypatch.setattr("prismatic.quality.failure.COUNTER_PATH", str(counter_file))` — works with both `str` and `Path` because `setattr` just replaces the attribute, but downstream `open(COUNTER_PATH, "r")` requires a `str`-coercible. | Medium | Test failure in `tests/quality/test_failure.py` (17 monkeypatch sites). | In `failure.py`, keep `COUNTER_PATH` typed as `str` for backward compat: `COUNTER_PATH: str = str(runtime_paths.FAILURE_COUNTER_PATH)`. Same pattern for `NUDGE_DIR` (used as string concat in dispatcher config). Document in code comment. |
| **R2** | `tempfile.gettempdir()` on macOS returns `/var/folders/.../T/` (per-user ephemeral). Existing deploys that rely on multiple processes sharing `/tmp/prismatic/` will get *different* dirs per user. | High | `FileSignalProvider` (writer in one process, reader in another) breaks if both run as the same user → still works. But if one runs as root and one as user → broken. | Document `PRISMATIC_RUNTIME_DIR` env var in the new module's docstring. Default behavior works for single-user deploys (which is the common case). |
| **R3** | CI macOS runner is x86_64 by default (sometimes arm64). Some pure-Python libs work; anything with C extensions (e.g. `cryptography`) might not. Current `pyproject.toml` has zero C-extension deps, so we're fine — but if a future PR adds one, CI silently flips red. | Low | macOS CI breaks unexpectedly later. | Phase 3 PR includes a comment in `ci.yml` listing the "no C-extension deps" invariant. Add a CI lint step that runs `python -c "import sys; print(sys.platform)"` and asserts macOS arm64 vs x86_64 to catch runner changes. |
| **R4** | `prismatic.journal.py` line 998 has `Path(f"/tmp/antigravity_{issue_identifier}.log")` as a fallback when `log_path` is None and `issue_identifier` is set. If `validate_agent_output` is called from production code without setting `log_path`, this writes to a real file on Linux (`/tmp/antigravity_<id>.log`) but a different location on macOS/Windows. Existing behavior change. | Medium | Unexpected file in different location on macOS/Windows. Existing callers may grep for `/tmp/antigravity_*.log` paths. | Add a test that asserts the journal fallback path is under `JOURNAL_LOG_DIR`. Update the docstring of `validate_agent_output` to call out the env-driven location. |
| **R5** | Sonnet might try to also do the pathlib refactor on the 24 out-of-scope files ("while I'm in there"). This blows up PR size and review time. | High | Plan adherence drift. | Explicit "Files NOT touched" list in §2. Reviewer (Sonnet peer) should reject any PR that touches files outside the inventory. |

---

## 6. Sprint 1 Dependencies

This gap depends on **zero new APIs from Sprint 1**. It is a refactor of existing code, not an integration with new features. Specifically:

- **Gap 10 (plugin auto-discovery)** — unchanged. Plugin load gate stays Linux-only.
- **Gap 11 (impact/action rule separation + hook dispatch)** — unchanged.
- **Gap 12 (telemetry tables)** — unchanged. Telemetry files use `PRISMATIC_STATE_DIR`, already cross-platform.
- **Gap 13 Sprint 1 (ship-time plugin load gate)** — **different file, same number.** The Sprint 1 Gap 13 is `gap13-plugin-load-gate-spec-2026-06-29.md` (ship-time plugin verification gate). The Phase 4 Gap 13 is `phase4-gap13-...` (cross-platform compat). They are orthogonal:
  - Sprint 1 Gap 13 depends on `pyproject.toml` core version → Linux-only runner.
  - Phase 4 Gap 13 depends on `pathlib` and `tempfile` stdlib → cross-platform by design.
  - They do not share code paths. Phase 4 Gap 13's `runtime_paths.py` does NOT import from `prismatic/quality/plugin_load.py`.

**Symbol stability:**
- `prismatic.dispatcher.NUDGE_DIR`, `PIPELINE_METRICS_PATH` — **public, used by `prismatic/agents/hermes.py` and dispatcher internals**. Will keep the same name, just sourced from `runtime_paths`. No breakage.
- `prismatic.quality.failure.COUNTER_PATH` — **public, monkeypatched in 17 tests**. Will keep the same name. Type stays `str`. No breakage.
- `prismatic.distributed_watchdog.NODE_ROSTER`, `HEALTH_STATE_PATH`, `VRAM_MARKER_DIR` — **public, used by `scripts/`** (need to verify but unlikely). Keep the same names. No breakage.

**What happens if a Sprint 1 API changes during Phase 4:**
- Sprint 1 is `deploy-fresh` HEAD. It's frozen.
- The 4 Sprint 1 PRs (Gaps 10/11/12/13) already shipped. No mid-Phase-4 churn expected.

---

## 7. Acceptance Criteria

The gap is **DONE** when **all** of the following are true:

### Code state
- [ ] `prismatic/runtime_paths.py` exists and exports: `RUNTIME_DIR`, `SCRATCH_DIR`, `STATE_DIR`, `PIPELINE_METRICS_PATH`, `SWARM_NODE_ROSTER`, `WATCHDOG_HEALTH_STATE`, `VRAM_MARKER_DIR`, `NUDGE_DIR`, `FAILURE_COUNTER_PATH`, `JOURNAL_LOG_DIR`.
- [ ] All 6 modules identified in §0a import from `runtime_paths` for their default paths. **No literal `/tmp/` string remains as a default in any of these 6 files.** (Docstrings may still reference `/tmp/` for historical context — that's fine.)
- [ ] `prismatic/quality/failure.py:COUNTER_PATH` is `str`, not `Path`. Backward compat with `monkeypatch.setattr` preserved.
- [ ] `prismatic/providers/signals/file.py:FileSignalProvider.__init__` default directory is the `NUDGE_DIR` from `runtime_paths`, not the literal string `"/tmp/prismatic"`.

### Test state
- [ ] 13 new tests pass on Linux (`pytest tests/test_runtime_paths.py tests/test_pipeline_metrics_path.py tests/test_failure_counter_path.py tests/test_distributed_watchdog_paths.py tests/test_file_signal_provider_path.py tests/test_cross_platform_smoke.py -v`).
- [ ] All 297 existing tests still pass on Linux.
- [ ] CI matrix (`.github/workflows/ci.yml`) runs and is **green** on: `ubuntu-latest`, `macos-latest`, `windows-latest`.
- [ ] `tests/test_cross_platform_smoke.py::test_cross_platform_smoke` passes on all 3 OSes (this is the gate).
- [ ] Any platform-specific test that must be skipped on Windows (e.g. signal handling) is marked `@pytest.mark.skipif(sys.platform == "win32", reason="...")` — not deleted.

### Documentation state
- [ ] `prismatic/runtime_paths.py` module docstring explains the `PRISMATIC_RUNTIME_DIR` env var + the `scratch`/`state` split.
- [ ] `okf/operations/phase4-gap13-shipped-2026-06-28.md` exists with: what shipped, what was deferred, any deviations from this plan, and the CI matrix green-check evidence (links to 3 successful workflow runs).
- [ ] `phase4-tracker-2026-06-28.md` updated to mark Gap 13 row ✅.
- [ ] `README.md` mentions supported platforms (Linux, macOS, Windows). If it currently says "Linux only", update to "Linux, macOS, Windows" with a one-liner about the cross-platform test matrix.

### Edge cases handled
- [ ] First-write to `STATE_DIR`-derived paths works even if `STATE_DIR` doesn't pre-exist (verified by `test_distributed_watchdog_creates_parent_dirs`).
- [ ] `tempfile.gettempdir()` on macOS doesn't cause permission errors (verified by smoke test passing on macOS runner).
- [ ] Windows backslash path separators don't break file comparisons (verified by Windows runner smoke passing).
- [ ] `COUNTER_PATH` monkeypatching in existing tests still works (verified by full `pytest tests/quality/test_failure.py` passing).
- [ ] On macOS, `FileSignalProvider` round-trips a nudge in `<1 second` (regression check vs. current Linux behavior).

### Out-of-scope, explicitly NOT acceptance criteria
- ❌ All `os.path` usages in `prismatic/` converted to `pathlib`. (Only the 6 modules per §0a.)
- ❌ Plugin-load gate runs on macOS/Windows.
- ❌ `prismatic/agents/hermes.py` does not crash on a fresh macOS install.
- ❌ `prismatic/dispatcher.py` boots and runs a full polling cycle on macOS/Windows. (That's Gap 13.5 — first real production cross-platform validation, needs Hermes profile setup.)

---

## Appendix A — Exact line numbers for the 6 modules

For Sonnet's reference. These are the lines to change (verified 2026-06-28):

```
prismatic/dispatcher.py:
  L94:  NUDGE_DIR default → runtime_paths.NUDGE_DIR
  L97-99: PIPELINE_METRICS_PATH default → runtime_paths.PIPELINE_METRICS_PATH
  L194-196: os.path.dirname(PIPELINE_METRICS_PATH) → Path(PIPELINE_METRICS_PATH).parent; os.makedirs → Path.mkdir
  L102-106: AGY_CONFIG_PATH — already uses HOME env var, cross-platform OK, NO CHANGE

prismatic/distributed_watchdog.py:
  L60-63: NODE_ROSTER default → runtime_paths.SWARM_NODE_ROSTER
  L66-69: HEALTH_STATE_PATH default → runtime_paths.WATCHDOG_HEALTH_STATE
  L72-75: VRAM_MARKER_DIR default → runtime_paths.VRAM_MARKER_DIR
  L20-22, L461: docstring references to /tmp/prismatic/... — UPDATE to "PRISMATIC_RUNTIME_DIR (default: tempfile.gettempdir()/prismatic)"

prismatic/providers/signals/file.py:
  L48: __init__(directory: str = "/tmp/prismatic") → __init__(directory: str | os.PathLike = runtime_paths.NUDGE_DIR)
  L5, L11, L17-19, L43: docstring updates to reference NUDGE_DIR

prismatic/providers/signals/__init__.py:
  L34, L44, L121: "/tmp/prismatic" literal in 3 places → runtime_paths.NUDGE_DIR (or str() of it for dict keys)

prismatic/quality/failure.py:
  L230: COUNTER_PATH = "/tmp/failure_counter.json" → COUNTER_PATH: str = str(runtime_paths.FAILURE_COUNTER_PATH)
  L256: Path(COUNTER_PATH).parent.mkdir → unchanged (already pathlib-aware)

prismatic/journal.py:
  L998: Path(f"/tmp/antigravity_{issue_identifier}.log") → runtime_paths.JOURNAL_LOG_DIR / f"antigravity_{issue_identifier}.log"

prismatic/agents/hermes.py:
  L61: os.environ.get("PRISMATIC_NUDGE_DIR", "/tmp/prismatic") → os.environ.get("PRISMATIC_NUDGE_DIR", str(runtime_paths.NUDGE_DIR))
```

## Appendix B — The exact `ci.yml` skeleton

For Sonnet's reference. Three named jobs sharing the same test command:

```yaml
name: CI

on:
  pull_request:
  push:
    branches: [main, deploy-fresh]

jobs:
  test-linux:
    name: Test (Linux)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: "3.12"}
      - run: pip install -e ".[dev]"
      - run: pytest tests/ -v --tb=short

  test-macos:
    name: Test (macOS)
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: "3.12"}
      - run: pip install -e ".[dev]"
      # Skip plugin-load tests on macOS — they assert Linux-only paths
      - run: pytest tests/ -v --tb=short --ignore=tests/test_plugin_load_gate.py

  test-windows:
    name: Test (Windows)
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: "3.12"}
      - run: pip install -e ".[dev]"
      - run: pytest tests/ -v --tb=short --ignore=tests/test_plugin_load_gate.py
```

---

## Appendix C — What "Done" looks like for the Sonnet implementer

Checklist Sonnet should walk through before opening the PR:

1. `cat prismatic/runtime_paths.py` — module exists, exports the 10 named paths.
2. `grep -rn "/tmp/" prismatic/dispatcher.py prismatic/distributed_watchdog.py prismatic/providers/signals/ prismatic/quality/failure.py prismatic/journal.py prismatic/agents/hermes.py` — only docstring/historical references remain, no path defaults.
3. `pytest tests/ -v` on Linux — all 297+13 = 310 tests green.
4. `pytest tests/ -v --ignore=tests/test_plugin_load_gate.py` on macOS (locally if possible, or trust CI) — green.
5. Push to branch, CI matrix runs, all 3 OSes green.
6. Open PR with the 4-phase breakdown as the description.

---

**End of plan. Ready for Sonnet implementation. Peer review (Sonnet) gates the PR.**