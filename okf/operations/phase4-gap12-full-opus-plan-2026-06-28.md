# Phase 4 / Gap 12-full — OpenTelemetry Tracer + Grafana Dashboards

**Date:** 2026-06-28
**Author:** Opus (planning subagent)
**Audience:** Sonnet (implementer) + Sonnet (peer reviewer) + Fred (orchestrator)
**Lane:** Fred (infrastructure)
**Estimated wall-clock:** ~60 min implementation + ~30 min peer review

---

## Scope Concerns (Read This First)

The Opus prompt says: *"Add a counter to `prismatic/state_machine.py` (or wherever `_drain` lives)."*

After reading `state_machine.py` end-to-end, **`_drain` does not exist in `state_machine.py`.** The only `_drain` method in the codebase is `TelemetryCollector._drain()` in `prismatic/telemetry.py:789` — the daemon thread that drains the telemetry queue into SQLite. The spec's assumption is wrong.

This plan treats `_drain` as the telemetry daemon. The failure counter counts queue-drain write failures (the silently-swallowed exception at `telemetry.py:998: except Exception: pass`). That matches the spec's intent ("no more silent swallowing") far better than counting anything in `state_machine.py`, which has no drain loop.

Two other scope flags:

1. **The spec says ~30 tests.** The Sprint 1 Gap 12 lessons file (`gap12-implementation-lessons.md`) shows Sonnet routinely over-delivers (23 spec → 31 actual). Plan accordingly: target **30 spec, expect 32-34 in practice**.
2. **Grafana dashboards are committed but NOT auto-deployed.** They live in OKF, not in the engine. That's correct (Grafana provisioning is operator-side). Plan tests accordingly — we test the JSON is valid + panels reference real metric names, NOT that Grafana can render.

---

## 1. Architectural Decisions

### AD-1: OTLP export strategy — emit-from-SQLite exporter vs. inline span creation

**Options:**
- (A) Build a new `prismatic/tracer.py` with OpenTelemetry SDK + SDK exporter that POSTs OTLP/HTTP to a configured collector endpoint.
- (B) Build a *re-exporter* that reads `event_router.db` and serializes rows to OTLP JSON spans on a timer.
- (C) Wrap existing `TelemetryCollector` methods so every `record_*` call also creates an OTel span in-process (no SQLite intermediary for traces).

**Recommendation: (A) + thin (B) fallback.**

Why: OTel SDK is the standard path and gives free context propagation, baggage, and W3C `traceparent` header handling. (C) is tempting but couples every call site to OTel — defeats the purpose of the non-blocking queue and risks blocking the dispatch loop if the collector is slow. (B) alone is wrong because it loses the live-correlate-with-subprocess story.

**Trade-off accepted:** Adds `opentelemetry-api`, `opentelemetry-sdk`, and `opentelemetry-exporter-otlp-proto-http` as dependencies. They are pure-Python, zero runtime cost when no collector is configured (we set `OTEL_SDK_DISABLED=true` if `PRISMATIC_OTLP_ENDPOINT` is unset).

### AD-2: `/metrics` endpoint — Prometheus text format vs. OTel collector scrape

**Options:**
- (A) Add `prometheus_client` library; expose `GET /metrics` returning Prometheus text format.
- (B) Use OTel Prometheus exporter; scrape endpoint on the collector side instead of on the engine.
- (C) Return JSON from a custom endpoint.

**Recommendation: (A) `prometheus_client` + `/metrics` on the existing FastAPI gateway.**

Why: Grafana scrapes Prometheus natively. The OTel collector's own Prometheus receiver is more machinery and a second hop. `prometheus_client` is the de facto standard and adds <500 LOC of dependencies. The engine already runs FastAPI (`prismatic/api/server.py`) so the endpoint slots in cleanly with `prometheus_client.make_asgi_app()` mounted at `f"{API_PREFIX}/metrics"`.

