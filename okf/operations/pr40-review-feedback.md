# PR #40 Review — Gap 9 / Part A: Wire Factory to `RealPRReviewer` + `PipelineOrchestrator`

**Branch:** `ned/gap9-wire-factory`  
**Reviewed at:** 2026-06-28T18:47Z  
**Reviewer:** AGY (agy-as-reviewer lane)

---

## Review Verdict: APPROVE

---

### Evidence Reviewed

| Artifact | Status |
|---|---|
| `prismatic/quality/gates.py` L956–L1090 (`trigger_ned_review`) | ✅ Read in full |
| `prismatic/quality/test_gates.py` `TestTriggerNedReview` class (7 tests) | ✅ Read in full |
| `prismatic/review/pr_reviewer_impl.py` (`RealPRReviewer`) | ✅ Read in full |
| `prismatic/review/pipeline.py` (`PipelineOrchestrator`, `PipelineDecision`, `ReworkPayload`) | ✅ Read in full |
| `prismatic/review/pr_reviewer.py` (`PRReviewResult.__post_init__` validator) | ✅ Verified via probe |
| All 7 new tests run: `python3 -m pytest prismatic/quality/test_gates.py::TestTriggerNedReview -v` | ✅ 7/7 passed |
| Full `test_gates.py` suite | ✅ 61/61 passed (no regressions) |
| Live probes: default reviewer, backward compat, pipeline propagation, exception paths, rework serialization | ✅ All correct |

---

### Strengths

- **Default wiring is correct and tested.** `reviewer = reviewer or RealPRReviewer()` (line 1027) is the idiomatic Python sentinel pattern. The test `test_default_reviewer_is_real_not_stub` uses `monkeypatch` + `__init__` tracking to assert exactly one `RealPRReviewer` was constructed — this is a meaningful behavioral assertion, not a whitebox spy.

- **Backward compatibility preserved.** Explicit `reviewer=StubPRReviewer()` injection still works. Verified both in `test_explicit_stub_reviewer_overrides_default` and live probe. No existing callers are broken.

- **Pipeline integration is clean.** The `pipeline` param is keyword-only (after `*`), eliminating positional confusion with `reviewer`. When `pipeline` is `None`, zero side effects; no `"pipeline"` key in metadata. When provided, `process()` is called with the correct kwargs, and the full `PipelineDecision` is serialized to a plain dict — including `rework_payload` fields enumerated explicitly (not `asdict()`) which is intentional since `ReworkPayload` is a dataclass and `asdict()` would have worked too, but the explicit mapping makes the contract visible.

- **rework_payload serialization is complete.** Live probe confirmed: a `REQUEST_CHANGES` result + `PipelineOrchestrator` → `pipeline_decision['rework_payload']` is a fully populated dict with all 7 fields (`issue_identifier`, `pr_url`, `verdict`, `summary`, `findings`, `rework_attempt`, `max_rework_attempts`, `rework_label`).

- **Exception propagation policy is consistent and tested.** `reviewer.review_pr()` and `pipeline.process()` both propagate exceptions (raw re-raise). Only `post_comment` and `transition_state` (Linear I/O) are caught and stored in metadata — correct asymmetry: reviewer/pipeline failures represent bad inputs or infra that should alert, while Linear comment/state failures should not crash the orchestrator.

- **`PRReviewResult` validator is a safety net.** `__post_init__` raises `ValueError` for any verdict not in `{APPROVE, REQUEST_CHANGES, NEEDS_DISCUSSION}`, so the `NED_REVIEW_TARGET_STATE[result.verdict]` dict lookup at line 1062 can never `KeyError` in production.

- **No metadata contract breakage.** Downstream consumers (`hermes.py`, `pipeline.py`) use `.get()` with defaults or access distinct keys (`status`, `critical_count`, etc.). The new `"pipeline"` key is additive only; no existing key is renamed or removed.

- **Test quality is high.** The 7 tests cover: default wiring, explicit injection, pipeline invoked/omitted, exception propagation, label-missing early-exit, and pr-url-missing early-exit. They test observable behavior (what is returned, what was constructed), not implementation details that would break on refactor.

---

### Issues Found

- **Low — Test name is semantically inverted.** `test_real_reviewer_failure_does_not_crash_trigger` asserts `pytest.raises(RuntimeError)`, meaning the exception *does* crash the trigger. The docstring says "the trigger must *surface* the exception", which is correct policy, but the test *name* says "does not crash." A future reader may misread the intent. Suggested rename: `test_real_reviewer_exception_propagates` or `test_reviewer_failure_surfaces_exception`.

- **Low — No test for `pipeline.process()` exception propagation.** The test for `reviewer.review_pr()` raising exists. There is no equivalent test asserting that `pipeline.process()` raising also propagates (rather than being silently swallowed like `post_comment`/`transition_state`). This was confirmed correct via live probe, but the policy asymmetry (I/O callbacks caught; core logic propagated) deserves explicit test coverage. This is a gap in the test suite, not a code bug.

- **Low — `rework_payload` serialization uses explicit field enumeration instead of `asdict()`.** Not a bug — it works correctly — but if `ReworkPayload` gains new fields in a future Gap, the serializer at lines 1047–1054 must be manually updated. Adding a `# NOTE: keep in sync with ReworkPayload dataclass` comment, or switching to `asdict(decision.rework_payload)`, would prevent future drift.

---

### Recommendation

**Merge as-is.** The core wiring is correct, all tests pass, backward compatibility is intact, and both exception and success paths are verified by live probes. The three issues are all low-severity housekeeping items — none of them constitute a correctness problem. The most actionable fix is renaming `test_real_reviewer_failure_does_not_crash_trigger` to accurately describe what it tests; this can be done in a follow-up or as a quick amendment to the PR. Optionally, add a companion test `test_pipeline_exception_propagates` to formally document the I/O-vs-core exception asymmetry policy.

---

### Re-review Checklist (if changes requested)

> Not required for this PR. Provided for reference if the team wants to close the gaps:

- [ ] Rename `test_real_reviewer_failure_does_not_crash_trigger` → `test_reviewer_exception_propagates`
- [ ] Add `test_pipeline_process_exception_propagates` to `TestTriggerNedReview`
- [ ] Add `# NOTE: keep in sync with ReworkPayload` comment at the rework_payload serializer block, or switch to `asdict(decision.rework_payload)`
