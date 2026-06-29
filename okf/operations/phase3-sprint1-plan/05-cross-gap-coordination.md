# Cross-Gap Coordination

---

## File Conflicts Between Gaps

### Files touched by multiple gaps

| File | Gap 12 | Gap 11 | Gap 10 | Conflict Type |
|---|---|---|---|---|
| `prismatic/review/pipeline.py` | Adds `telemetry` param to `__init__` + `process()` | Adds `registry` param to `__init__` + `apply_impact_rules` call in `process()` | — | **SEQUENTIAL MERGE CONFLICT.** Gap 11 must merge on top of Gap 12's changes to `__init__` and `process()`. Both add keyword-only params. |
| `prismatic/review/pr_reviewer_impl.py` | Adds `telemetry` param to `__init__` + `record_review_completed` call | Fires `HOOK_BEFORE_SECRET_SCAN` + `HOOK_BEFORE_QUALITY_CHECKS` in `review_pr()` | — | **LOW CONFLICT.** Different insertion points (Gap 12: success path; Gap 11: before secret scan / quality checks). But both modify `review_pr()`. |
| `prismatic/quality/gates.py` | Adds `telemetry` param to `trigger_ned_review()` | Fires `HOOK_BEFORE_NED_REVIEW` in `trigger_ned_review()` | — | **LOW CONFLICT.** Both modify the same function but at different insertion points (telemetry after review; hook before review). |
| `prismatic/review/registry.py` | — | Updates `register_impact_rule()` docstring | — | No conflict — Gap 12 doesn't touch this file. |
| `prismatic/review/hooks.py` | — | Updates all `HOOK_*` docstrings | — | No conflict. |
| `prismatic/review/__init__.py` | — | Exports `apply_impact_rules` | Exports `discover_and_register_plugins` | **LOW CONFLICT.** Both add exports to the same file. Strictly sequential (Gap 11 first). |
| `prismatic/dispatcher.py` | — | — | Adds `discover_and_register_plugins()` call | No conflict — only Gap 10 touches this file. |
| `prismatic/telemetry.py` | Adds 4 methods, 4 tables, 4 drain branches, 4 cleanup entries | — | — | No conflict — only Gap 12 touches this file. |

### Conflict Resolution Strategy

The **strict sequential order** (Gap 12 → Gap 11 → Gap 10) eliminates all merge conflicts:

1. Gap 12 lands first. `pipeline.py:__init__` gains `telemetry` param.
2. Gap 11 lands second. `pipeline.py:__init__` gains `registry` param. The subagent sees the post-Gap-12 state and adds its param alongside `telemetry`.
3. Gap 10 lands third. No overlap with Gap 11/12 modified files (only `dispatcher.py` + `__init__.py` exports).

**Critical constraint:** Each subagent MUST read the current file state (post-previous-gap) before making changes. The subagent prompt includes the file list; Fred verifies the subagent is working against the correct baseline.

---

## Test Interleaving

### Can Gap 12 + Gap 11 tests run together?

**Yes.** No isolation needed. Rationale:

- Gap 12 tests (`test_telemetry_extension.py`, `test_ops_feed.py`) test `TelemetryCollector` methods and `ops_feed.py` — no dependency on Gap 11's wiring.
- Gap 11 tests (`test_wire_deferrals.py`) test `apply_impact_rules`, `fire_hook`, and end-to-end review-through-pipeline — no dependency on Gap 12's telemetry tables.
- The one overlap: Gap 12's integration tests (#22, #23) use `RealPRReviewer(telemetry=...)` and `PipelineOrchestrator(telemetry=...)`. After Gap 11 lands, these constructors also accept `registry`. The tests pass `telemetry=` but not `registry=`, which is fine (both are optional kwargs with `None` defaults).

### Can Gap 10 tests run with Gap 11 + Gap 12 tests?

**Yes, with one caveat:**

- Tests #9-11 in Gap 10 (`TestRealPluginEndToEnd`) require `pip install -e plugins/prismatic-hello-world`. These tests may be marked `@pytest.mark.integration` or `@pytest.mark.skipif` for CI.
- All other Gap 10 tests mock `entry_points()` and don't depend on installed plugins.
- No conflict with Gap 11 or Gap 12 test fixtures.

### Test count progression