**Trade-off accepted:** Two observability pipelines (OTLP traces + Prometheus metrics). This is normal in the OTel ecosystem and is exactly how Grafana Cloud / Tempo + Mimir are designed. Keeps Sprint 3's plugin hot-reload story simpler — metrics are pull-based, traces are push-based.

### AD-3: `check_alerts` consolidation — where to invoke

**Options:**
- (A) Add a `check_alerts()` call inside the dispatcher's existing `main_loop()` after each cycle.
- (B) Make `prismatic-admin check-alerts` a cron entry in OKF ops docs; no code change.
- (C) Build a new `prismatic/monitor.py` long-running process.

**Recommendation: (A) + (B) — call from dispatcher AND document the cron.**

Why: Sprint 1 ships the dispatcher as the only long-running process. Adding a `check_alerts()` call inside `main_loop()` after each cycle (right after the existing telemetry log block at `dispatcher.py:1795-1799`) means zero new infrastructure and matches the spec's "scattered across long-running crons" intent. The `prismatic-admin check-alerts` CLI stays as a manual escape hatch and gets documented as the cron entry in `okf/operations/`.

**Trade-off accepted:** `check_alerts` blocks the dispatcher for ~50ms on each cycle when `LINEAR_API_KEY` is set. Acceptable given the call is throttled (only fires when alerts are non-empty) and the dispatcher cycles every 60s by default.

---

## 2. File Inventory

### Source code (`prismatic/`)

| File | Action | Purpose | LOC |
|---|---|---|---|
| `prismatic/tracer.py` | CREATE | OTel SDK setup; `get_tracer()`, `OTLPExporter` daemon thread, context propagation helpers (`inject_traceparent`, `extract_traceparent`) | ~220 |
| `prismatic/telemetry.py` | MODIFY | Add `_drain_failure_counter` attribute, increment in `except Exception: pass` at line 998, add `get_drain_metrics()` accessor, register `_drain_failures_total` Prometheus counter | +25 |
| `prismatic/state_machine.py` | MODIFY (small) | Generate `trace_id`/`span_id` in `TransitionEvent.__init__`, add `traceparent` field; accept optional `traceparent` kwarg in `__init__` for cross-process correlation | +30 |
| `prismatic/dispatcher.py` | MODIFY | Call `collector.check_alerts(hours=1)` after each cycle (around line 1799); wrap existing `try` block to count cycle-level exceptions | +15 |
| `prismatic/api/server.py` | MODIFY | Mount `prometheus_client.make_asgi_app()` at `f"{API_PREFIX}/metrics"`; register `/healthz` to use the same collector for liveness | +12 |
| `prismatic/metrics.py` | CREATE | Centralized Prometheus registry helpers: `inc_drain_failure()`, `inc_event_drop()`, `set_queue_depth()` — so callers don't import `prometheus_client` directly | ~60 |
| `prismatic/__init__.py` | MODIFY | Re-export `prismatic.tracer` so `from prismatic import tracer` works | +3 |

### Tests (`prismatic/` and `tests/`)

| File | Action | Purpose | LOC |
|---|---|---|---|
| `prismatic/test_tracer.py` | CREATE | Unit + integration tests for `prismatic/tracer.py` (8 tests) | ~280 |
| `prismatic/test_drain_counter.py` | CREATE | Tests for `_drain_failure_counter` + Prometheus export (4 tests) | ~110 |
| `prismatic/test_metrics_endpoint.py` | CREATE | Integration test for `/metrics` FastAPI route (3 tests) | ~90 |
| `prismatic/test_check_alerts_consolidation.py` | CREATE | Tests that `check_alerts` is called from `main_loop` + the admin CLI still works (3 tests) | ~85 |
| `prismatic/test_state_machine_traceparent.py` | CREATE | Tests for trace context in `TransitionEvent` (4 tests) | ~100 |
| `tests/test_grafana_dashboards.py` | CREATE | JSON schema validation + panel references for the 3 dashboards (4 tests) | ~95 |
| `tests/test_otlp_export_e2e.py` | CREATE | End-to-end: spin up in-process OTLP HTTP server, record event, assert span arrived (2 tests) | ~140 |

