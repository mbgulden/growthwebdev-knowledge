# Phase 3 Sprint 1 — Reconnaissance Report

**Date:** 2026-06-28
**Trigger:** Second-opinion reviews flagged CRITICAL Gap 12 miss (invented parallel observability when `prismatic/telemetry.py` already exists). Full recon ordered before rewriting specs.
**Coverage:** 3 parallel recon tasks (telemetry API map, entry-points discovery, hook/impact wiring)
**Outcome:** Real ground truth for all 3 spec areas. Specs can now be rewritten grounded in codebase reality.

---

## Recon 1 — `prismatic/telemetry.py` API Map

**File:** 905 lines, single class `TelemetryCollector`, single singleton via `get_collector()`

### Public methods (full list — I missed `update_agent_run`, `check_circuit`, `reset_breaker`, `check_alerts`, `cleanup_expired` in my original spec)

| Method | Signature |
|---|---|
| `record_loop` | `(run_id, issue_id, agent, loop_type, trigger=None, resolved=False, depth=0, parent_id=None)` |
| `record_tokens` | `(run_id, agent, provider, model=None, prompt_tokens=0, completion_tokens=0, ttft_ms=0.0, tps=0.0, context_pct=0.0, vram_mb=0)` |
| `record_validation` | `(run_id, agent, event_type, total=0, passed=0, failed=0, sandbox_id=None, rollback=False, watch_sec=0.0)` |
| `record_agent_run` | INSERT/REPLACE at dispatch |
| **`update_agent_run`** | UPDATE on completion (credits are **incrementally** added) |
| `record_credit` | Append-only ledger row |
| `record_agy_live_state` | AGY runtime snapshot |
| **`check_circuit`** | Synchronous breaker check + auto-loop event on trip |
| **`reset_breaker`** | DELETE row after human intervention |
| `get_dashboard_data` | The single read API for the ops dashboard |
| **`check_alerts`** | Evaluates 3 rules; optional Linear posting |
| **`cleanup_expired`** | Per-table retention sweep; `dry_run=True` mode |

### Database schema (7 tables in `event_router.db`)
- `telemetry_loop_events` — includes auto-pushed `circuit_breaker` events
- `telemetry_circuit_breakers` — state machine under `BEGIN IMMEDIATE`
- `telemetry_token_metrics`
- `telemetry_validation_events` — co-opted for `review_verdict` kludge
- `telemetry_agent_runs`
- `telemetry_credit_ledger` — Phase 4.4 billing columns added via in-line migration
- `agy_live_state` — **inconsistent**: no `telemetry_` prefix

### Threading model
- `queue.Queue(maxsize=10000)` typed `queue.Queue[tuple[str, dict]]`
- Single daemon thread (`self._writer`)
- **Drop policy: silent on full queue** (no counter, no log)
- **Drain loop: swallows ALL exceptions** (line 758: `except Exception: pass`)
- **No `shutdown()`/`close()`/`flush()` method**

### Two parallel Linear posting patterns (pick one to extend)
- **Pattern A — curl subprocess** (used by telemetry.py + credit_tracker.py): body interpolated raw into GraphQL string, breaks on `"` in body
- **Pattern B — urllib.request GraphQL client** (canonical: `prismatic/providers/tasks/linear.py`): uses variables, proper escaping, returns `bool`

**Recommendation:** Pattern B. Extend `LinearTaskProvider`.

### Configuration env vars (all defaults, all read at import)
- `PRISMATIC_STATE_DIR` — DB path root
- `PRISMATIC_BREAKER_MICRO_MAX=5`, `PRISMATIC_BREAKER_MACRO_MAX=3`
- `PRISMATIC_ALERT_CREDIT_BURN=1000`, `PRISMATIC_ALERT_LOOP_COUNT=5`, `PRISMATIC_ALERT_FAILURE_RATE=0.20`, `PRISMATIC_ALERT_WINDOW_HOURS=1`
- `PRISMATIC_RETENTION_AGENT_RUNS=30`, `PRISMATIC_RETENTION_TOOL_CALLS=7` (dead), `PRISMATIC_RETENTION_LOOP_EVENTS=90`, `PRISMATIC_RETENTION_RESOURCE_SNAPSHOTS=1` (dead), `PRISMATIC_RETENTION_CREDIT_LEDGER=90`

### Two retention env vars are dead
- `PRISMATIC_RETENTION_TOOL_CALLS` — no `telemetry_tool_calls` table
- `PRISMATIC_RETENTION_RESOURCE_SNAPSHOTS` — no `telemetry_resource_snapshots` table

