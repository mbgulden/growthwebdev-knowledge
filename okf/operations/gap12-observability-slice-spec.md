# Gap 12 — Review Observability (Extends `TelemetryCollector`)

**Date:** 2026-06-28 (revised after recon)
**Sprint:** 1 of 3 (Phase 3)
**Lane:** Fred (infrastructure)
**Estimated effort:** 1 day
**Status:** SPEC REVISION — pending Michael's sign-off before AGY delegation

---

## What changed from the original spec

**Original (REJECTED):** Proposed new `prismatic/review/metrics.py` with in-memory `ReviewMetrics` dataclass + Linear ops feed via curl subprocess + `prismatic/observability/ops_feed.py`.

**Problem caught by subagent review:** `prismatic/telemetry.py` (905 lines, queue+daemon-thread, SQLite-backed) **already exists** and is the canonical telemetry layer. The original spec reinvented it badly (in-memory, single-Lock, no persistence). The `GRO-OPS` Linear issue was also invented (zero references in okf tree).

**Recon findings (3 parallel tasks, full audit in `phase3-reconnaissance-2026-06-28.md`):**
- `TelemetryCollector` has 12 public methods (I missed 5 of them)
- 7 SQLite tables in `event_router.db` with existing retention/circuit-breaker/alert infrastructure
- Two parallel Linear posting patterns; the canonical one is `prismatic/providers/tasks/linear.py::LinearTaskProvider.add_comment()`
- Zero of 6 review-pipeline event types are currently covered by telemetry

## Revised approach

**Extend `TelemetryCollector` with 4 new methods + 4 new tables.** Pure additive change to one file. No new modules.

---

## Goal

Close the review-pipeline telemetry black hole. After this gap, every review tick emits structured events (review completed, plugin registered, hook fired, pipeline action) that surface in:
1. **SQLite event tables** (durable, queryable via `get_dashboard_data()` extension)
2. **Linear comments** (via canonical `LinearTaskProvider.add_comment()` — Pattern B, not the broken curl-subprocess pattern)
3. **Optional dashboard aggregation** (extend `get_dashboard_data()` with review stats)

This is the **thin slice** referenced in the Phase 3 plan — minimum viable observability to validate Gap 10 + Gap 11 ship correctly. Full tracing + Grafana is Gap 12-full (Sprint 2).

## Non-Goals

- **OpenTelemetry export** — `prismatic/tracer.py` was collapsed into the single `telemetry.py` file (per `phase3-reconnaissance-2026-06-28.md` "Surprises"); rebuilding tracing is Gap 12-full
- **Prometheus / Grafana** — not in scope; existing `get_dashboard_data()` is the query API
- **Per-tenant metrics** — global counters only
- **Replacing existing alert systems** — `gateway/alert_manager.py::AlertEvaluator` and `telemetry.check_alerts` coexist; we extend telemetry, don't replace either

## Public API Contracts

### 4 new methods on `TelemetryCollector` (additive, no signature changes to existing methods)

```python
def record_review_completed(
    self,
    run_id: str,
    issue_id: str,
    reviewer: str,
    verdict: str,
    impact: str,
    rework_attempt: int = 0,
    duration_sec: float = 0.0,
) -> None:
    """Push a review.completed event to telemetry_review_completed table."""

def record_plugin_registered(
    self,
    plugin_name: str,
    plugin_version: str = "",
    source: str = "",
    success: bool = True,
    error: str | None = None,
) -> None:
    """Push a plugin.registered/register_failed event."""

def record_hook_fired(
    self,
    hook_name: str,
    event_type: str,
    run_id: str | None = None,
    issue_id: str | None = None,
    success: bool = True,
    error: str | None = None,
    duration_ms: float = 0.0,
) -> None:
    """Push a hook.fired/hook.failed event."""

def record_pipeline_action(
    self,
    action: str,
    run_id: str,
    issue_id: str,
    actor: str = "review-orchestrator",
    details: str | None = None,
) -> None:
    """Push a pipeline.action event (ACTION_ADVANCE/HOLD/REWORK/GIVE_UP)."""
```