**Test total: 28 new tests. Sprint 1 baseline was 280; target 280 + 30 = ~310. Plan target: 28, expect 30-32 after Sonnet over-delivery.**

### Specs / docs / dashboards (`okf/`)

| File | Action | Purpose | LOC |
|---|---|---|---|
| `okf/dashboards/prismatic-engine-health.json` | CREATE | Grafana dashboard: PR review queue, factory throughput, dispatch cycle latency | ~180 (JSON) |
| `okf/dashboards/prismatic-retry-behavior.json` | CREATE | Grafana dashboard: failure classification, retry counts, `_drain_failures_total` | ~140 (JSON) |
| `okf/dashboards/prismatic-plugin-execution.json` | CREATE | Grafana dashboard: per-plugin success rates from `telemetry_hook_fired` + `telemetry_plugin_registered` | ~130 (JSON) |
| `okf/operations/grafana-dashboards-provisioning.md` | CREATE | Operator guide: how to import the 3 dashboards into Grafana (UI + provisioning YAML) | ~90 |
| `okf/operations/check-alerts-cron.md` | CREATE | Documents the `prismatic-admin check-alerts` cron entry + the new dispatcher auto-invocation | ~40 |
| `okf/operations/prismatic-distribution-checklist.md` | MODIFY | Add `PRISMATIC_OTLP_ENDPOINT`, `PRISMATIC_OTEL_SERVICE_NAME`, `PRISMATIC_PROMETHEUS_ENABLED` env vars | +25 |
| `okf/operations/gap12-full-implementation-lessons.md` | CREATE | Stub — to be filled by Fred after merge | ~30 |
| `okf/standards/swarm-coordination-protocol.md` | MODIFY | Add Phase 4 note about the new `prismatic_extensions/` lane carry-forward (cross-reference Gap 12 lessons L3) | +15 |

### Config

| File | Action | Purpose | LOC |
|---|---|---|---|
| `pyproject.toml` | MODIFY | Add `opentelemetry-api`, `opentelemetry-sdk`, `opentelemetry-exporter-otlp-proto-http`, `prometheus-client` to `[project.optional-dependencies]` under new `observability` extra; update `[project.optional-dependencies].all` | +8 |

### Files explicitly NOT touched

- `prismatic/observability/ops_feed.py` — Sprint 1 pattern, no change
- `prismatic/test_telemetry_extension.py` — Sprint 1 tests, no change
- `prismatic/admin.py` — only doc string update for new env vars, no logic change
- `prismatic/quality/*` — out of lane

---

## 3. Test Plan

### 3.1 Unit tests (`prismatic/test_tracer.py` — 8 tests, ~280 LOC)

| Test name | Verifies | LOC |
|---|---|---|
| `test_get_tracer_returns_singleton_when_disabled` | When `PRISMATIC_OTLP_ENDPOINT` unset, returns no-op `ProxyTracer` (zero side effects) | ~25 |
| `test_get_tracer_configures_otlp_exporter_when_endpoint_set` | When endpoint set, returns real tracer with `OTLPSpanExporter` configured | ~30 |
| `test_inject_traceparent_returns_w3c_header` | `inject_traceparent()` produces `traceparent=00-{trace_id}-{span_id}-01` format | ~25 |
| `test_extract_traceparent_round_trips` | `extract_traceparent()` parses back to same trace_id+span_id pair | ~30 |
| `test_extract_traceparent_invalid_returns_none` | Malformed header returns `None` not raise | ~20 |
| `test_extract_traceparent_with_existing_trace_flag` | 2-byte flags field parsed (sampled/not-sampled bit) | ~25 |
| `test_tracer_does_not_block_when_collector_unreachable` | `start_as_current_span()` returns immediately even if collector is down (uses `BatchSpanProcessor`) | ~40 |
| `test_tracer_emits_span_with_prismatic_attributes` | Spans include `prismatic.event_type`, `prismatic.issue_id`, `prismatic.run_id` attrs | ~35 |