### Surprises / Gotchas
1. **Orphan `prismatic/vertex_telemetry.py`** (594 lines) — module docstring says `prismatic/telemetry/gcp_vertex.py`, leftover from earlier move
2. **Deleted but still cached `prismatic/telemetry/__pycache__/`** — had `_collector`, `metrics`, `tracer`, `gcp_vertex` modules. Tracing support was collapsed into the single file.
3. **Two parallel alert systems** — `telemetry.check_alerts` (rules: credit_burn, loop_count, failure_rate) and `gateway/alert_manager.AlertEvaluator` (rules: HighLockContention, AgentStall, CreditBurnRate) both read `get_dashboard_data()`
4. **`check_alerts` is never called automatically** — zero callers in repo
5. **`update_agent_run` is additive on `credits_spent`** — `credits_spent = credits_spent + ?` (line 717) — non-obvious
6. **`get_dashboard_data` is the only query API** — no per-issue, per-run, or per-time-series queries
7. **`agy_live_state` lacks `telemetry_` prefix** — inconsistency to fix
8. **`_drain` swallows ALL exceptions silently** — debugging instrumentation failures is hard
9. **No `shutdown`/`flush`** — last ~1 second of telemetry lost on clean shutdown
10. **No direct tests of `TelemetryCollector`** — only mock-based and `test_cost_attribution.py:343-407` indirect tests

### Extension pattern (validated by subagent)
Adding 4 new `record_*` methods + 4 new tables + 4 new `_drain` branches + 4 new `cleanup_expired` entries is a **~150-line PR** touching one file.

---

## Recon 2 — Entry-Points Discovery

### What's declared
- **One entry-point group** in the codebase: `prismatic.plugins` (pyproject.toml:73)
- Group is **declared but the consumer is unwired** — zero calls to `importlib.metadata.entry_points()` in any `.py` file
- Verified live: `entry_points(group="prismatic.plugins")` returns `[]` — no plugins installed

### Two parallel plugin systems coexist (uncoordinated!)

**OLD — Filesystem-based (`prismatic/core/registry.py::PluginLoader`, 212 lines)**
- Walks `$PRISMATIC_HOME/plugins/`, reads `plugin-manifest.yaml`
- Validates `core_version_constraint`, `hardware_profile`, `execution_profile`
- Subclasses `PrismaticPlugin` ABC (`prismatic/interface/plugin.py`)
- Exposes `register_tools()`, `personas`, hook methods (`on_init`, `before_task_execution`)
- Examples live in `/home/ubuntu/work/prismatic-engine/plugins/` (12 dirs)
- **`PluginLoader` is not called from anywhere in production** — grep confirms zero callers

**NEW — Registry-based (`prismatic/review/registry.py::ReviewerRegistry`, 215 lines)**
- Additive composition: `register_secret_pattern` / `register_check` / `register_impact_rule`
- No validation, no version checks, no hooks, no tools
- `register_impact_rule` is explicitly **inert** (docstring L155-169)

### `ReviewerRegistry` gaps a real plugin author would hit
1. No `unregister_*` methods
2. No `__repr__` / `__iter__`
3. No `reset()` / `clear()` / context manager
4. **No plugin-source tagging** — once `discover_and_register_plugins()` runs, you can't tell which entry-point contributed which check
5. No structured error type (silent accept of broken callables)
6. `register_impact_rule` is a trap (currently inert)
7. `register_check` dedup is partial (named replaces, unnamed appends)
8. **No way to register hooks via registry** — review-side hooks vs core hooks are entirely separate APIs

### Pip-installed prismatic packages
- `prismatic-engine 0.1.0` (self)
- `prismatic-hub 0.1.0` (at `/tmp/agy_sandboxes/GRO-1664`)
- `prismatic-web-plugin 0.1.0` (at `/home/ubuntu/work/prismatic-web-plugin`)

**Zero** register under `prismatic.plugins`. The web-plugin ships only a CLI script.

### Distribution checklist gaps
11+ items missing for a real plugin author:
- No `register(registry)` signature contract
- No load-order / error-isolation / duplicate-resolution spec
- No reference entry-points-style plugin
- No debug-logging story
- No Windows/macOS guidance
- No version-compatibility check on the new path

---

## Recon 3 — Hook Dispatch + Impact-Rule Wiring

### `PipelineOrchestrator` (verified: spec.impact_rules NOT consumed)

`__init__` (line 291): `(max_rework_attempts: int = DEFAULT_MAX_REWORK_ATTEMPTS) = 2)` — **no registry param**

`process()` body (lines 316-373):
- Holds `threading.Lock` for full body (line 331)
- Calls `classify_impact(result)` (L332)
- Calls `decide_next_action(result, rework_attempts=attempts, max_rework_attempts=self.max_rework_attempts)` (L334-338)
- Builds rework_payload if action == ACTION_REWORK (L347-354)
- Returns `PipelineDecision(...)`

