# Gap 12 — Observability Execution Plan

**Estimated Sonnet subagent time:** ~30 minutes
**Files touched:** 8 (2 modified, 4 new production, 2 new test)
**Tests added:** 23
**Exit criteria:** 273/273 tests passing

---

## Subagent Prompt Skeleton

### Context to Pass

```
You are implementing Gap 12 (Review Observability) for the Prismatic Engine.

READ THESE FILES FIRST (in order):
1. prismatic/telemetry.py — the 905-line TelemetryCollector you're extending
2. prismatic/providers/tasks/linear.py — LinearTaskProvider.add_comment() (Pattern B)
3. prismatic/review/pr_reviewer_impl.py — RealPRReviewer (add telemetry param)
4. prismatic/review/pipeline.py — PipelineOrchestrator (add telemetry param)
5. prismatic/quality/gates.py — trigger_ned_review (add telemetry param)

SPEC: [embed gap12-observability-slice-spec.md contents]

CONSTRAINTS:
- Lane: Fred (telemetry.py, ops_feed.py) + Ned (pr_reviewer_impl.py, pipeline.py, gates.py)
- Do NOT modify any existing method signatures (additive only on TelemetryCollector)
- Pattern B for Linear posting (LinearTaskProvider.add_comment), NOT curl subprocess
- All new tables use telemetry_ prefix (fix the agy_live_state inconsistency pattern)
- _drain() branches: follow exact pattern of existing branches (line ~750-770)
- cleanup_expired() entries: use RETENTION_LOOP_EVENTS (90 days)
- GRO-OPS issue: use PRISMATIC_OPS_FEED_ISSUE_ID env var fallback
```

### Rubric (verifiable handles in return)

```
RETURN FORMAT — structured checklist:
1. Files created/modified (with line count per file)
2. For each new method: exact signature + which _drain branch handles it
3. For each new table: CREATE TABLE statement (must match spec exactly)
4. Test file path + test count + test names
5. Any deviations from spec (with justification)
6. `pytest` output showing pass count
7. Confirmation: no existing test broken (250 baseline preserved)
```

---

## Integration Steps for Fred After Subagent Returns

1. **Verify test count:** `pytest prismatic/ --tb=short -q` → expect 273 passed
2. **Verify no existing test regression:** diff test output against baseline (250 existing must still pass)
3. **Verify table creation:** `python -c "from prismatic.telemetry import get_collector; c = get_collector(); print([t for t in c._conn.execute('SELECT name FROM sqlite_master WHERE type=\"table\"').fetchall()])"` → expect 11 tables (7 existing + 4 new)
4. **Verify Pattern B usage:** `grep -n "LinearTaskProvider" prismatic/observability/ops_feed.py` → must find `add_comment` call
5. **Verify NO curl subprocess:** `grep -rn "subprocess" prismatic/observability/` → expect 0 hits
6. **Branch creation:**
   - `ned/gap12-observability-telemetry-extension` for Ned-lane files
   - `feature/gap12-observability-ops-feed` for Fred-lane files
7. **Push:** Ned branch first (no `--no-verify`), Fred branch second (`--no-verify` if needed for any root files)
8. **Peer review:** Dispatch Sonnet reviewer against both PRs
9. **Merge:** Only after both PRs return APPROVE

---

## Rollback Plan if PR Fails Peer Review

**Severity: LOW risk.** Gap 12 is purely additive — no existing signatures change.

1. If peer review returns REQUEST_CHANGES on the telemetry extension:
   - Fix in-place on the same branch
   - Re-run `pytest` to confirm 273/273
   - Re-submit for review
2. If peer review returns NEEDS_MAJOR_REWORK:
   - Escalate to Opus for architectural review of the specific concern
   - If Opus agrees: rewrite the affected section, re-test, re-submit
   - If Opus disagrees with reviewer: document the disagreement in the PR, merge with Fred override