### 4 new SQLite tables (created idempotently in `_ensure_tables()`)

```sql
CREATE TABLE IF NOT EXISTS telemetry_review_completed (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id          TEXT NOT NULL,
    issue_id        TEXT NOT NULL,
    reviewer        TEXT NOT NULL,
    verdict         TEXT NOT NULL,
    impact          TEXT NOT NULL,
    rework_attempt  INTEGER DEFAULT 0,
    duration_sec    REAL DEFAULT 0.0,
    created_at      TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_review_completed_issue
    ON telemetry_review_completed(issue_id, created_at);
CREATE INDEX IF NOT EXISTS idx_review_completed_verdict
    ON telemetry_review_completed(verdict, created_at);

CREATE TABLE IF NOT EXISTS telemetry_plugin_registered (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    plugin_name     TEXT NOT NULL,
    plugin_version  TEXT,
    source          TEXT,
    success         INTEGER DEFAULT 0,
    error           TEXT,
    created_at      TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_plugin_name
    ON telemetry_plugin_registered(plugin_name, created_at);

CREATE TABLE IF NOT EXISTS telemetry_hook_fired (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    hook_name       TEXT NOT NULL,
    event_type      TEXT NOT NULL,
    run_id          TEXT,
    issue_id        TEXT,
    success         INTEGER DEFAULT 0,
    error           TEXT,
    duration_ms     REAL DEFAULT 0.0,
    created_at      TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_hook_name
    ON telemetry_hook_fired(hook_name, created_at);
CREATE INDEX IF NOT EXISTS idx_hook_issue
    ON telemetry_hook_fired(issue_id, created_at);

CREATE TABLE IF NOT EXISTS telemetry_pipeline_action (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    action          TEXT NOT NULL,
    run_id          TEXT NOT NULL,
    issue_id        TEXT NOT NULL,
    actor           TEXT,
    details         TEXT,
    created_at      TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_pipeline_action_issue
    ON telemetry_pipeline_action(issue_id, created_at);
```

### 4 new INSERT branches in `_drain()` (after existing branches)

Each event_type → its table → INSERT with safe column extraction (`data.get(...)`).

### 4 new entries in `cleanup_expired()` retention table map

All 4 new tables use `RETENTION_LOOP_EVENTS=90` days (same default as existing review-related tables).

### Extended `get_dashboard_data()` returns

Add to the returned dict:
```python
"review": [
    {"verdict": "approve", "cnt": 42},
    {"verdict": "request_changes", "cnt": 7},
    {"verdict": "needs_discussion", "cnt": 3},
],
"hooks": {"succeeded": 156, "failed": 2},
"plugins": {"registered": 4, "register_failed": 1},
```

### Linear ops feed integration

**Use Pattern B (`LinearTaskProvider.add_comment`), NOT Pattern A (curl subprocess).**

New thin module `prismatic/observability/ops_feed.py`:
```python
def post_review_event_to_linear(
    issue_id: str,
    event_type: str,
    payload: dict[str, Any],
    *,
    linear_api_key: str | None = None,
) -> bool:
    """Post a review-pipeline event as a Linear comment.

    Falls back to stdout logging if linear_api_key is None or if the
    Linear API call fails. Never raises.

    Returns True if Linear accepted the comment, False otherwise.
    """
```

This function:
1. Validates `event_type` is one of: `review.completed`, `plugin.registered`, `plugin.register_failed`, `hook.fired`, `hook.failed`, `pipeline.action`
2. Builds a markdown body from `payload` (uses `json.dumps(indent=2)` for nested fields)
3. Calls `LinearTaskProvider(api_key=linear_api_key).add_comment(issue_id, body)`
4. On any exception: logs to stderr, returns False

