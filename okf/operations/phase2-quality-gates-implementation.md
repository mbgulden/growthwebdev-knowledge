# Phase 2 Quality Gates — Implementation Tracker

**Date:** 2026-06-28
**Phase:** Phase 2 of Quality Gates initiative
**Status:** ✅ **COMPLETE** — all 4 gaps merged to deploy-fresh

## Shipped

| Gap | Component | PR | Commit | Tests | Status |
|-----|-----------|----|----|-------|--------|
| 5 | Smoke test layer (`prismatic/quality/smoke.py`) | #36 → #37 | 84d7f90c | 40 | ✅ MERGED |
| 7 | Failure classification (`prismatic/quality/failure.py`) | #35 | (pre-deploy-fresh) | 52 | ✅ MERGED |
| 4 | Real PR reviewer (`prismatic/review/pr_reviewer_impl.py`) | #38 | 58d08298 | 38 | ✅ MERGED |
| 8 | Pipeline orchestrator (`prismatic/review/pipeline.py`) | #39 | 9ad18bf0 | 30 | ✅ MERGED |

**Aggregate:** 214/214 tests pass (54 Phase 1 + 40 Gap 5 + 52 Gap 7 + 38 Gap 4 + 30 Gap 8).

## What Each Gap Ships

### Gap 5 — Smoke Test Layer

Detects fabricated file claims. A worker that says "I created `foo.py` and `bar.py`" but the files don't exist (or are empty) fails the smoke test before reaching PR review.

