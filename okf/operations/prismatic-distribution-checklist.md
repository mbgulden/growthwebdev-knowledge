# Prismatic Engine — Distribution Checklist

**Status:** **PARTIAL** — shipped core works on Linux; Windows + macOS untested
**Last verified:** 2026-06-28
**Scope:** Gap 9 / Part B — make Prismatic Engine portable, distributable, plugin-friendly

---

## What This Document Is

A verification gate for "enterprise level distribution ready." The Prismatic Engine must:
1. Install cleanly on any major platform (Linux, macOS, Windows)
2. Expose a stable public API surface
3. Accept plugins via standard Python entry-points
4. Run standalone (no Hermes/AGY required)
5. Use platform-portable path conventions

This checklist is run before declaring Gap 9 done.

---

## ✅ Currently Passing

### 1. Installable as a Python package

```toml
# pyproject.toml — already shipped
[build-system]
requires = ["setuptools>=64", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "prismatic-engine"
version = "0.2.0"
requires-python = ">=3.10"

[project.scripts]
prismatic-engine = "prismatic.dispatcher:main"
prismatic-engine-skills = "prismatic.skills:cli_skills"
prismatic-lock = "prismatic.lock:main"
prismatic-admin = "prismatic.admin:main"
prismatic-gateway = "prismatic.gateway.server:main"
prismatic-api = "prismatic.api.server:run"
```

**Verified:** `python3 -c "import prismatic; print(prismatic.__version__)"` works (Python 3.12).

**Status:** ✅ Linux Python 3.10–3.13 (declared in classifiers).

### 2. Public API surface complete

```python
from prismatic.review import (
    # Contracts
    PRReviewer, PRReviewResult, StubPRReviewer, RealPRReviewer,
    # Pipeline
    PipelineDecision, PipelineOrchestrator, ReworkPayload,
    build_rework_payload, classify_impact, decide_next_action,
    # Plugin extension (Gap 9 / Part B)
    ReviewerRegistry, ComposedReviewerSpec, SecretPattern,
    QualityCheck, ImpactRule,
    HOOK_BEFORE_SECRET_SCAN, HOOK_BEFORE_QUALITY_CHECKS,
    HOOK_BEFORE_CLASSIFY_IMPACT, HOOK_BEFORE_DECIDE_ACTION,
    HOOK_BEFORE_NED_REVIEW, ALL_HOOKS,
    # Constants
    APPROVE, REQUEST_CHANGES, NEEDS_DISCUSSION,
    ACTION_ADVANCE, ACTION_HOLD, ACTION_REWORK, ACTION_GIVE_UP,
    IMPACT_TRIVIAL, IMPACT_MINOR, IMPACT_MAJOR, IMPACT_BLOCKER,
    DEFAULT_MAX_REWORK_ATTEMPTS, IMPACT_RANK, IMPACT_LEVELS, ACTIONS,
)
```

**Status:** ✅ All symbols importable, well-typed, documented.

### 3. Plugin entry-points declared

```toml
# pyproject.toml — Gap 9 / Part B
[project.entry-points."prismatic.plugins"]
# (Empty by default — external plugins register themselves.)
```

Third-party plugins register via:
```toml
# Their pyproject.toml
[project.entry-points."prismatic.plugins"]
my_plugin = "my_pkg:register"
```

**Status:** ✅ Group declared; resolver call works (verified locally).

### 4. Standalone runtime

```python
# Engine runs without Hermes/AGY:
from prismatic.review import RealPRReviewer, PipelineOrchestrator
reviewer = RealPRReviewer()
orchestrator = PipelineOrchestrator()
result = reviewer.review_pr("https://github.com/o/r/pull/1")
decision = orchestrator.process(identifier="GRO-1", pr_url="...", result=result)
```

**Status:** ✅ No Hermes or AGY imports anywhere in the review subsystem.

### 5. Test suite passes

```bash
$ python3 -m pytest prismatic/
============================= 247 passed in 0.45s ==============================
```

**Status:** ✅ 247/247 passing (54 Phase 1 + 40 Gap 5 + 52 Gap 7 + 38 Gap 4 + 30 Gap 8 + 7 trigger_ned_review + 26 registry/hooks).

---

## ⚠️ Known Issues (Track for Gap 10+)

### Issue A: `os.path.join` calls in core modules

**Files affected:**
- `prismatic/run_records.py:51` — `os.path.join(state_dir, "run_records.json")`
- `prismatic/sandbox/pod_manager.py:41, 329` — sandbox workspace paths
- `prismatic/core/router.py:37` — DB path
- `prismatic/distributed_watchdog.py` — uses `/tmp/prismatic/...` and `/home/ubuntu/...` as defaults