**`GRO-OPS` issue ID:**
- `agent:ops-feed` label is referenced in the original spec but the Linear issue ID `GRO-OPS` was invented (zero references in okf tree)
- Reconnaissance did not find a concrete `GRO-OPS` issue
- **Resolution:** Gap 12 ships with `ops_feed_target_issue_id` as an env var `PRISMATIC_OPS_FEED_ISSUE_ID`. If unset, ops_feed falls back to stdout-only mode (no Linear posts). The existing factory cron has access to `LINEAR_API_KEY`; the `PRISMATIC_OPS_FEED_ISSUE_ID` env var is a new addition documented in the deployment guide.

## Files Changed

| File | Change |
|---|---|
| `prismatic/telemetry.py` | Add 4 `record_*` methods, 4 tables in `_ensure_tables`, 4 INSERT branches in `_drain`, 4 entries in `cleanup_expired`, extend `get_dashboard_data` |
| `prismatic/observability/__init__.py` (NEW) | Empty package marker |
| `prismatic/observability/ops_feed.py` (NEW) | `post_review_event_to_linear()` thin wrapper using `LinearTaskProvider` |
| `prismatic/review/pr_reviewer_impl.py` | `RealPRReviewer.__init__` accepts optional `telemetry: TelemetryCollector \| None = None`; `review_pr()` calls `telemetry.record_review_completed(...)` on success path |
| `prismatic/review/pipeline.py` | `PipelineOrchestrator.__init__` accepts optional `telemetry`; `process()` calls `telemetry.record_pipeline_action(...)` |
| `prismatic/quality/gates.py` | `trigger_ned_review()` accepts optional `telemetry`; calls `telemetry.record_hook_fired(HOOK_BEFORE_NED_REVIEW, ...)` (when Gap 11 lands hook dispatch) |
| `prismatic/observability/test_ops_feed.py` (NEW) | Test rubrics below |
| `prismatic/test_telemetry_extension.py` (NEW) | Test rubrics for the 4 new `record_*` methods + 4 new tables |
| `okf/operations/prismatic-distribution-checklist.md` | Update with `PRISMATIC_OPS_FEED_ISSUE_ID` env var doc |

## Test Rubrics

In `TestRecordReviewCompleted` (4 tests):

1. `test_record_review_completed_inserts_row` — push event, query `telemetry_review_completed` table, verify row
2. `test_record_review_completed_with_rework_attempt` — verify `rework_attempt` column populated
3. `test_record_review_completed_with_zero_duration` — verify `duration_sec=0.0` accepted
4. `test_record_review_completed_uses_telemetry_prefix` — verify table name starts with `telemetry_` (not the `agy_live_state` inconsistency)

In `TestRecordPluginRegistered` (3 tests):

5. `test_record_plugin_registered_success_path` — verify `success=1` row
6. `test_record_plugin_registered_failure_path_with_error` — verify `success=0`, `error` populated
7. `test_record_plugin_registered_with_version_metadata` — verify `plugin_version` populated

In `TestRecordHookFired` (3 tests):

8. `test_record_hook_fired_success_path` — verify `success=1`
9. `test_record_hook_fired_failure_path` — verify `success=0`, `error` populated, `duration_ms` preserved
10. `test_record_hook_fired_with_optional_run_id_issue_id` — verify NULL handling for missing fields

In `TestRecordPipelineAction` (2 tests):

11. `test_record_pipeline_action_inserts_row` — verify all 4 ACTION_* values accepted
12. `test_record_pipeline_action_with_details_json` — verify `details` TEXT column accepts complex payloads

In `TestDashboardExtension` (3 tests):

13. `test_get_dashboard_data_includes_review_block` — verify new `review` block present in return
14. `test_get_dashboard_data_includes_hooks_block` — verify `hooks` block with succeeded/failed counts
15. `test_get_dashboard_data_includes_plugins_block` — verify `plugins` block with registered/failed counts

In `TestOpsFeed` (6 tests):

16. `test_post_review_event_with_valid_event_type_attempts_linear` — mock `LinearTaskProvider.add_comment`, verify called
17. `test_post_review_event_with_invalid_event_type_returns_false` — invalid type, no Linear call
18. `test_post_review_event_with_no_api_key_returns_false_gracefully` — missing key, no crash
19. `test_post_review_event_swallows_linear_api_exception` — Linear raises, returns False
20. `test_post_review_event_falls_back_to_stderr_on_linear_failure` — verify stderr log on failure
21. `test_post_review_event_payload_serialized_as_markdown` — verify markdown body shape