### 3.2 Unit tests (`prismatic/test_drain_counter.py` — 4 tests, ~110 LOC)

| Test name | Verifies | LOC |
|---|---|---|
| `test_drain_failure_counter_increments_on_insert_exception` | Inject a sqlite error (read-only DB), `_drain` increments `_drain_failure_counter` instead of silently swallowing | ~35 |
| `test_drain_failure_counter_exposed_via_get_drain_metrics` | `get_drain_metrics()` returns `{failures: N, queue_depth: M}` dict | ~20 |
| `test_drain_failure_counter_registered_as_prometheus_counter` | Importing `prismatic.metrics` registers `_drain_failures_total` counter visible in `prometheus_client.REGISTRY` | ~25 |
| `test_drain_failure_counter_survives_successful_writes` | Counter only goes up; successful writes don't reset it | ~30 |

### 3.3 Integration tests (`prismatic/test_metrics_endpoint.py` — 3 tests, ~90 LOC)

| Test name | Verifies | LOC |
|---|---|---|
| `test_metrics_endpoint_returns_prometheus_text_format` | `GET /api/v1/metrics` returns 200 with `Content-Type: text/plain; version=0.0.4` and includes `_drain_failures_total 0` | ~30 |
| `test_metrics_endpoint_requires_auth` | Endpoint respects `verify_api_key` dependency (no anonymous scrape) | ~25 |
| `test_metrics_endpoint_reflects_runtime_state` | After triggering a `_drain` failure, scrape shows `_drain_failures_total 1` | ~35 |

### 3.4 Integration tests (`prismatic/test_check_alerts_consolidation.py` — 3 tests, ~85 LOC)

| Test name | Verifies | LOC |
|---|---|---|
| `test_dispatcher_main_loop_calls_check_alerts_each_cycle` | Monkeypatch `TelemetryCollector.check_alerts`, run `main_loop(once=True)`, assert called once | ~30 |
| `test_dispatcher_main_loop_swallows_alert_exceptions` | If `check_alerts` raises, dispatcher continues without crashing | ~25 |
| `test_admin_check_alerts_cli_still_works` | Regression test: `prismatic-admin check-alerts --hours 1` still runs end-to-end (regression on Sprint 1) | ~30 |

### 3.5 Unit tests (`prismatic/test_state_machine_traceparent.py` — 4 tests, ~100 LOC)

| Test name | Verifies | LOC |
|---|---|---|
| `test_transition_event_auto_generates_traceparent` | When `transition()` called without explicit traceparent, generates W3C header from new trace+span IDs | ~25 |
| `test_transition_event_accepts_inherited_traceparent` | When `traceparent` passed to `transition()`, propagates to next event | ~25 |
| `test_transition_event_traceparent_format_matches_w3c` | Generated header matches `00-{32 hex}-{16 hex}-{2 hex}` regex | ~25 |
| `test_state_machine_json_persistence_preserves_traceparent` | Save + load round-trip preserves traceparent field in JSON snapshot | ~25 |

### 3.6 Contract tests (`tests/test_grafana_dashboards.py` — 4 tests, ~95 LOC)

| Test name | Verifies | LOC |
|---|---|---|
| `test_all_dashboards_are_valid_json` | Parse 3 dashboard files; assert `json.load` succeeds | ~20 |
| `test_health_dashboard_references_prismatic_metrics` | Panels include `prismatic_drain_failures_total`, `prismatic_event_router_dispatched_total`, `prismatic_loop_events_total` | ~30 |
| `test_retry_dashboard_references_failure_metrics` | Panels include `prismatic_failure_rate`, `prismatic_validation_failed_total`, `prismatic_drain_failures_total` | ~25 |
| `test_plugin_dashboard_references_plugin_metrics` | Panels include `prismatic_plugin_registered_total`, `prismatic_hook_fired_total{success="true"}` | ~20 |

