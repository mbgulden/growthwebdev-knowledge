# Gap 12 — Post-Sonnet Integration Checklist

**Date:** 2026-06-28
**Gap:** Phase 3 / Sprint 1 / Gap 12 (Observability — extends `prismatic/telemetry.py`)
**Owner:** Fred (orchestrator)

## Pre-merge verification (run these BEFORE opening PR)

### 1. File inventory
- [ ] `prismatic/telemetry.py` has 4 new `record_*` methods: `record_review_completed`, `record_plugin_registered`, `record_hook_fired`, `record_pipeline_action`
- [ ] `prismatic/observability/__init__.py` exists (NEW, may be empty)
- [ ] `prismatic/observability/ops_feed.py` exists (NEW, exports `post_review_event_to_linear`)
- [ ] `prismatic/test_telemetry_extension.py` exists (NEW)
- [ ] `prismatic/observability/test_ops_feed.py` exists (NEW)
- [ ] NO out-of-lane files modified (verify with `git diff --name-only origin/deploy-fresh`)

### 2. Tests
- [ ] `python3 -m pytest prismatic/` shows 273/273 (was 250 + 23 new)
- [ ] `python3 -m pytest prismatic/test_telemetry_extension.py -v` shows 17 passing
- [ ] `python3 -m pytest prismatic/observability/test_ops_feed.py -v` shows 6 passing
- [ ] `python3 -m pytest prismatic/test_cost_attribution.py` still passes (regression check)

### 3. Lint + format
- [ ] `ruff check prismatic/` clean (no errors)
- [ ] `ruff format --check prismatic/` clean (no diffs)

### 4. Live verification probes (run these in Python REPL)

```python
# Probe 1: Methods exist
from prismatic.telemetry import get_collector
c = get_collector()
for m in ["record_review_completed", "record_plugin_registered", "record_hook_fired", "record_pipeline_action"]:
    assert hasattr(c, m), f"missing method: {m}"
print("PASS: 4 record_* methods exist")

# Probe 2: ops_feed imports
from prismatic.observability.ops_feed import post_review_event_to_linear
from prismatic.providers.tasks.linear import LinearTaskProvider
assert callable(post_review_event_to_linear)
print("PASS: ops_feed imports + LinearTaskProvider reference")

# Probe 3: Dashboard extension
data = c.get_dashboard_data(hours=1)
assert "review" in data, f"missing review block: {list(data.keys())}"
assert "hooks" in data
assert "plugins" in data
print(f"PASS: dashboard has review/hooks/plugins blocks. Review: {data['review']}")

# Probe 4: Tables exist (after first insert triggers _ensure_tables)
c.record_review_completed(
    run_id="probe", issue_id="probe", reviewer="probe",
    verdict="approve", impact="trivial"
)
import time; time.sleep(0.5)  # let daemon drain
import sqlite3, os
db_path = os.environ.get("PRISMATIC_STATE_DIR", "./prismatic_state") + "/event_router.db"
conn = sqlite3.connect(db_path)
for table in ["telemetry_review_completed", "telemetry_plugin_registered", "telemetry_hook_fired", "telemetry_pipeline_action"]:
    cursor = conn.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
    assert cursor.fetchone() is not None, f"missing table: {table}"
print("PASS: 4 new tables exist in event_router.db")
conn.close()

# Probe 5: ops_feed end-to-end (no Linear key, expect graceful fallback)
result = post_review_event_to_linear(
    issue_id="probe",
    event_type="review.completed",
    payload={"run_id": "probe", "verdict": "approve"},
)
assert result is False  # no key → returns False, no crash
print("PASS: ops_feed handles missing key gracefully")

# Probe 6: ops_feed invalid event type
result = post_review_event_to_linear(
    issue_id="probe",
    event_type="bogus.event",
    payload={},
)
assert result is False
print("PASS: ops_feed rejects invalid event_type")

# Probe 7: ops_feed uses Pattern B (LinearTaskProvider), NOT curl
import inspect
from prismatic import observability
src = inspect.getsource(observability.ops_feed)
assert "LinearTaskProvider" in src, "ops_feed should use LinearTaskProvider"
assert "subprocess" not in src and "curl" not in src, "ops_feed should NOT use curl subprocess"
print("PASS: ops_feed uses Pattern B (LinearTaskProvider)")
```