**Risk:** Breaks on Windows (path separator is `\` not `/`).

**Mitigation:** `pathlib.Path` handles cross-platform paths. Refactor to use `Path(state_dir) / "run_records.json"` etc.

**Priority:** Medium. Fix as part of Gap 10 ("Windows compatibility pass").

### Issue B: Hardcoded Unix paths

**Files affected:**
- `prismatic/distributed_watchdog.py:30, 56, 62, 68` — `/tmp/...`, `/home/ubuntu/...`

**Risk:** Breaks on Windows where `/tmp/` doesn't exist.

**Mitigation:** Use `tempfile.gettempdir()` + `Path.home()` instead.

**Priority:** Medium. Fix as part of Gap 10.

### Issue C: Plugin discovery not yet wired

**Status:** The `prismatic.plugins` entry-point group is **declared** but the **consumer** (in `prismatic.core.registry.PluginLoader` or wherever startup-time plugin discovery happens) is **not yet wired** to query this group.

**Risk:** A plugin installed via `pip install my-plugin` will not auto-register. Plugin authors must still call `ReviewerRegistry.register_*()` manually.

**Mitigation:** Add startup hook in `prismatic.dispatcher.main()`:
```python
from importlib.metadata import entry_points
for ep in entry_points(group="prismatic.plugins"):
    register_fn = ep.load()
    register_fn(registry)
```

**Priority:** High — this is the gap between "plugin group exists" and "plugins actually work." Track for Gap 10.

### Issue D: No CI matrix for Windows/macOS

**Status:** Only Linux CI runs. No `windows-latest` or `macos-latest` jobs in `.github/workflows/`.

**Risk:** Regressions on non-Linux platforms ship without detection.

**Mitigation:** Add to `.github/workflows/test.yml`:
```yaml
strategy:
  matrix:
    os: [ubuntu-latest, macos-latest, windows-latest]
    python-version: ["3.10", "3.11", "3.12", "3.13"]
```

**Priority:** Low — manual Windows validation can ship first; CI matrix is polish.

### Issue E: No signed plugin verification

**Status:** No signature check on plugin code.

**Risk:** Supply-chain attack via malicious plugin.

**Mitigation:** Defer to Gap 10+ (security track). For now, document in README that plugins run with full Python privileges.

---

## 🧪 Verification Commands

Run these to validate distribution readiness after any change:

```bash
# 1. Install in editable mode (validates pyproject.toml)
pip install -e .[all]

# 2. Verify entry-points resolve
python3 -c "
from importlib.metadata import entry_points
eps = entry_points(group='prismatic.plugins')
print(f'Plugin entry-points resolvable: {len(list(eps))}')
"

# 3. Verify public API surface
python3 -c "
from prismatic.review import (
    ReviewerRegistry, ComposedReviewerSpec,
    HOOK_BEFORE_NED_REVIEW, ALL_HOOKS,
    RealPRReviewer, PipelineOrchestrator,
)
r = ReviewerRegistry()
spec = r.compose()
print(f'Registry works: secret_patterns={len(spec.secret_patterns)} checks={len(spec.checks)}')
print(f'Hooks registered: {len(ALL_HOOKS)}')
"

# 4. Run full test suite
python3 -m pytest prismatic/

# 5. Verify no shell-only assumptions (Path-only filesystem ops)
grep -rn "os.path.join\|os.sep" prismatic/review/ prismatic/quality/
# Should return zero hits in the review + quality subsystems (which ship
# in 0.2.0). Other subsystems are tracked under Issue A.

# 6. Verify entry-point group exists
grep "prismatic.plugins" pyproject.toml
# Should show the [project.entry-points."prismatic.plugins"] section.
```

---

## Definition of Done — Gap 9

Gap 9 / Part B is **DONE** when:
- ✅ Public API surface exported from `prismatic.review`
- ✅ Plugin registry API (`ReviewerRegistry`) implemented with frozen snapshots
- ✅ Hook constants defined and documented
- ✅ `RealPRReviewer` and `PipelineOrchestrator` accept optional `registry` param
- ✅ pyproject.toml declares `prismatic.plugins` entry-point group
- ✅ Version bumped to 0.2.0
- ✅ 247/247 tests passing
- ⏳ Plugin auto-discovery consumer wired (Gap 10)
- ⏳ Windows + macOS CI matrix (Gap 10)
- ⏳ `os.path.join` → `pathlib.Path` refactor (Gap 10)

---

## References

- Phase 2 implementation tracker: `okf/operations/phase2-quality-gates-implementation.md`
- Gap 9 second opinion (design rationale): `okf/operations/phase2-quality-gates-plan.md` Gap 9 section
- Plugin contract: `prismatic/interface/plugin.py` (existing PrismaticPlugin ABC)
- Existing plugins: `plugins/` directory (9 examples: hermes-plugin-*, pwp, example_plugin)