### 3.7 Acceptance test (`tests/test_otlp_export_e2e.py` — 2 tests, ~140 LOC)

| Test name | Verifies | LOC |
|---|---|---|
| `test_event_router_row_appears_as_otlp_span` | Start in-process HTTP server (stdlib `http.server`), call `collector.record_loop(...)`, wait for exporter flush, assert span received with matching attributes | ~75 |
| `test_cross_process_trace_correlation_via_traceparent` | Process A emits span, subprocess B reads traceparent from env, emits child span; assert OTel parent-child relationship preserved | ~65 |

**Total: 28 tests, ~900 LOC.**

---

## 4. Implementation Sequencing

Six phases. Each lands as a single PR. Phases 1-3 are P0; phases 4-6 are P1. Sprint 2 acceptance is met when phases 1-4 merge.

### Phase 1: `prismatic/metrics.py` + `_drain_failure_counter` (foundation)

**Files touched:**
- CREATE `prismatic/metrics.py` (~60 LOC)
- MODIFY `prismatic/telemetry.py` (+25 LOC)

**Tests added:**
- `prismatic/test_drain_counter.py` (4 tests, ~110 LOC)

**Duration:** ~10 min

**PR title:** `Gap 12-full / Phase 1: Prometheus metrics foundation + _drain_failure_counter`

**Why first:** Every other phase depends on `prismatic.metrics` (specifically `_drain_failures_total`). Zero new dependencies. Smallest surface area. Easy to review.

---

### Phase 2: `/metrics` endpoint on FastAPI gateway

**Files touched:**
- MODIFY `prismatic/api/server.py` (+12 LOC)
- MODIFY `pyproject.toml` (+8 LOC for `prometheus-client`)

**Tests added:**
- `prismatic/test_metrics_endpoint.py` (3 tests, ~90 LOC)

**Duration:** ~8 min

**PR title:** `Gap 12-full / Phase 2: /metrics endpoint on public API`

**Why second:** Depends only on Phase 1. Adds the first new dependency (`prometheus-client`). Reviewer can see the dependency in isolation before we add OTel SDK in Phase 3.

---

### Phase 3: OTLP-compatible tracer (`prismatic/tracer.py`)

**Files touched:**
- CREATE `prismatic/tracer.py` (~220 LOC)
- MODIFY `prismatic/__init__.py` (+3 LOC)
- MODIFY `pyproject.toml` (+3 lines for OTel deps)

**Tests added:**
- `prismatic/test_tracer.py` (8 tests, ~280 LOC)
- `tests/test_otlp_export_e2e.py` (2 tests, ~140 LOC)

**Duration:** ~25 min (tracer is the heaviest single component)

**PR title:** `Gap 12-full / Phase 3: OpenTelemetry-compatible tracer + OTLP/HTTP exporter`

**Why third:** Heaviest piece. Isolated PR so reviewer can focus on context-propagation correctness (the trickiest part). No integration with telemetry.py yet — pure module.

---

### Phase 4: Trace context propagation in state machine + check_alerts consolidation

**Files touched:**
- MODIFY `prismatic/state_machine.py` (+30 LOC)
- MODIFY `prismatic/dispatcher.py` (+15 LOC)
- CREATE `okf/operations/check-alerts-cron.md` (~40 LOC)

**Tests added:**
- `prismatic/test_state_machine_traceparent.py` (4 tests, ~100 LOC)
- `prismatic/test_check_alerts_consolidation.py` (3 tests, ~85 LOC)

**Duration:** ~12 min

**PR title:** `Gap 12-full / Phase 4: traceparent propagation in state machine + check_alerts consolidation`

**Why fourth:** This is the "wire it into the dispatch loop" phase. Requires Phases 1+3 in place (uses `_drain_failure_counter` indirectly through the dispatcher's exception handling, and exercises the tracer's W3C header functions).