All 7 probes should print `PASS:`. If any fails, the implementation is incomplete.

### 5. Lane check (forbidden modifications)

Run `git diff --name-only origin/deploy-fresh`:

✅ **Expected in diff:**
- `prismatic/telemetry.py`
- `prismatic/observability/__init__.py` (NEW)
- `prismatic/observability/ops_feed.py` (NEW)
- `prismatic/test_telemetry_extension.py` (NEW)
- `prismatic/observability/test_ops_feed.py` (NEW)
- `okf/operations/gap12-implementation-lessons.md` (NEW, written after merge)

❌ **Forbidden (would block push):**
- `prismatic/review/pr_reviewer_impl.py` (Ned lane — Gap 11)
- `prismatic/review/pipeline.py` (Ned lane — Gap 11)
- `prismatic/quality/gates.py` (Ned lane — Gap 11)
- `prismatic/review/registry.py` (Ned lane — Gap 11)
- `prismatic/review/hooks.py` (Ned lane — Gap 11)
- `pyproject.toml` (Fred lane — separate PR)
- `prismatic/dispatcher.py` (Fred lane — Gap 10)

If any forbidden file is in the diff, extract it into a separate PR before pushing.

## Push + PR

### 6. Branch + push
- [ ] `git checkout -b fred/gap12-observability-extension` (or similar)
- [ ] `git add` only the in-lane files
- [ ] `git commit -m "[Fred] Gap 12: extend TelemetryCollector with review observability (#XXXX)"`
- [ ] `git push -u origin fred/gap12-observability-extension`
- [ ] PR created with `gh pr create --base deploy-fresh`

### 7. PR description template

```markdown
## Goal
Close the review-pipeline telemetry black hole by extending `prismatic/telemetry.py`
with 4 new `record_*` methods + 4 new SQLite tables. Adds `prismatic.observability.ops_feed`
for Linear comments via `LinearTaskProvider` (Pattern B, not curl subprocess).

## What's in this PR
- 4 new record_* methods on TelemetryCollector (record_review_completed, record_plugin_registered, record_hook_fired, record_pipeline_action)
- 4 new tables in _ensure_tables() with telemetry_ prefix
- 4 new INSERT branches in _drain() (parameterized queries)
- 4 new entries in cleanup_expired() retention map
- get_dashboard_data() extended with review/hooks/plugins blocks
- New module prismatic.observability.ops_feed (post_review_event_to_linear)
- 23 new tests (17 telemetry extension + 6 ops_feed)

## Out of scope (deferred)
- prismatic/review/pr_reviewer_impl.py — Ned lane, gets telemetry param in Gap 11
- prismatic/review/pipeline.py — Ned lane, gets telemetry param in Gap 11
- prismatic/quality/gates.py — Ned lane, gets telemetry param in Gap 11
- pyproject.toml — Fred lane, separate PR if needed
- prismatic/dispatcher.py — Gap 10 calls discover_and_register_plugins from there

## Test count
- Baseline (deploy-fresh HEAD): 250
- New tests: 23
- Total after merge: 273

## Spec
okf/operations/gap12-observability-slice-spec.md

## Risk register
okf/operations/phase3-sprint1-plan/06-risk-register.md (R1, R4, R5, R8)
```

## Peer review (Sonnet)

After PR is open, trigger Sonnet peer review:
- [ ] Fire `agy --model claude-sonnet-4-6 --dangerously-skip-permissions` with PR URL + review prompt
- [ ] Sonnet verdict: APPROVE / REQUEST_CHANGES
- [ ] If REQUEST_CHANGES: address findings, push fix commits, re-review
- [ ] If APPROVE: merge PR with `gh pr merge <num> --squash --delete-branch`

## Post-merge

- [ ] Update OKF: write `okf/operations/gap12-implementation-lessons.md`
- [ ] Update distribution checklist (add `PRISMATIC_OPS_FEED_ISSUE_ID` env var)
- [ ] Update memory (add Gap 12 shipped entry)
- [ ] Verify on deploy-fresh: `python3 -m pytest prismatic/` shows 273/273
- [ ] Notify Michael: "Gap 12 merged, ready for Gap 11"
- [ ] Update todo list: mark `phase3-gap12-fire` completed, set `phase3-gap11-fire` in_progress

---

*Filed 2026-06-28 by Fred (orchestrator).*
