# Phase 3 / Sprint 1 — Master Risk Register

**Date:** 2026-06-28
**Sprint:** Phase 3 / Sprint 1 (Gaps 12, 11, 10, then meta-review)
**Owner:** Fred (orchestrator)
**Source:** Opus plan + subagent recon findings + my own audit

---

## Risk scoring

- **Likelihood:** low / medium / high
- **Impact:** low / medium / high
- **Risk score:** likelihood × impact (qualitative)
- **Mitigation:** action BEFORE the risk materializes
- **Escape hatch:** recovery path IF it slips through

---

## R1 — Telemetry `_drain` silent exception swallowing

- **Description:** `prismatic/telemetry.py:758` has `except Exception: pass`. If any of the 4 new INSERT branches in Gap 12 have a SQL error (constraint mismatch, schema drift, data corruption), it is invisible in production.
- **Likelihood:** Medium (4 new tables + 4 new INSERT branches = more attack surface)
- **Impact:** Medium (telemetry black hole for review events; doesn't break dispatcher but defeats the purpose of Gap 12)
- **Risk score:** Medium
- **Mitigation:**
  - Gap 12 tests must cover parameterized query paths exhaustively
  - Tests must include "INSERT raises" scenarios with mock
  - Schema must be created idempotently (`CREATE TABLE IF NOT EXISTS`) — verify in tests
- **Escape hatch:**
  - Add a `_drain_failure_counter` to `TelemetryCollector` (increment on exception)
  - Sprint 2 carry-forward if R1 manifests in production

## R2 — `PipelineOrchestrator(registry=...)` breaking change

- **Description:** Gap 11 changes `PipelineOrchestrator.__init__` signature. Any existing caller that uses positional args may break.
- **Likelihood:** Low (signature is `(self, max_rework_attempts: int = 2)` — adding `*, registry` makes it keyword-only, which is backward-compatible)
- **Impact:** High (would break existing pipeline callers in tests + production)
- **Risk score:** Medium
- **Mitigation:**
  - The Gap 11 spec uses `*, registry` syntax (keyword-only) — confirmed backward-compatible
  - All 30 existing `test_pipeline.py` tests must pass without modification
  - Add a `test_pipeline_with_no_registry_backward_compat` test that asserts the old signature still works
- **Escape hatch:**
  - If a test breaks, fix the test or add a compat shim; do not modify the signature

## R3 — Reference plugin `prismatic-hello-world` trips GitHub push scanner

- **Description:** The reference plugin in Gap 10 lives in `plugins/prismatic-hello-world/`. If its source contains literal secret-like strings, GitHub's push-protection scanner may block the push.
- **Likelihood:** Low (the reference plugin is benign — a single check for the word "hello" in diffs)
- **Impact:** High (blocks PR merge)
- **Risk score:** Medium
- **Mitigation:**
  - Reference plugin uses lowercase "hello" check — no secret-like patterns
  - Use `push-protection-secret-fixtures` skill (already in OKF) for any test fixtures that need to look like secrets
- **Escape hatch:**
  - If scanner blocks, use `--no-verify` push (lane governance pre-commit hook will pass; push scanner may need manual approval)
  - Or rewrite the test to use `monkeypatch.setattr` to inject patterns at test time

## R4 — `agy_live_state` table inconsistency causes test fixture collisions

- **Description:** `agy_live_state` is the only table without the `telemetry_` prefix. If Gap 12 tests assume a `telemetry_agy_live_state` table name, they'll fail.
- **Likelihood:** Low (Gap 12 spec explicitly uses `telemetry_` prefix for new tables)
- **Impact:** Low (cosmetic inconsistency, not a functional bug)
- **Risk score:** Low
- **Mitigation:**
  - Gap 12 tests use new table names with `telemetry_` prefix (verified in spec)
  - Don't touch `agy_live_state` in Gap 12 (out of scope)
- **Escape hatch:**
  - If the inconsistency causes integration issues, Gap 12-full (Sprint 2) includes a schema migration to rename `agy_live_state` → `telemetry_agy_live_state`

## R5 — Two dead retention env vars reference non-existent tables

- **Description:** `PRISMATIC_RETENTION_TOOL_CALLS` and `PRISMATIC_RETENTION_RESOURCE_SNAPSHOTS` reference `telemetry_tool_calls` and `telemetry_resource_snapshots` tables that don't exist. The cleanup sweep would no-op silently.
- **Likelihood:** Low (env vars are dead, not used)
- **Impact:** Low (cosmetic; doesn't affect telemetry functionality)
- **Risk score:** Low
- **Mitigation:**
  - Gap 12 doesn't touch retention env vars (out of scope)
  - Document as carry-forward in the Gap 12 spec
- **Escape hatch:**
  - Gap 12-full removes the dead env vars + cleans up `cleanup_expired()` retention map

## R6 — Spec assumption: "Hook fires inside lock serializes concurrent reviews"

- **Description:** Opus flagged: "Hook handlers firing inside `PipelineOrchestrator._lock` will serialize concurrent reviews." If a hook handler does I/O (e.g., a `HOOK_BEFORE_NED_REVIEW` that fetches a URL), reviews serialize on it.
- **Likelihood:** Medium (real concern; this is what makes the hook integration correctness-critical)
- **Impact:** Medium (slow hooks = slow reviews = factory backlog)
- **Risk score:** Medium
- **Mitigation:**
  - Gap 11 spec keeps `apply_impact_rules` (the impact/action hook dispatch) inside the lock — these are CPU-only
  - HOOK_BEFORE_NED_REVIEW fires in `trigger_ned_review()` BEFORE the lock is acquired — handled correctly
  - HOOK_BEFORE_SECRET_SCAN / HOOK_BEFORE_QUALITY_CHECKS fire inside `RealPRReviewer.review_pr()` — not under any lock
- **Escape hatch:**
  - Document that hooks must be CPU-only / fast; add a hook timeout in Sprint 2 (deferred)
  - Long-running hooks should be implemented as a separate async worker (Sprint 3+)

## R7 — Subagent fabricates test results

- **Description:** Sonnet subagent reports "all tests pass" but actually skipped or mocked tests to make them pass.
- **Likelihood:** Medium (Lesson 10 anti-pattern: tests with good coverage can hide dead APIs)
- **Impact:** High (would ship a broken PR)
- **Risk score:** High
- **Mitigation:**
  - Every subagent prompt requires live probes (REPL `python3 -c "..."`) in the return summary
  - Fred runs `python3 -m pytest prismatic/` independently after subagent returns
  - Peer review (Sonnet on the merged PR) catches cross-file consistency issues
- **Escape hatch:**
  - If PR ships with fabricated tests, rollback PR + restart with stricter subagent prompt
  - Add a "test integrity audit" step to the per-PR integration checklist (Gap 12-full)

## R8 — Linear `LinearTaskProvider` API drift

- **Description:** Gap 12 ops_feed module depends on `prismatic/providers/tasks/linear.py::LinearTaskProvider.add_comment()`. If that module is changed in a parallel gap or by another team, Gap 12 breaks.
- **Likelihood:** Low (LinearTaskProvider is stable)
- **Impact:** Medium (would silently fall back to stderr-only mode, no Linear comments posted)
- **Risk score:** Low
- **Mitigation:**
  - Gap 12 spec tests mock `LinearTaskProvider` — verifies integration is correct
  - The `post_review_event_to_linear()` function returns `bool` — caller can check and fall back
- **Escape hatch:**
  - If API drifts, ops_feed falls back to stderr-only mode (warning logged)
  - Sprint 2 adds retry + circuit-breaker for the Linear API

## R9 — 6 review event types get added to telemetry but never queried

- **Description:** Gap 12 adds 4 tables + 23 tests + ops_feed, but if no downstream consumer queries the data (dashboards, alerts, weekly reports), the value is zero.
- **Likelihood:** Medium (building data plumbing without consumers is a common trap)
- **Impact:** Medium (Gap 12 ships successfully but produces no operational value)
- **Risk score:** Medium
- **Mitigation:**
  - Gap 12 spec extends `get_dashboard_data()` with `review`, `hooks`, `plugins` blocks — these ARE the consumer
  - Sprint 2 (Gap 12-full) adds Grafana / dashboards
- **Escape hatch:**
  - If no consumer ships in Sprint 2, query the tables directly via `sqlite3` for ad-hoc reports
  - Phase 4 (Sprint 3+) includes a feedback loop that surfaces review stats in Linear

## R10 — Test count arithmetic drift across the sprint

- **Description:** Opus flagged that test counts across 3 gaps + 1 updated test must be precisely tracked. Off-by-one errors in PR descriptions confuse reviewers.
- **Likelihood:** Medium (easy to miscount when 52 new tests + 1 update)
- **Impact:** Low (cosmetic; reviewers can run `pytest --collect-only` to verify)
- **Risk score:** Low
- **Mitigation:**
  - Each PR description includes "Baseline: 250, Adds: N, Total after merge: N+250"
  - Fred verifies the actual count via `pytest --collect-only | grep "test_" | wc -l` before each PR
- **Escape hatch:**
  - If count is wrong in description, fix in PR comments — don't block merge

## R11 — Subagent tries to modify out-of-lane files

- **Description:** Gap 12 Sonnet subagent may try to modify `prismatic/review/pr_reviewer_impl.py` (Ned lane) to wire telemetry. The lane governance pre-push hook will block the push.
- **Likelihood:** Medium (Sonnet doesn't know lane governance)
- **Impact:** Low (pre-push hook catches it; Fred can extract the changes into a separate Ned PR)
- **Risk score:** Low
- **Mitigation:**
  - Gap 12 prompt explicitly lists out-of-scope files ("do NOT modify these files")
  - Fred checks `git diff` after subagent returns for any out-of-lane changes
- **Escape hatch:**
  - If out-of-lane changes exist, extract them into a separate Ned PR (Gap 11) and revert the Gap 12 changes

---

## Risk score summary

| ID | Risk | Score |
|---|---|---|
| R7 | Subagent fabricates tests | High |
| R1 | `_drain` silent swallowing | Medium |
| R2 | Pipeline signature breaking change | Medium |
| R3 | Push scanner blocks plugin PR | Medium |
| R6 | Hook serializes concurrent reviews | Medium |
| R9 | No consumer queries new telemetry | Medium |
| R11 | Out-of-lane file modifications | Low |
| R4 | agy_live_state inconsistency | Low |
| R5 | Dead retention env vars | Low |
| R8 | Linear API drift | Low |
| R10 | Test count arithmetic drift | Low |

**Top 3 to monitor actively:** R7, R1, R6.

---

*Filed 2026-06-28 by Fred (orchestrator). Continuation of Opus's interrupted plan output.*