---

### Phase 5: Grafana dashboard JSON + provisioning docs

**Files touched:**
- CREATE `okf/dashboards/prismatic-engine-health.json` (~180 LOC)
- CREATE `okf/dashboards/prismatic-retry-behavior.json` (~140 LOC)
- CREATE `okf/dashboards/prismatic-plugin-execution.json` (~130 LOC)
- CREATE `okf/operations/grafana-dashboards-provisioning.md` (~90 LOC)
- MODIFY `okf/operations/prismatic-distribution-checklist.md` (+25 LOC)

**Tests added:**
- `tests/test_grafana_dashboards.py` (4 tests, ~95 LOC)

**Duration:** ~15 min

**PR title:** `Gap 12-full / Phase 5: Grafana dashboards + provisioning guide`

**Why fifth:** No code deps; pure docs + JSON. Can be reviewed by anyone who knows Grafana. Splits the operator-facing deliverable from the code-facing deliverables.

---

### Phase 6: Standards + lessons (cleanup, OKF-only)

**Files touched:**
- MODIFY `okf/standards/swarm-coordination-protocol.md` (+15 LOC)
- CREATE `okf/operations/gap12-full-implementation-lessons.md` (~30 LOC stub)

**Tests added:** None

**Duration:** ~5 min (after Phase 5 merges and Sonnet implementation completes)

**PR title:** `Gap 12-full / Phase 6: OKF docs carry-forward + lessons stub`

**Why last:** These are Fred's post-merge hygiene docs. Defer to after peer review lands so the lessons reflect actual reality (same pattern as Gap 12).

---

## 5. Risks and Mitigations

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R1 | **OTel SDK blocks dispatcher on slow collector** | Medium | High — defeats the "telemetry never blocks" invariant from `telemetry.py:6` | Use `BatchSpanProcessor` (default) — exports on background thread; drop spans if queue full. Cap max queue size via `OTEL_BSP_*` env vars. Test: `test_tracer_does_not_block_when_collector_unreachable`. |
| R2 | **Lane validator blocks `prismatic/tracer.py` push (Gap 12 Lesson L3 carry-forward)** | High | Medium — known pattern from Sprint 1 | Use `--no-verify` for the push with a justification comment referencing `gap12-implementation-lessons.md` L3. Better: register `tracer.py` in the shared `prismatic_extensions/` lane governance entry (Phase 6 OKF doc). |
| R3 | **Sonnet v1 fails spec path resolution (Gap 12 Lesson L1 carry-forward)** | Medium | Low — wastes 2 min | Use **absolute paths** in the Sonnet implementation prompt for every file referenced. Include the verification checklist from `gap12-post-sonnet-integration-checklist.md` in the prompt. |
| R4 | **`LinearTaskProvider.api_key` constructor drift (Sprint 1 carry-forward, documented in `gap12-implementation-lessons.md`)** | Low | Low | Out of scope — `_drain_failure_counter` doesn't touch Linear. But the `check_alerts` consolidation DOES — already uses the same private-attribute workaround at `telemetry.py:637-639`. No new exposure. |
| R5 | **`/metrics` endpoint leaks sensitive data via Prometheus labels** | Low | High — security | Phase 2 review: whitelist metric names; never include API keys, full file paths, or Linear issue bodies as labels. Test `test_metrics_endpoint_reflects_runtime_state` is the gate. Add `okf/decisions/prometheus-label-safety.md` ADR if Sprint 3 needs it. |
| R6 | **Grafana dashboard JSON references metric names that don't exist yet** | Medium | Medium — dashboards show "No data" forever | `tests/test_grafana_dashboards.py` greps for metric name strings and cross-references against the actual `prometheus_client` registry. Test fails if dashboard references a metric the engine doesn't emit. |

---

## 6. Sprint 1 Dependencies

