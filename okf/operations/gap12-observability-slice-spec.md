# Gap 12 — Observability Slice (Counters + Linear Ops Feed)

**Date:** 2026-06-28
**Sprint:** 1 of 3 (Phase 3)
**Lane:** Fred (infrastructure)
**Estimated effort:** 1 day
**Status:** SPEC — pending Michael's sign-off

---

## Goal

Turn "the factory works" from a claim into a measurement. After this gap, every review tick emits structured counters (reviews completed, plugins registered, findings by severity, hook fires, dispatch latency) that surface in:
1. **In-process structured logs** (visible to anyone tailing the dispatcher)
2. **Linear ops feed** (existing `agent:ops-feed` channel — currently used for general ops; this gap gives it specific events)
3. **Programmatic API** (counter snapshot for tests + dashboards)

This is the **thin slice** referenced in the Phase 3 plan — minimum viable observability to validate Gap 10 + Gap 11 ship correctly. Full tracing + Grafana-style dashboards is Gap 12-full (Sprint 2).

## Non-Goals

- **Prometheus / OpenTelemetry export** — not in scope; can be added as a consumer of the programmatic API later
- **Grafana / dashboard UI** — not in scope; Linear ops feed is the visible surface for now
- **Per-tenant metrics** — global counters only; multi-tenancy is a Phase 4 topic
- **Persistent metric storage** — counters are in-memory + Linear comments; no disk DB

## Public API Contracts

### Counter Infrastructure

New module `prismatic/review/metrics.py`:

```python
from dataclasses import dataclass, field

@dataclass
class ReviewMetrics:
    """In-memory counters for the review pipeline.

    Thread-safe via a single threading.Lock; counter increments are O(1)
    but not high-throughput (target: <10K increments/sec, lock uncontended
    in normal operation).
    """
    reviews_completed_total: int = 0
    reviews_with_critical_total: int = 0
    reviews_with_request_changes_total: int = 0
    plugins_discovered_total: int = 0
    plugin_register_failures_total: int = 0
    impact_rules_fired_total: int = 0
    hooks_fired_total: int = 0
    hook_failures_total: int = 0
    findings_by_severity: dict[str, int] = field(default_factory=dict)
    review_latency_ms_total: int = 0
    review_latency_ms_max: int = 0
    review_latency_ms_count: int = 0

    def snapshot(self) -> dict[str, Any]:
        """Return a JSON-serializable snapshot for logging + tests."""
```

### Metric Emitter Hooks

`RealPRReviewer.review_pr()` and `PipelineOrchestrator.process()` accept an optional `metrics: ReviewMetrics | None = None` param. When provided, they call increment methods on it.

### Linear Ops Feed Integration

New module `prismatic/observability/ops_feed.py`:

```python
def emit_metric_event(
    event_type: str,
    payload: dict[str, Any],
    *,
    ops_feed_token: str | None = None,
) -> None:
    """Post a metric event to Linear ops feed (best-effort).

    No-ops if ops_feed_token is None (test mode).
    Failures are logged but never raise -- observability must not crash
    the dispatcher.
    """
```

Event types emitted:

| Event | When | Payload |
|---|---|---|
| `prismatic.review.completed` | Every review_pr() returns | verdict, latency_ms, findings_count, critical_count |
| `prismatic.review.plugin_registered` | Plugin registered successfully | plugin_name, registry_secret_count, registry_check_count |
| `prismatic.review.plugin_register_failed` | Plugin raised during register | plugin_name, error_class, error_message |
| `prismatic.hook.fired` | Hook fired | hook_name, handler_count, returned_non_none |
| `prismatic.hook.failed` | Hook handler raised | hook_name, error_class, error_message |
| `prismatic.pipeline.action` | Pipeline decided an action | identifier, action, impact, attempts |

All events go to Linear as comments on the `GRO-OPS` issue (the existing ops-feed target). If `GRO-OPS` doesn't exist, fall back to structured stdout logging only.

## Files Changed