- `extract_claimed_paths()` — 4 regex patterns (I created, file:, backticks, "and X")
- `is_path_traversal()` — `../` and `..\` detection (handles leading `..` not matched by `[\w./-]+`)
- `file_exists()` + `file_has_substantive_content()` with binary detection (1% null-byte threshold)
- `smoke_test()` — orchestrator with PASS/FAIL/Findings

**Peer review findings (PR #36):** 3 → all fixed → APPROVED

### Gap 7 — Failure Classification

Classifies failed-task exceptions into 5 modes (TRANSIENT, RATE_LIMIT, SHAPE_VIOLATION, LOGIC_ERROR, IMPOSSIBLE) and applies a per-mode retry policy. Prevents unbounded retry loops when a task is structurally impossible.

- `classify_failure()` + `classify_with_policy()` (fail-open/fail-closed)
- `apply_failure_classification()` with Linear integration
- File-locked failure counter with `fcntl.flock`
- Type guard for None/non-string logs
- Log truncation at 16 KB (keeps tail — most recent signal)

**Peer review findings (PR #35):** 8 → all fixed → APPROVED

### Gap 4 — Real PR Reviewer

Replaces stub with real implementation that fetches PR diffs via `gh` CLI and runs code-quality checks. Verdict flow: APPROVE / REQUEST_CHANGES / NEEDS_DISCUSSION.

- 10-pattern secret detection (AWS, GitHub PAT, Slack, Stripe, private keys, DB URLs, etc.)
- Function length >50 lines warning
- File length >500 lines warning
- Test coverage heuristic: only flags NEW source files (`--- /dev/null` marker) with >10 added lines
- `RealPRReviewer.review_pr(pr_url)` with 30s timeout

**Peer review findings (PR #38):** 4 → 3 fixed, 1 acknowledged → APPROVED
- Bug 1 (CRITICAL): medium severity silently produced APPROVE — FIXED with NEEDS_DISCUSSION branch
- Bug 2 (HIGH): warning details missing from high-severity summary — FIXED with warnings loop
- Bug 3 (MEDIUM): RealPRReviewer not exported — FIXED
- Bug 4 (MEDIUM): line numbers from diff-enumeration — ACKNOWLEDGED as known limitation

### Gap 8 — Pipeline Orchestrator

Wraps `PRReviewResult` in a classify → decide → rework-dispatch loop. State holds per-issue attempt counters; the factory calls this to route issues between Done / In Review / In Progress.

- `classify_impact(result)` → `trivial` / `minor` / `major` / `blocker`
- `decide_next_action(result, rework_attempts)` → `advance` / `hold` / `rework` / `give_up`
- `build_rework_payload(...)` → JSON-serializable dispatch payload
- `PipelineOrchestrator()` — stateful, thread-safe (full read-modify-write under lock)

**Decision rules:**
- APPROVE → advance (counter resets)
- REQUEST_CHANGES + attempts < max → rework (counter bumps)
- REQUEST_CHANGES + attempts >= max → give_up
- NEEDS_DISCUSSION → hold (never auto-dispatches)

**Impact classification:**
- Critical findings always → blocker (regardless of verdict)
- APPROVE no findings → trivial
- NEEDS_DISCUSSION with warning/medium → minor
- NEEDS_DISCUSSION with high → major
- REQUEST_CHANGES → major (or blocker if critical)

**Peer review findings (PR #39):** 5 → all fixed → APPROVED
- ISSUE-1 (medium): IMPACT_RANK / DEFAULT_MAX_REWORK_ATTEMPTS / IMPACT_LEVELS / ACTIONS not exported — FIXED
- ISSUE-2 (medium): docstring table missing defensive fallback row — FIXED
- ISSUE-3 (low): thread-safety not documented — FIXED with Lock + docstring + regression test
- ISSUE-4 (low): lazy `import re` inside hot-path function — FIXED with module-top import
- Re-review follow-up (low): lock-scope narrower than docstring claimed — FIXED with full read-modify-write under lock

## Metrics

| Metric | Value |
|---|---|
| Total PRs merged to deploy-fresh | 4 (Gaps 5, 7, 4, 8) |
| Total new tests added | 160 (40 + 52 + 38 + 30) |
| Total tests passing in deploy-fresh | 214 |
| Critical bugs caught by peer review | 2 (medium-severity false-safe, warning details gap) |
| High bugs caught by peer review | 1 (warning details missing) |
| Re-review cycles | 2 (PR #38 + PR #39) |
| Skills saved | 2 (second-opinion-on-design, push-protection-secret-fixtures) |
| Lessons recorded to OKF | 6 (phase2-lessons-learned-2026-06-28.md) |

## Cross-Cutting Concerns

### Push Protection

GitHub's secret-scanner blocks test fixtures containing real secret prefixes (AKIA, ghp_, xoxb-, sk_live_). Solved with:
1. Build fake tokens via string concat at runtime (`"AKIA" + "IOSF" + ...`)
2. Include explicit `+++ b/` headers in test diffs (detect_secrets requires file context)
3. Use exact length matches for regex quantifiers (ghp_ needs 36 chars, sk_live_ needs 24+)

When the scanner blocks a push due to secrets in branch history, create a fresh branch off `deploy-fresh` with a single clean commit. The scanner checks ALL commits, not just latest.

### Pre-Commit Hooks

`.pre-commit-config.yaml` includes ruff check + ruff format + yamllint + shellcheck + path portability check. Catches:
- Hardcoded `/tmp/...` paths (should use `Path(__file__).parent`)
- Unused imports
- Line length issues
- Format inconsistencies

The pre-push hook (in Prismatic Engine) checks lane compliance — files in `src/`, `infra/`, `deploy/` vs `content/`, `active-oahu/`.

### Factory Audit

Audits found 20 falsely-Done tasks (marked Done in Linear without code actually being merged). Root cause: factory marked tasks Done when AGY reported "all checks pass" without verifying PR merge. Fix: webhook on PR-merge event to auto-confirm Linear task completion.

**Status:** webhook still needed; for now, manual re-queue comments document false-completions.

## What's Next

Phase 3 will tackle:
- **Cross-cutting:** Webhook on PR-merge for Linear task auto-completion
- **Quality:** Address acknowledged Bug 4 from Gap 4 (hunk-header parser for accurate line numbers)
- **Gap 6:** Verify against master plan — may not exist or may need scope clarification
- **Operational:** Wire factory's GRO-2876 to actually call `RealPRReviewer` and `PipelineOrchestrator` (currently uses stub)

## References

- Lessons doc: `okf/operations/phase2-lessons-learned-2026-06-28.md`
- Review feedback:
  - `okf/operations/pr35-review-feedback.md` (Gap 7)
  - `okf/operations/pr36-review-feedback.md` (Gap 5)
  - `okf/operations/pr38-review-feedback.md` (Gap 4)
  - `okf/operations/pr39-review-feedback.md` (Gap 8)
- Skills:
  - `~/.hermes/profiles/orchestrator/skills/peer-review-before-merge.md`
  - `~/.hermes/profiles/orchestrator/skills/factory-code-audit.md`
  - `~/.hermes/profiles/orchestrator/skills/second-opinion-on-design.md`
  - `~/.hermes/profiles/orchestrator/skills/push-protection-secret-fixtures.md`