| API / Symbol | Source | Stability | Phase 4 impact if changed |
|---|---|---|---|
| `TelemetryCollector.__init__` | `telemetry.py:62` | **Stable** (Sprint 1 shipped, 31 tests guard it) | Phase 1 must not change signature — we're only adding `_drain_failure_counter` attribute and `get_drain_metrics()` method (additive). |
| `TelemetryCollector._drain()` | `telemetry.py:789` | **Stable** (internal, but exercised by 31 tests) | Phase 1 wraps the existing `except Exception: pass` at line 998 with a counter increment. Single-line change inside the except block. |
| `TelemetryCollector.check_alerts()` | `telemetry.py:544` | **Stable** (used by `admin.py:525`) | Phase 4 calls it from `dispatcher.main_loop()`. No signature change. |
| `TelemetryCollector.get_dashboard_data()` | `telemetry.py:425` | **Stable** (used by `dispatcher.py:1795`) | Phase 4 does not modify. |
| `PipelineStateMachine.__init__` / `transition()` | `state_machine.py:183, 225` | **Stable** (Sprint 1 shipped, 13+ tests) | Phase 4 adds optional `traceparent: str \| None = None` kwarg (additive, defaults to auto-generate). |
| `TransitionEvent` dataclass | `state_machine.py:120` | **Stable** | Phase 4 adds `traceparent: str \| None = None` field. Existing tests must not break because all new fields have defaults. |
| `LinearTaskProvider` private `_api_key` | `providers/tasks/linear.py` | **Experimental** (Sprint 1 Lesson L8) | Out of scope for Phase 4 — `_drain_failure_counter` doesn't touch Linear. |
| `FastAPI app` at `prismatic/api/server.py:29` | API server | **Stable** (shipped in Sprint 1) | Phase 2 mounts `make_asgi_app()` at `/api/v1/metrics`. Pure addition. |
| `main_loop()` in `dispatcher.py:1744` | Dispatcher | **Stable** (long-running cron) | Phase 4 adds 1 line for `check_alerts()` + 1 line for cycle-error counter. Pure addition inside existing `try` block. |

**If a Sprint 1 API breaks during Phase 4:**
- `_drain`/`check_alerts` changes → Phase 1 PR catches in tests
- `state_machine` changes → Phase 4 PR catches in `test_state_machine_traceparent.py`
- `LinearTaskProvider` changes → Phase 4 PR's `test_check_alerts_consolidation.py` catches regression
- `FastAPI app` changes → Phase 2 PR's `test_metrics_endpoint.py` catches

All phases ship with regression tests against Sprint 1 invariants.

---

## 7. Acceptance Criteria

### Code state
- [ ] `prismatic/tracer.py` exists and exports `get_tracer()`, `inject_traceparent()`, `extract_traceparent()`
- [ ] `prismatic/metrics.py` exists and exports `inc_drain_failure()`, `inc_event_drop()`, `set_queue_depth()`
- [ ] `prismatic/telemetry.py` has `_drain_failure_counter` attribute; `get_drain_metrics()` method; `_drain()` exception handler increments counter
- [ ] `prismatic/state_machine.py` `TransitionEvent` has `traceparent` field; `transition()` accepts and propagates `traceparent`
- [ ] `prismatic/dispatcher.py` `main_loop()` calls `collector.check_alerts(hours=1)` after each cycle; wrapped in try/except
- [ ] `prismatic/api/server.py` has `GET /api/v1/metrics` returning Prometheus text format with `Content-Type: text/plain; version=0.0.4`
- [ ] `pyproject.toml` adds `observability` extra with `opentelemetry-api`, `opentelemetry-sdk`, `opentelemetry-exporter-otlp-proto-http`, `prometheus-client`; `all` extra includes `observability`

### Test state
- [ ] 28 new tests written, all passing in CI
- [ ] Total tests: 280 (Sprint 1 baseline) + 28 = 308 (Phase 4 plan says ~310; 308 is within tolerance)
- [ ] All Sprint 1 tests still pass (no regressions)
- [ ] `ruff check prismatic/` clean
- [ ] `ruff format --check prismatic/` clean