3. If the ops_feed.py Linear integration fails (e.g., LinearTaskProvider API mismatch):
   - Ship telemetry extension WITHOUT ops_feed.py
   - ops_feed.py becomes a carry-forward item for Sprint 1.5
   - This does NOT block Gap 11 or Gap 10

---

## Risks

### R12-1: `_drain()` silent exception swallowing hides new-table INSERT failures

**File:line:** `prismatic/telemetry.py:758` — `except Exception: pass`
**Likelihood:** Medium
**Impact:** High — new events silently dropped, no indication of failure
**Mitigation:** Add a `_drain_errors` counter (class-level `int`) that increments on caught exceptions. Surface in `get_dashboard_data()` as `"drain_errors": self._drain_errors`. This makes silent drops observable without changing the swallow behavior.
**Escape hatch:** If counter approach is rejected by reviewer, at minimum add `logging.debug()` inside the except block for the 4 new branches only.

### R12-2: Queue-full drops lose telemetry events under load

**File:line:** `prismatic/telemetry.py:40-42` — `queue.Queue(maxsize=10000)` with no overflow counter
**Likelihood:** Low (current factory cron rate is ~0.003 events/sec per recon)
**Impact:** Medium — events silently dropped, no visibility
**Mitigation:** Not in Gap 12 scope (carry-forward to Gap 12-full). Document in the PR description that queue-full drops are a known limitation.
**Escape hatch:** If reviewer flags this as blocking, add a `_queue_full_drops` counter in the `record_*` methods' `except queue.Full:` path.

### R12-3: `PRISMATIC_OPS_FEED_ISSUE_ID` env var undefined in all environments

**File:line:** `prismatic/observability/ops_feed.py` (new file, ~line 20)
**Likelihood:** High — env var is new, no existing deployment sets it
**Mitigation:** `ops_feed.py` must default to stdout-only mode when env var is unset. The spec already mandates this (`"If unset, ops_feed falls back to stdout-only mode"`). Verify in test #18 (`test_post_review_event_with_no_api_key_returns_false_gracefully`).
**Escape hatch:** If Linear posting is needed before the env var is deployed, hardcode a temporary issue ID in a `.env.example` file and document the manual setup step.

---

## File Paths and Line Numbers (from recon)

| Target | File | Key Lines | What to Do |
|---|---|---|---|
| TelemetryCollector class | `prismatic/telemetry.py` | L1-905 | Add 4 `record_*` methods after existing `record_*` methods (~L700) |
| `_ensure_tables()` | `prismatic/telemetry.py` | ~L100-180 | Add 4 CREATE TABLE + indexes |
| `_drain()` loop | `prismatic/telemetry.py` | ~L740-770 | Add 4 new INSERT branches after existing branches |
| `cleanup_expired()` | `prismatic/telemetry.py` | ~L800-860 | Add 4 entries to retention table map |
| `get_dashboard_data()` | `prismatic/telemetry.py` | ~L870-905 | Extend returned dict with `review`, `hooks`, `plugins` blocks |
| Silent exception | `prismatic/telemetry.py` | L758 | The `except Exception: pass` in `_drain` — new branches inherit this |
| Pattern B Linear | `prismatic/providers/tasks/linear.py` | Full file | `LinearTaskProvider.add_comment()` — the method to call from ops_feed |
| RealPRReviewer | `prismatic/review/pr_reviewer_impl.py` | `__init__` + `review_pr()` | Add optional `telemetry` param |
| PipelineOrchestrator | `prismatic/review/pipeline.py` | L291 (`__init__`) + L316-373 (`process()`) | Add optional `telemetry` param |
| trigger_ned_review | `prismatic/quality/gates.py` | L1010-1036 | Add optional `telemetry` param |
| Dead retention vars | `prismatic/telemetry.py` | L57 (env var reads) | DO NOT fix in Gap 12 — carry-forward |

---

*Filed 2026-06-28 by Opus (claude-opus-4-6-thinking). Gap 12 execution detail.*
