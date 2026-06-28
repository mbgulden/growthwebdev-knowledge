# Prismatic Engine Quality Gates — Comprehensive Plan

**Date:** 2026-06-27
**Author:** Fred (orchestrator)
**Trigger:** 256 tasks now dispatch-ready in autonomous mode → volume is solved, quality is not
**Status:** Phase 1 ✅ MERGED (PR #33) | Phase 2 ⏳ PLAN READY | Phase 3 ⏳ pending

**Phase 1 implementation:** See `okf/operations/phase1-quality-gates-implementation.md` for the live tracker.
**Phase 2 plan:** See `okf/operations/phase2-quality-gates-plan.md` for the active quality rollout.

---

## Executive Summary

The factory's conveyer belt now works. Volume is solved: 256 dispatch-ready tasks, autonomous mode on, ~10-15 tasks/hour projected. **But volume without quality gates is waste** — low-quality tasks eat quota, pollute Linear, flood PRs, and erode trust in the factory itself.

This document identifies **9 quality gaps** in the Prismatic Engine today, ordered by impact. Each gap has:
- **What it is** — the current behavior
- **Why it matters** — the failure mode it produces
- **The fix** — concrete implementation plan
- **Acceptance criteria** — how we know it works

The fixes are scoped to ship in **3 phases over ~2 weeks** of autonomous factory work.

---

## The 9 Quality Gaps

### Gap 1 (CRITICAL) ✅ PHASE 1 COMPLETE — "needs-human-review" label has no definition

**What it is:**
The label `agent:needs-human-review` is currently applied to tasks whose "task body doesn't follow the AGY-safe task shape". It's a parking lot, not a quality gate. ~259 tasks accumulated there.

**Why it matters:**
- Every task in this state is **dead** — can't be dispatched (factory auto-skips)
- No owner of these tasks, no SLA, no review process
- The label means "Michael should look at this", but there's no workflow behind that

**The fix:**
Two-part split of `agent:needs-human-review` into two semantic labels:

1. `task:shape-violation` — task body is not AGY-safe
   - Owner: agent:fred (you)
   - SLA: 24 hours to reshape or cancel
   - Auto-fail rule: if still in `task:shape-violation` after 24 hours → auto-cancel with comment
   
2. `output:requires-verification` — task completed but output not yet verified
   - Owner: agent:ned-review (peer review)
   - SLA: 12 hours for peer review
   - Auto-fail rule: if no peer review after 12 hours → downgrade to `output:requires-attention` and notify

**Acceptance criteria:**
- New `task:shape-violation` count: 0 within 24 hours
- New `output:requires-verification` flow has < 12-hour SLA
- Old `agent:needs-human-review` label is **archived** (cannot be used)

---

### Gap 2 (CRITICAL) ✅ PHASE 1 COMPLETE — Output verification doesn't actually verify output

**What it is:**
`agy_self_review.py` and `prismatic_self_review.py` post a "Self-Review PASSED" comment after the task runs. But the actual check is shallow — it verifies the script exited 0 and the agent didn't say "failed". It does NOT verify:
- The PR exists and links correctly
- The PR diff is meaningful (not empty / not 1000+ files drift)
- The output matches the task's stated goal
- The code runs (lint, type-check, basic import)

**Why it matters:**
Tasks get marked Done when in reality they shipped broken code, empty PRs, or unrelated drift. This is the highest-impact gap.

**The fix:**
Replace `Self-Review PASSED` with a **layered verification pipeline** that produces a `VerificationVerdict`:

```python
class VerificationVerdict:
    shape_ok: bool           # did the agent respect task shape (no test runs, no docker, no npm)
    workdir_ok: bool         # did the agent only touch the declared workdir
    files_changed_ok: bool   # did the agent touch reasonable file count (5-50)
    diff_meaningful: bool    # diff has substance (not whitespace-only, not 100% of one file)
    linked_pr_ok: bool       # if commit was made, PR exists or was opened
    basic_syntax_ok: bool    # python/json/yaml files in diff pass syntax check
    goal_match: bool         # agent's "what I did" matches the task's stated goal
```

Each layer is a separate function. All layers must pass for `Verdict = PASS`. Any failure → `Verdict = FAIL` with the specific layer that failed.

**Acceptance criteria:**
- `VerificationVerdict` is recorded in Linear as a comment on every completed task
- Tasks with `Verdict = FAIL` are transitioned to `In Progress` for retry, NOT `Done`
- 7-day audit: zero tasks marked `Done` with `Verdict = FAIL`

---

### Gap 3 (CRITICAL) ✅ PHASE 1 COMPLETE — Drift is detected late, not prevented

**What it is:**
AGY agents routinely pollute PRs with 300-400+ files of unrelated drift (we saw this on PRs #12, #13, #14 in agentic-swarm-ops). The drift only gets caught at PR-review time, **after** the work is done.

**Why it matters:**
- Polluted PRs can't be merged (too much to review)
- The valuable work is buried inside drift
- Reviewer can't tell signal from noise

**The fix:**
Add a **pre-commit drift gate** that runs inside the agent's session, BEFORE the commit:

```python
def check_drift(modified_files: list[str], declared_workdir: str) -> DriftReport:
    """Returns PASS if all modified files are within declared_workdir and total < 50."""
    out_of_workdir = [f for f in modified_files if not f.startswith(declared_workdir)]
    return DriftReport(
        out_of_workdir=out_of_workdir,
        total_files=len(modified_files),
        total_drift_lines=count_drift_lines(modified_files),
        verdict="PASS" if (not out_of_workdir and len(modified_files) < 50) else "FAIL"
    )
```

This runs as part of `agent_dispatcher.py`'s post-execution, pre-PR-open check. If drift detected → transition task to `In Progress` with comment naming the drift, do NOT open PR, do NOT mark Done.

**Acceptance criteria:**
- Drift gate runs on every task
- 0 polluted PRs opened (audit PRs over 7 days)
- Tasks with drift auto-retry once with stricter workdir pinning

---

### Gap 4 (HIGH) — PR review is fake (label-pass, not real review)

**What it is:**
29 Linear issues track 6 unique PRs. Each issue is `agent:needs-human-review` waiting for a real reviewer to actually look at the PR. But:
- There's no automated PR-reviewer skill
- PRs sit open indefinitely
- We merged 3 PRs this session on trust, not on review

**Why it matters:**
- Real review is bottleneck (only Michael can review)
- Fake "needs human review" labels accumulate
- Merged-on-trust PRs may carry bugs we don't catch

**The fix:**
Build a real **`agent:ned-review`** skill that:
1. Reads the PR diff
2. Checks for: hardcoded secrets, code quality issues, lint errors, missing tests, large drift files
3. Posts an inline review comment with verdict: APPROVE / REQUEST_CHANGES / NEEDS_DISCUSSION
4. Auto-approves PRs that pass; flags for Michael only the ones that fail or are ambiguous

This is **not** a replacement for human review — it's a **first-pass filter** so Michael only sees the PRs that genuinely need his judgment.

**Acceptance criteria:**
- `ned-review` skill exists and posts real reviews on PRs
- 80%+ of merged PRs over 14 days have a `ned-review` APPROVE comment
- Michael's PR-review queue drops from 29 issues to <5

---

### Gap 5 (HIGH) — Tasks are dispatched without smoke test

**What it is:**
AGY runs in a sandbox with `agy --sandbox` mode that restricts file paths and blocks certain commands. But there's no **smoke test** of the agent's output before it's considered complete. The agent might "succeed" by deleting the workdir or marking itself Done without doing anything.

**Why it matters:**
- Autonomous mode amplifies this — agents can complete 256 tasks in 17 hours
- Even a 10% "fake success" rate = 25 broken artifacts shipped
- Each broken artifact erodes trust in the system

**The fix:**
Add a **smoke test layer** that runs after agent completion, before the PR opens:

```python
def smoke_test(task: Task, workdir: Path) -> SmokeTestResult:
    """Verify basic invariants: file was created, repo is clean, agent's claims are true."""
    checks = [
        verify_files_were_created(task.expected_artifacts, workdir),
        verify_repo_is_committed(workdir),
        verify_agents_claim_is_true(task.agent_output_claim, task.expected_artifacts, workdir),
    ]
    return SmokeTestResult(checks=checks, verdict="PASS" if all(c.passed for c in checks) else "FAIL")
```

The third check is the killer — it verifies the agent's "I created X" claim against the filesystem. Catches lies.

**Acceptance criteria:**
- Smoke test runs on every AGY task
- Smoke test failure rate < 5% (anything higher means task shape is wrong)
- Tasks failing smoke test auto-transition to `In Progress` with named failure

---

### Gap 6 (HIGH) — No rate-limiting per task type

**What it is:**
256 dispatch-ready tasks span many types: doc audits, code refactors, tests, configuration changes. They all run at the same rate and priority. There's no quality-aware scheduling.

**Why it matters:**
- Low-quality task types can dominate quota
- High-quality work (the revenue line) competes with low-quality work for resources
- Some task types have higher failure rates and waste quota

**The fix:**
Add a **task-type quality score** that biases the dispatcher:

| Task type | Quality score | Notes |
|-----------|--------------|-------|
| doc audit / markdown edits | 0.9 | High success rate, low impact |
| bounded code refactor | 0.85 | Good ROI |
| test addition | 0.8 | High value, often correct |
| new feature implementation | 0.5 | Higher risk |
| infrastructure / config | 0.4 | Highest risk (can break prod) |
| cross-repo changes | 0.2 | Drift-prone |

The dispatcher picks from `dispatch:ready` queue with probability proportional to quality score. High-quality tasks get first dibs on quota.

**Acceptance criteria:**
- Task-type quality scoring implemented
- 7-day audit: <2% of tasks shipped are low-quality types in the wrong priority
- Quota utilization improves (fewer retries)

---

### Gap 7 (MEDIUM) — Retry logic is dumb (infinite retry)

**What it is:**
When a task fails, the dispatcher retries it once with the same prompt. If it fails again, the task is dropped. There's no exponential backoff, no shape-modification, no human escalation.

**Why it matters:**
- Some failures are deterministic (the task is impossible, needs human redesign)
- Some failures are transient (rate limits, network blips)
- Dumb retry wastes quota on impossible tasks

**The fix:**
Implement **failure classification**:

```python
class FailureMode(Enum):
    TRANSIENT = "transient"          # retry immediately, 3 attempts
    RATE_LIMIT = "rate_limit"        # exponential backoff, 5 attempts
    SHAPE_VIOLATION = "shape"        # don't retry, escalate to task:shape-violation
    LOGIC_ERROR = "logic_error"      # retry once with modified prompt, then escalate
    IMPOSSIBLE = "impossible"        # don't retry, mark output:requires-attention
```

The dispatcher classifies failures based on error patterns and applies the right retry policy.

**Acceptance criteria:**
- Failure classification implemented
- Retry waste < 5% of quota (today it's ~15%)
- Impossible tasks get escalated within 2 attempts instead of 1

---

### Gap 8 (MEDIUM) — No peer review between agents

**What it is:**
`agent:agy` does work. `agent:ned-review` reviews. But there's no **adversarial pair** — ned-review is not currently invoked automatically. Agents work in isolation.

**Why it matters:**
- Self-review is biased (the agent reviewing its own work)
- Cross-agent review catches more issues
- Two agents looking at the same output = higher confidence

**The fix:**
Add **mandatory peer review** for high-impact task types:
- All `agent:agy` tasks → peer-reviewed by `agent:ned-review`
- All `agent:fred` (me) tasks → peer-reviewed by `agent:agy`
- All `agent:kai` tasks → peer-reviewed by `agent:fred`

The reviewer runs in a separate session with read-only access to the diff. Approval is required before transition to Done.

**Acceptance criteria:**
- Peer review pipeline implemented
- 100% of high-impact tasks have peer review
- Peer-reviewed tasks have 50% fewer post-merge fixes

---

### Gap 9 (LOW) — Quota-aware task selection is missing

**What it is:**
`agy_auto_failover.py` exists and monitors quota, but the dispatcher doesn't use quota state to choose which tasks to run. Right now it just picks the next dispatch-ready task without considering whether we have enough quota to finish it.

**Why it matters:**
- Tasks started with low quota may not finish → wasted work
- Quota-aware selection can prioritize small/fast tasks when quota is low

**The fix:**
Hook the dispatcher into `agy_auto_failover.py`:
- Before dispatching a task, check current quota for the chosen model
- If quota < 50%, only dispatch tasks with expected_runtime < 5 minutes
- If quota < 20%, pause all non-critical tasks
- If quota = 0, switch to next model in failover chain

**Acceptance criteria:**
- Dispatcher reads quota before each task
- Wasted work (started but not finished) < 2%
- Quota transitions are smooth (no all-or-nothing stops)

---

## Phased Implementation

### Phase 1: Foundation (3-5 days, ~30 tasks)

**Goal:** Replace fake `needs-human-review` with real quality pipeline.

- [ ] **Gap 1**: Split `needs-human-review` into `task:shape-violation` and `output:requires-verification`. Archive old label.
- [ ] **Gap 2**: Build `VerificationVerdict` with 7 layers (shape, workdir, files, diff, pr-link, syntax, goal-match)
- [ ] **Gap 3**: Pre-commit drift gate in `agent_dispatcher.py`

### Phase 2: Active Quality (3-5 days, ~25 tasks)

**Goal:** Real review + smoke tests + failure classification.

- [ ] **Gap 4**: `agent:ned-review` PR-review skill (real first-pass review)
- [ ] **Gap 5**: Smoke test layer (verify agent claims against filesystem)
- [ ] **Gap 7**: Failure classification with retry policies
- [ ] **Gap 8**: Mandatory peer review for high-impact task types

### Phase 3: Optimization (3-5 days, ~15 tasks)

**Goal:** Quota efficiency + scheduling intelligence.

- [ ] **Gap 6**: Task-type quality scoring in dispatcher
- [ ] **Gap 9**: Quota-aware task selection
- [ ] **Audit**: 7-day quality audit, document findings

---

## Total Work Estimate

| Phase | Tasks | Duration | Quota (est.) |
|-------|-------|----------|--------------|
| Phase 1 | ~30 | 3-5 days | 60-80K tokens |
| Phase 2 | ~25 | 3-5 days | 50-70K tokens |
| Phase 3 | ~15 | 3-5 days | 30-40K tokens |
| **Total** | **~70** | **9-15 days** | **~150-190K tokens** |

That's about 70 of the 256 dispatch-ready tasks. Leaves 186 tasks for actual product work.

---

## Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Gap 2 (VerificationVerdict) too strict, breaks valid tasks | Medium | High | Ship in dry-run mode first, compare pass rates before enforcing |
| Gap 4 (ned-review) hallucinates reviews | Medium | Medium | Build conservative review skill that admits uncertainty; only auto-approves obvious passes |
| Gap 8 (peer review) doubles quota usage | High | Medium | Skip peer review for low-impact task types; gate behind task-type scoring |
| Phase 1 foundation takes longer than estimated | Medium | Low | Phase 1 unlocks Phase 2/3; ship what's ready, defer the rest |

---

## What I'm Asking You to Approve

1. **Sign off on this plan** as the spec for filling the 9 quality gaps
2. **Authorize Phase 1 implementation** (Gaps 1, 2, 3) — these are the critical foundations
3. **Set target completion**: ~3-5 days from now
4. **Allow me to file ~30 Linear tasks** to implement Phase 1

After Phase 1 ships, I'll come back with Phase 2 plan. We'll do this in waves so each phase has clear acceptance criteria before moving on.

---

## Honest Caveats

1. **This plan was written without your input.** I'm proposing the structure based on what I see. If you disagree with prioritization or have specific quality concerns, now's the time.
2. **I don't know the full extent of every gap.** These are the ones I can see. There may be more. We'll discover them as we implement.
3. **Autonomous mode runs continuously.** While we work on quality, the factory is also shipping 256 tasks. Some of those will be low-quality. That's the current state — quality work is the fix, not the cause.
4. **The token estimates are rough.** I've never run this factory at full autonomous mode for 9-15 days straight. Quota consumption could be 2-3x higher than estimated.

---

**Ready for your call:** sign off, modify, or defer.

— Fred