| Stage | Expected Count | Delta |
|---|---|---|
| Baseline (deploy-fresh) | 250 | — |
| After Gap 12 | 273 | +23 |
| After Gap 11 | 290 | +16 new, +1 updated (net: 290, not 291, because the updated test replaces the old assertion) |
| After Gap 10 | 302 | +13 (includes 1 updated test from PR #43 already counted in baseline) |

**Note:** The spec says "302/302" as the sprint target. The arithmetic: 250 + 23 + 17 + 13 = 303. But 1 test is an UPDATE (not a net-new), so: 250 + 23 + 16 + 13 = 302. The updated test (`test_register_impact_rule_docstring_warns`) doesn't add to the count — it replaces an existing test's assertion.

---

## Order Rationale: Why Gap 12 → Gap 11 → Gap 10

### Option A (chosen): Gap 12 → Gap 11 → Gap 10

**Rationale:**
1. **Observability before wiring.** Gap 12 adds telemetry params to `PipelineOrchestrator` and `RealPRReviewer`. Gap 11 then wires hooks and impact rules into these same objects, and can emit telemetry events as hooks fire. If Gap 11 went first, telemetry calls would need to be added in a follow-up pass.
2. **Wiring before discovery.** Gap 11 wires `register_impact_rule()` so it's no longer inert. Gap 10 then advertises it in the distribution checklist and reference plugin docs. If Gap 10 went first, the docs would say "impact rules are supported" but they'd still be dead.
3. **Simplest merge graph.** The file-conflict analysis shows `pipeline.py` is touched by both Gap 12 and Gap 11. Sequential ordering avoids merge conflicts entirely.

### Option B (rejected): Gap 11 → Gap 12 → Gap 10

**Problem:** Gap 11 would add `registry` param to `PipelineOrchestrator`, but there's no telemetry to observe hook firings. Gap 12 would then need to add telemetry calls into the hook dispatch paths that Gap 11 just wrote — a cross-concern edit that's harder to review.

### Option C (rejected): Gap 10 → Gap 11 → Gap 12

**Problem:** Gap 10 ships plugin discovery before `register_impact_rule()` is wired. The reference plugin and distribution checklist would need to warn "impact rules don't work yet" — contradicting the goal of shipping a functional plugin authoring experience.

---

## Hidden Dependencies the Specs Might Have Missed

### 1. `PipelineOrchestrator.__init__` double-expansion

Gap 12 adds `telemetry: TelemetryCollector | None = None`. Gap 11 adds `registry: ReviewerRegistry | None = None`. After both, the signature is:

```python
def __init__(
    self,
    max_rework_attempts: int = DEFAULT_MAX_REWORK_ATTEMPTS,
    *,
    registry: ReviewerRegistry | None = None,
    telemetry: TelemetryCollector | None = None,
) -> None:
```

**Risk:** Any existing caller that uses positional args for `max_rework_attempts` is fine. But if anyone passes `registry=` or `telemetry=` before their respective gaps land, they'll get `TypeError`. Since both are `None`-defaulted keyword-only args, this is safe — but the specs don't mention the combined post-sprint signature.

### 2. Gap 11's `fire_hook()` could emit telemetry if Gap 12's telemetry param is available

The specs treat these as independent, but in practice: if `PipelineOrchestrator` has both `registry` and `telemetry`, then `fire_hook()` could call `telemetry.record_hook_fired()` as part of dispatch. The Gap 12 spec defines `record_hook_fired()` but doesn't say who calls it. The Gap 11 spec defines `fire_hook()` but doesn't mention telemetry.

**Resolution:** The caller of `fire_hook()` (inside `process()` or `review_pr()`) should call `telemetry.record_hook_fired()` after `fire_hook()` returns. This is a ~3-line addition per call site. It's not in either spec but is the natural integration point. Fred should add this in the Gap 11 integration step.

### 3. Gap 10's `discover_and_register_plugins()` should emit `telemetry.record_plugin_registered()` 

Gap 12 defines `record_plugin_registered()`. Gap 10 defines `discover_and_register_plugins()`. Neither spec says one should call the other.

**Resolution:** `discover_and_register_plugins()` should accept an optional `telemetry` param and call `telemetry.record_plugin_registered()` for each plugin (success or failure). This is a ~5-line addition. Fred should add this in the Gap 10 integration step.

### 4. `test_register_impact_rule_docstring_warns` baseline count uncertainty

PR #43 added this test, bringing the baseline from 247 to 249. The recon says "250/250 on deploy-fresh." There may be 1 additional test from another source. The Sprint 1 test count target (302) assumes 250 as baseline. If the baseline is actually 249 or 251, the target shifts by ±1.

**Resolution:** Fred runs `pytest --co -q` before starting Gap 12 to get the exact baseline count, and adjusts the target accordingly.

---

*Filed 2026-06-28 by Opus (claude-opus-4-6-thinking). Cross-gap coordination analysis.*