**Confirmed: `spec.impact_rules` is never read by `PipelineOrchestrator.process()`.** Subagent claim verified.

### `RealPRReviewer.review_pr` registry consumption points
- `spec.secret_patterns` consumed in `_detect_secrets_with_registry` (line 592) ✅ wired
- `spec.checks` consumed in loop (line 513) ✅ wired
- `spec.impact_rules` **never consumed** ❌ inert

### `trigger_ned_review` integration points (3 candidates)
1. Before review (L1010-1028) — fires `HOOK_BEFORE_NED_REVIEW`
2. After review (L1028-1035) — fires `HOOK_AFTER_NED_REVIEW` (not defined)
3. Before pipeline (L1034-1036) — fires `HOOK_BEFORE_CLASSIFY_IMPACT`

### HOOK_* dispatch code (verified: zero in production)
- 5 constants defined in `hooks.py` L43-82
- `ALL_HOOKS` tuple L93-99
- Module docstring L26-31: "Dispatch code is NOT YET WIRED"
- **Zero production consumers** — repo-wide grep confirms only test file references

### impact_rules tests — Lesson 10 anti-pattern VERIFIED
- `test_rules_fire_in_registration_order` (L137-159): manually iterates `spec.impact_rules`, passes `None` as result
- `test_first_non_none_wins` (L161-183): same manual pattern
- **Both would pass even if `PipelineOrchestrator` never wired impact_rules** — test bypasses production code entirely
- `test_register_impact_rule_docstring_warns` (L370-387): asserts "Currently inert" warning string — **will need to be updated** when wiring lands

### Tests pass/fail
- 29 tests pass in `test_registry.py`
- 0 integration tests for impact_rules through `RealPRReviewer.review_pr()` or `PipelineOrchestrator.process()`

---

## Cross-Cutting Surprises

1. **Two parallel plugin systems, zero bridge** — old `PluginLoader` (filesystem) vs new `ReviewerRegistry` (entry-points). Gap 10 needs to decide: bridge, replace, or leave alone.

2. **Two parallel telemetry/alert systems** — `telemetry.check_alerts` vs `gateway/alert_manager.AlertEvaluator`. Gap 12 should pick one.

3. **Two parallel Linear posting patterns** — `curl subprocess` (broken escaping) vs `urllib.request` (canonical). Gap 12 should use Pattern B.

4. **`register_impact_rule` is currently a trap** — Gap 11 fixes this. But Gap 10 must NOT advertise it as a working API until Gap 11 lands.

5. **Dead retention env vars** — `PRISMATIC_RETENTION_TOOL_CALLS` and `PRISMATIC_RETENTION_RESOURCE_SNAPSHOTS` reference tables that don't exist. Cleanup candidate.

6. **`agy_live_state` table missing `telemetry_` prefix** — minor inconsistency to fix when adding new tables.

---

## Implications for the 3 Specs

### Gap 10 (Plugin Auto-Discovery)
- Now know: **two plugin systems coexist, no bridge.** Gap 10 must explicitly scope to the new `prismatic.plugins` entry-point group, leaving the old `PluginLoader` alone.
- Now know: **`register_impact_rule` is inert** — Gap 10's docs must NOT advertise it as working.
- Now know: **No reference plugin exists** — Gap 10 should include a `prismatic-hello-world` reference plugin as part of the PR.

### Gap 11 (Wire the Deferrals)
- Now know: **`PipelineOrchestrator.__init__` needs a `registry` param** — that's the breaking change.
- Now know: **`trigger_ned_review` integration points** are well-defined (3 candidates, 1 obvious choice: before reviewer).
- Now know: **`PipelineOrchestrator._lock` is held across the full process() body** — hook firing inside the lock will serialize reviews if handlers are slow.
- Now know: **`update_agent_run` is additive on credits_spent** — relevant if we emit telemetry from the pipeline.
- Now know: **`test_register_impact_rule_docstring_warns` must be updated** when wiring lands.

### Gap 12 (Observability)
- Now know: **`TelemetryCollector` is the canonical extension point** — add 4 new `record_*` methods.
- Now know: **Pattern B Linear posting** (`LinearTaskProvider.add_comment`) is the right integration point.
- Now know: **`GCP_OPS` issue may not exist** — fallback strategy needed.
- Now know: **Queue-full silent drops + drain exception swallowing** are real operational hazards.
- Now know: **6 of 6 review event types are missing** from telemetry — extension is purely additive, no migration.

---

*Filed 2026-06-28 by Fred (orchestrator). 3 parallel recon tasks via `delegate_task` with claude-sonnet-4-6.*