In `TestEndToEnd` (2 tests):

22. `test_real_reviewer_completing_emits_review_completed_event` — real review through `RealPRReviewer.review_pr()`, verify telemetry row inserted (this is the test that would have caught Phase 2 Lesson 10 — dead channel)
23. `test_pipeline_action_advance_emits_pipeline_action_event` — real `PipelineOrchestrator.process()`, verify telemetry row inserted

**Total: 23 new tests.**

## Acceptance Criteria

- [ ] 4 new `record_*` methods exist on `TelemetryCollector`
- [ ] 4 new tables created in `_ensure_tables()` with `telemetry_` prefix
- [ ] 4 new INSERT branches in `_drain()`
- [ ] 4 new entries in `cleanup_expired()` retention map
- [ ] `get_dashboard_data()` extended with `review`, `hooks`, `plugins` blocks
- [ ] `post_review_event_to_linear()` exported from `prismatic.observability`
- [ ] Pattern B (`LinearTaskProvider`) used, NOT curl subprocess
- [ ] `RealPRReviewer(..., telemetry=...)` accepts telemetry param
- [ ] `PipelineOrchestrator(..., telemetry=...)` accepts telemetry param
- [ ] 23 new tests pass
- [ ] Total tests: 273+ (was 250; +23)
- [ ] Peer review by claude-sonnet-4-6 returns APPROVE

## Acceptance: "This Gap Shipped Correctly" Evidence

The meta-review of Gap 10 + 11 will look for **observable proof** that plugin auto-discovery and hook dispatch are actually happening. This gap provides that proof. Specifically:

- `sqlite3 event_router.db "SELECT COUNT(*) FROM telemetry_plugin_registered WHERE success=1"` returns > 0 after first dispatcher boot with a real plugin installed
- `sqlite3 event_router.db "SELECT * FROM telemetry_hook_fired ORDER BY id DESC LIMIT 5"` returns rows when hooks are invoked
- `get_dashboard_data()` returns non-empty `review` block after at least one review tick

If the meta-review cannot find this evidence, Gap 12 didn't ship correctly.

## Carry-Forward (not in this gap)

- **Tracing support** — `prismatic/tracer.py` was collapsed into single file; rebuild as Gap 12-full
- **Histograms / percentiles** — `get_dashboard_data` returns aggregates only; p50/p95/p99 deferred to Gap 12-full
- **Sampling for high-volume events** — at current factory cron rate (~0.003/sec per Phase 2 Lesson 1), no sampling needed; defer until scaling track
- **OpenTelemetry export** — Gap 12-full
- **`check_alerts` auto-invocation** — currently never called automatically; add a dispatcher cron job in Gap 12-full
- **Dead retention env vars** (`PRISMATIC_RETENTION_TOOL_CALLS`, `PRISMATIC_RETENTION_RESOURCE_SNAPSHOTS`) — cleanup candidate

## Lane Notes

- **Fred lane only** for new code (telemetry.py extension + ops_feed.py)
- **Ned lane** for the small integration changes in `pr_reviewer_impl.py`, `pipeline.py`, `gates.py` (each adds one optional `telemetry` param + one telemetry call on success path)
- Two PRs expected:
  - PR #X (Fred): `telemetry.py` extension + `ops_feed.py` + tests
  - PR #Y (Ned): integration in `pr_reviewer_impl.py` + `pipeline.py` + `gates.py`

## Pattern Reference

- `okf/operations/phase3-reconnaissance-2026-06-28.md` — full telemetry API map + extension pattern
- `okf/operations/phase2-meta-review-2026-06-28.md` — operational realism check
- `okf/operations/phase3-second-opinions-2026-06-28.md` — original spec rejection rationale

---

*Spec revised by Fred (orchestrator) after recon + subagent review. Pending Michael's sign-off.*