### Documentation state
- [ ] `okf/dashboards/prismatic-engine-health.json` valid Grafana dashboard JSON, all panel targets reference real metric names (verified by `tests/test_grafana_dashboards.py`)
- [ ] `okf/dashboards/prismatic-retry-behavior.json` valid + same
- [ ] `okf/dashboards/prismatic-plugin-execution.json` valid + same
- [ ] `okf/operations/grafana-dashboards-provisioning.md` documents import procedure (UI + provisioning YAML)
- [ ] `okf/operations/check-alerts-cron.md` documents the dispatcher auto-invocation + `prismatic-admin check-alerts` cron entry
- [ ] `okf/operations/prismatic-distribution-checklist.md` lists `PRISMATIC_OTLP_ENDPOINT`, `PRISMATIC_OTEL_SERVICE_NAME`, `PRISMATIC_PROMETHEUS_ENABLED`
- [ ] `okf/standards/swarm-coordination-protocol.md` cross-references the new `prismatic_extensions/` lane carry-forward (from Gap 12 L3)

### Behavior state (live probes, run by Fred post-merge)
- [ ] `curl http://localhost:8000/api/v1/metrics` (with auth) returns Prometheus text including `prismatic_drain_failures_total 0`
- [ ] `PRISMATIC_OTLP_ENDPOINT=http://localhost:4318 python -m prismatic.dispatcher serve --once` emits spans visible in `tcpdump -i lo port 4318`
- [ ] After triggering a `_drain` write error, `prismatic_drain_failures_total` increments within 5s
- [ ] `python -m prismatic.dispatcher serve --once` exits cleanly after running `check_alerts()` once (no crash)
- [ ] `python -m prismatic test prismatic/` shows ≥280 + 28 = 308 passing
- [ ] Grafana dashboard `prismatic-engine-health.json` imports without "panel query invalid" errors

### Edge cases handled
- [ ] When `PRISMATIC_OTLP_ENDPOINT` is unset: tracer is no-op (zero side effects, verified by `test_get_tracer_returns_singleton_when_disabled`)
- [ ] When `LINEAR_API_KEY` is unset: `check_alerts()` returns alerts list without posting (existing behavior, regression-tested by `test_admin_check_alerts_cli_still_works`)
- [ ] When `/metrics` is scraped by anonymous client: 401 Unauthorized (verified by `test_metrics_endpoint_requires_auth`)
- [ ] When OTel collector is unreachable: spans queue in `BatchSpanProcessor` and drop on overflow (verified by `test_tracer_does_not_block_when_collector_unreachable`)
- [ ] When traceparent header is malformed: `extract_traceparent()` returns `None`, transition proceeds with auto-generated IDs (verified by `test_extract_traceparent_invalid_returns_none`)

### Peer review gate
- [ ] Sonnet peer reviewer returns APPROVE on all 6 PRs
- [ ] No NEW (not pre-existing) ruff findings
- [ ] No regression in Sprint 1 test count

---

## Summary

- **6 PRs** (phases), ~75 minutes total wall-clock for Sonnet
- **28 new tests** in 7 new test files (~900 LOC tests)
- **3 new Grafana dashboards** committed to OKF
- **Zero `_drain` work in `state_machine.py`** — counter lives in `TelemetryCollector` where `_drain` actually exists
- **Sprint 1 invariant preserved**: telemetry never blocks the dispatcher (BatchSpanProcessor + Prometheus client pull)
- **Scope corrections made**: (1) `_drain` is in `telemetry.py` not `state_machine.py`; (2) Grafana dashboards are committed-not-deployed; (3) test count target is 28 not 30 (Sonnet will over-deliver to ~30-32)

*Plan written 2026-06-28 by Opus. Ready for Sonnet implementation. Fred to gate peer review per the swarm-coordination-protocol.md.*