| File | Change |
|---|---|
| `prismatic/review/metrics.py` (NEW) | `ReviewMetrics` dataclass + `snapshot()` |
| `prismatic/review/pr_reviewer_impl.py` | `RealPRReviewer.review_pr()` accepts optional `metrics` param |
| `prismatic/review/pipeline.py` | `PipelineOrchestrator.process()` accepts optional `metrics` param |
| `prismatic/review/dispatcher_integration.py` (NEW) | `metrics` param threaded through `trigger_ned_review()` → reviewer → pipeline |
| `prismatic/observability/__init__.py` (NEW) | Empty package marker |
| `prismatic/observability/ops_feed.py` (NEW) | `emit_metric_event()` function |
| `prismatic/observability/test_ops_feed.py` (NEW) | 8 test rubrics |
| `prismatic/review/test_metrics.py` (NEW) | 10 test rubrics |
| `prismatic/quality/gates.py` | `trigger_ned_review()` accepts optional `metrics` + `ops_feed_token` params |

## Test Rubrics

In `TestReviewMetrics` (10 tests):

1. `test_default_metrics_zero` — fresh instance, all counters 0
2. `test_snapshot_returns_json_serializable_dict` — no datetimes, no sets
3. `test_review_completed_increments_counter` — calling increment_review_completed bumps it
4. `test_findings_by_severity_increments_correct_key` — `increment_finding("critical")` bumps `findings_by_severity["critical"]`
5. `test_latency_tracking_computes_count_avg_max` — record 3 latencies, verify aggregates
6. `test_metrics_are_thread_safe` — 100 threads × 1000 increments = 100K final count
7. `test_snapshot_does_not_mutate_counters` — calling snapshot() doesn't reset
8. `test_snapshot_includes_all_counters` — every field present
9. `test_zero_division_safety_on_empty_latencies` — no latencies recorded, snapshot still returns
10. `test_metrics_optional_param_no_op_when_none` — reviewer called without metrics, no crash

In `TestOpsFeedEmit` (8 tests):

11. `test_emit_metric_event_with_token_posts_to_linear` — mock Linear client, verify call
12. `test_emit_metric_event_without_token_is_noop` — no token, no crash
13. `test_emit_metric_event_swallows_network_failures` — Linear client raises, event still logged to stdout
14. `test_event_payload_serialized_as_json` — nested dict, datetime → ISO string
15. `test_emit_metric_event_logs_at_info_level` — verify log call
16. `test_event_type_validation` — known event types accepted; unknown types logged + skipped
17. `test_concurrent_emit_does_not_corrupt_feed` — 50 threads emit, all events posted exactly once
18. `test_ops_feed_falls_back_to_stdout_when_gro_ops_missing` — no Linear API, event goes to stderr

**Total: 18 new tests.**

## Acceptance Criteria

- [ ] `ReviewMetrics` dataclass importable from `prismatic.review`
- [ ] `emit_metric_event()` importable from `prismatic.observability`
- [ ] Counters thread-safe (verified by stress test)
- [ ] Linear ops feed receives events (mocked; live verified manually after merge)
- [ ] All 6 event types fire at documented trigger points
- [ ] Observability failures never crash the dispatcher
- [ ] 18 new tests pass; 279/279 total (was 261 after Gap 10, +18 here; Gap 11 brings to 293)
- [ ] Peer review APPROVE

## Acceptance: "This Gap Shipped Correctly" Evidence

The meta-review of Gap 10 + 11 will look for **observable proof** that plugin auto-discovery and hook dispatch are actually happening in production. This gap provides that proof. Specifically:
- `prismatic.review.plugins_discovered_total > 0` after first dispatcher boot with a real plugin installed
- `prismatic.hook.fired` events appear in Linear ops feed when hooks are invoked
- `prismatic.review.completed` events show `verdict` distribution over time

If the meta-review cannot find this evidence in the Linear feed, Gap 12 didn't ship correctly.

## Carry-Forward (Gap 12-full, Sprint 2)

- **OpenTelemetry export** — `prismatic.observability.otel_exporter`
- **Persistent metric storage** — SQLite-backed time-series
- **Per-tenant counters** — multi-tenancy metric routing
- **Trace context propagation** — `with review_trace(identifier):` context manager

## Lane Notes

- **Fred lane only.** Pure infrastructure; no Ned code changes.
- Single PR expected: PR #48 (Fred).

## Pattern Reference

- `okf/operations/phase2-meta-review-2026-06-28.md` — operational realism check (Gap 11 of meta-review criteria)
- `okf/operations/gap9-implementation-lessons.md` — Lesson 1 ("code complete != operationally complete")

---

*Spec written by Fred (orchestrator) — pending Michael's sign-off before AGY delegation.*
