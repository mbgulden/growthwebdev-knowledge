# Phase 2 Quality Gates — Implementation Plan

**Date:** 2026-06-28
**Author:** Fred (orchestrator)
**Phase 1 reference:** `okf/operations/phase1-quality-gates-implementation.md` (MERGED via PR #33)
**Plan reference:** `okf/operations/prismatic-quality-gates-comprehensive-plan.md`

---

## Phase 2 Goal

Build the **active quality** layer on top of Phase 1's foundation:
- Real PR review (not label-pass) — Gap 4
- Smoke tests that catch agent lies — Gap 5
- Smart retry with failure classification — Gap 7
- Mandatory peer review for high-impact tasks — Gap 8

**Target completion:** 3-5 days
**Total work:** ~25 Linear tasks, ~50-70K tokens estimated

---

## Gap 4: `agent:ned-review` PR Review Skill

### The problem

29 PR-review issues track 6 unique PRs. Each is labeled `agent:needs-human-review` and waits indefinitely for a real reviewer. There's no automated first-pass filter, so Michael's PR-review queue is the bottleneck.

### What to build

**`prismatic/review/pr_reviewer.py`** — automated PR reviewer that:

1. Reads PR diff via GitHub API
2. Runs structured checks:
   - **Hardcoded secrets** (regex: AWS keys, private keys, API tokens)
   - **Code quality** (cyclomatic complexity, function length, file length)
   - **Lint errors** (ruff / eslint depending on file type)
   - **Test coverage** (does the PR add tests for new code?)
   - **Drift files** (>50 file changes trigger re-check)
3. Posts inline review comments on the PR via GitHub API
4. Returns verdict: `APPROVE` / `REQUEST_CHANGES` / `NEEDS_DISCUSSION`
5. Auto-approves clean PRs; flags ambiguous ones for Michael

### Acceptance criteria

- Skill exists at `prismatic/review/pr_reviewer.py` with comprehensive unit tests
- 80%+ of merged PRs over 14 days have a `ned-review` APPROVE comment
- Michael's PR-review queue drops from 29 → <5
- Reviews complete within 60 seconds of PR open

### Tasks (est. ~8)

1. Build `pr_reviewer.py` with diff-fetching + secret-detection
2. Add code-quality metrics (complexity, length)
3. Add lint integration (ruff for Python, basic JSON/YAML validation)
4. Add test-coverage heuristic (does the diff touch `tests/` or `*_test.py`?)
5. Wire GitHub API for inline comments + verdicts
6. Add `agent:ned-review` label trigger in `quality_gate.py`
7. Write 30+ unit tests for the reviewer
8. End-to-end test: open a clean PR, verify auto-approve

---

## Gap 5: Smoke Test Layer

### The problem

Today, agents can "complete" a task by doing nothing — marking themselves Done without producing artifacts. There's no verification that the agent's claimed output actually exists.

### What to build

**Extend `prismatic/quality/gates.py` with `smoke_test()`** that:

1. Parses the agent's "what I did" narrative from their log
2. Extracts claimed file paths and artifact names
3. Verifies each path exists on disk
4. Verifies each artifact has substantive content (not empty / not whitespace)
5. Verifies the agent's commit/PR claims match reality

### Acceptance criteria

- `smoke_test()` runs on every task after `VerificationVerdict`
- Smoke test failure rate < 5% (anything higher means task shape is wrong)
- Tasks failing smoke test auto-transition to `In Progress` with named failure

### Tasks (est. ~5)

1. Build `smoke_test()` function with claim parsing
2. Add filesystem verification (file exists, non-empty)
3. Add claim-extraction heuristic
4. Wire into `quality_gate.py` post-execution hook
5. Write 15+ tests covering lying agents, empty output, partial claims

---

## Gap 7: Failure Classification

### The problem

When a task fails, the dispatcher retries it once with the same prompt. If it fails again, the task is dropped. There's no classification of *why* it failed, so impossible tasks get retried indefinitely (wasting quota).

### What to build

**`prismatic/quality/failure.py`** — failure classifier with retry policies:

```python
class FailureMode(Enum):
    TRANSIENT = "transient"          # retry immediately, 3 attempts
    RATE_LIMIT = "rate_limit"        # exponential backoff, 5 attempts
    SHAPE_VIOLATION = "shape"        # don't retry, escalate
    LOGIC_ERROR = "logic_error"      # retry once with modified prompt, then escalate
    IMPOSSIBLE = "impossible"        # don't retry, mark output:requires-attention
```

Each classification maps to a retry policy. The classifier uses error patterns (like the existing `ERROR_PATTERNS` in `agent_output_validator.py`).

### Acceptance criteria

- Failure classification implemented
- Retry waste < 5% of quota (today ~15%)
- Impossible tasks get escalated within 2 attempts instead of 1

### Tasks (est. ~6)

1. Build `FailureMode` enum + `classify_failure()` function
2. Add retry policy mapping (mode → max attempts, backoff)
3. Integrate with `agent_dispatcher.py` retry loop
4. Add failure counter (track failures per task)
5. Add `output:requires-attention` escalation label
6. Write 20+ tests covering each failure mode

---

## Gap 8: Mandatory Peer Review for High-Impact Tasks

### The problem

Agents work in isolation. `agent:agy` does work, `agent:fred` reviews, but ned-review isn't automatically invoked. Self-review is biased; cross-agent review catches more issues.

### What to build

**Peer review pipeline** in `prismatic/review/peer_pipeline.py` that:

1. Identifies "high-impact" task types: cross-repo changes, infra changes, new features, anything tagged `priority:high`
2. After a task completes, automatically launches a peer review session
3. The reviewer (different agent class) runs in read-only mode
4. Reviewer's verdict gates the transition to Done
5. Approval is required; rejection triggers rework loop

### Acceptance criteria

- Peer review pipeline implemented
- 100% of high-impact tasks have peer review
- Peer-reviewed tasks have 50% fewer post-merge fixes (measured over 30 days)

### Tasks (est. ~6)

1. Define "high-impact" task classification
2. Build peer review orchestrator (read-only session, different agent)
3. Wire into `agent_dispatcher.py` post-completion flow
4. Add review verdict → Linear state transition logic
5. Build rework loop (rejection → back to worker)
6. Write 15+ integration tests

---

## Total Phase 2 Work

| Gap | Tasks | Est. tokens |
|---|---|---|
| Gap 4 — ned-review skill | ~8 | ~20K |
| Gap 5 — smoke test | ~5 | ~10K |
| Gap 7 — failure classification | ~6 | ~15K |
| Gap 8 — peer review pipeline | ~6 | ~20K |
| **Total** | **~25** | **~65K** |

---

## Phasing Within Phase 2

**Sprint 1 (Day 1-2):** Gap 7 (failure classification) — smallest, biggest quota-savings impact
**Sprint 2 (Day 2-4):** Gap 5 (smoke tests) + Gap 4 (ned-review) in parallel
**Sprint 3 (Day 4-5):** Gap 8 (peer review pipeline) — depends on Gap 4 being done

---

## Risks

1. **Gap 4 hallucinated reviews** — review skill could miss subtle issues. Mitigation: conservative threshold, only auto-approve obvious passes.
2. **Gap 5 false positives** — smoke test could reject legitimate output. Mitigation: tune heuristic against real task outputs first.
3. **Gap 8 doubles quota usage** — peer review runs every high-impact task. Mitigation: skip peer review for low-impact types, gate behind quality scoring (Gap 6 in Phase 3).
4. **Phase 1 bugs surface** — Phase 2 may expose issues in the `VerificationVerdict`. Mitigation: fast iteration loop.

---

## Next Action

After your sign-off, I'll file ~25 Linear tasks for Phase 2 and queue them for the autonomous factory. The `agent:agy-sonnet` review process from Phase 1 will carry forward — every gap gets a peer review before merge.

---

**Ready for sign-off.** Phase 1 is shipped (PR #33 merged). Phase 2 takes us from "foundation" to "active quality" with real PR review, smoke tests, smart retry, and peer review.