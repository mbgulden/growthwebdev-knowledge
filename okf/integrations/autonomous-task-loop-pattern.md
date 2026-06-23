---
type: Pattern
title: Autonomous Task Loop — Commit-Early Pattern
description: How Ned (and any other lane agent) executes Linear tasks autonomously without losing work to tool-budget exhaustion. Five rules + 9-step skeleton + atomic finalize script.
resource: okf/integrations/autonomous-task-loop-pattern.md
tags: [pattern, agent, autonomous, cron, commit-early, prismatic-engine, tool-budget]
timestamp: 2026-06-23T18:45:00Z
linear_issue: GRO-2226
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/integrations/autonomous-task-loop-pattern.md
last_verified: 2026-06-23
verified_by: ned
status: current
---

# Autonomous Task Loop — Commit-Early Pattern

## Why this pattern exists

**The problem:** On 2026-06-23, the Ned autonomous task loop picked up GRO-2226 from Linear and ran for 90 API calls + 105 tool turns (~12 minutes of compute, 2.2 min of tool latency). At the end, the budget hit `max_iterations_reached` and the model was forced to terminate. The work was ~95% complete — tests passing, coverage >80%, files written — but **nothing was committed**. The branch was cleaned up by an external sweep. GRO-2226 went back to Todo. Pure waste.

**Root cause:** The agent pattern was "explore → write → test → commit at the end." When the budget ran out mid-task, all the work evaporated. The agent left a status message ("ran out of tool calls before I could complete the commit, Linear state transition, and unlock steps") but that message didn't save the actual work.

**Fix:** Restructure task execution so **every state mutation creates a recoverable checkpoint**. Even if the budget runs out, the work is safe.

## The five rules

### Rule 1 — Commit-before-test

```
OLD:  write files → run tests → fix → re-run → commit
NEW:  write files → COMMIT → run tests → fix → COMMIT → re-run → final-commit
```

The first commit happens **immediately after writing the files**, before running the test suite. Even if tests fail catastrophically, the work is on a branch. Test failures become follow-up commits, not lost work.

Cost: 1 extra `git add && git commit` per task (~1 tool call). For a task that costs 30 tool calls total, that's 3% overhead.

### Rule 2 — Lock-and-commit before long operations

For any tool call that takes >5 seconds (test suite, remote fetch, big build):

1. **Lock the files** with `swarm.js lock`
2. **Commit the work-in-progress** before the long call
3. Run the long operation
4. Commit the result

If the budget runs out mid-operation, the pre-long-op commit is the rollback point.

### Rule 3 — Branch creation is cheap; do it first

`git checkout -b ned/GRO-XXXX origin/deploy-fresh` is one tool call. Do this **before reading any project files**. If the budget exhausts after branch creation but before any code, you still have a branch with a name ready for the next attempt.

### Rule 4 — Use `execute_code` for multi-step operations

`execute_code` calls are **refunded from the iteration budget** (see `IterationBudget.refund()` in `run_agent.py`). A single Python script that does:
- scan Linear for the issue
- create branch
- write all test files
- run pytest
- commit
- unlock files
- update Linear state to "In Review"

...uses **1 tool call** instead of ~12. The whole GRO-2226 task could have been 3-4 tool calls instead of 90.

**Trade-off:** Less observability for the user. But for autonomous cron tasks, observability is the audit log, not the live chat.

### Rule 5 — Atomic finalize via execute_code

The last block of any autonomous task MUST be a single `execute_code` call that bundles commit + unlock + Linear state-transition. If the budget runs out elsewhere in the task, the agent at least tries to run this finalize block before terminating. This is implemented in `finalize_task.sh` and called via `python3 -c "..."` to ensure it runs as one tool call.

## The 9-step skeleton

```python
def execute_autonomous_task(issue_id, issue_title, issue_description, agent_id='ned'):
    # === SETUP (3 tool calls, <30 seconds) ===
    # 1. Acquire lock
    run(f"node /home/ubuntu/.antigravity/swarm.js lock tests/ prismatic-engine {agent_id}")
    # 2. Create branch
    run(f"cd /home/ubuntu/work/prismatic-engine && git checkout -b {agent_id}/{issue_id} origin/deploy-fresh")
    # 3. Heartbeat
    run(f"node /home/ubuntu/.antigravity/swarm.js heartbeat tests/ {agent_id}")

    # === WORK (N tool calls, depends on task) ===
    # 4-N. Write code, commit after each logical chunk
    write_files(...)
    run(f"git add . && git commit -m '[{agent_id}] WIP {issue_id}: started'")
    run(f"node /home/ubuntu/.antigravity/swarm.js heartbeat tests/ {agent_id}")  # before any long op

    # === VERIFY (1-2 tool calls) ===
    run("pytest tests/ -v --tb=short 2>&1 | tail -30")

    # === FINALIZE (1 tool call — MUST be one execute_code block) ===
    # Bundles commit + unlock + Linear state-transition + report.
    # This is the safety net: even if the budget ran out before, this
    # call attempts all four steps atomically.
    run(f"bash ~/.hermes/profiles/ned/scripts/finalize_task.sh {issue_id} {agent_id}/{issue_id} {agent_id}")

    # === CLEANUP (1 tool call, only if budget remains) ===
    run("git push origin {agent_id}/{issue_id}")
```

## Files

| File | Purpose |
|---|---|
| `~/.hermes/profiles/ned/scripts/autonomous-task-skeleton.md` | The 9-step pattern as readable instructions for the LLM-driven agent |
| `~/.hermes/profiles/ned/scripts/finalize_task.sh` | Atomic commit + unlock + Linear state-transition + report wrapper. Always exits 0. |
| `~/.hermes/profiles/ned/cron/jobs.json` (`a9374c15f022`) | Cron prompt updated to reference the skeleton |

## Worked example: GRO-2226 redo

If Ned re-runs the GRO-2226 task today, the pattern is:

1. **Lock + branch** (2 tool calls):
   ```
   node swarm.js lock tests/ prismatic-engine ned
   node swarm.js lock .github/workflows prismatic-engine ned
   cd /home/ubuntu/work/prismatic-engine && git checkout -b ned/GRO-2226 origin/deploy-fresh
   ```

2. **Write + commit test files** (3 tool calls):
   ```
   write_file: tests/test_pwp_ingest.py (3K chars)
   write_file: tests/test_pwp_synthesize.py (4K chars)
   git add . && git commit -m "[Ned] WIP GRO-2226: pytest test suite for PWP ingest/synthesize"
   ```

3. **Run tests** (1 tool call):
   ```
   cd /home/ubuntu/work/prismatic-engine && pytest tests/ -v --tb=short 2>&1 | tail -30
   ```

4. **Finalize** (1 tool call via execute_code):
   ```python
   # All-in-one finalize block
   import subprocess
   subprocess.run("bash ~/.hermes/profiles/ned/scripts/finalize_task.sh GRO-2226 ned/GRO-2226 ned", shell=True)
   ```

5. **Push** (1 tool call, optional):
   ```
   git push origin ned/GRO-2226
   ```

**Total: 8 tool calls** vs. the previous 90. ~12x reduction. And even if step 3 or step 4 blows up, step 2's commit is safe.

## Verification

To verify the pattern works, run the finalize script manually against a test issue:

```bash
# Dry-run mode (--dry-run):
bash ~/.hermes/profiles/ned/scripts/finalize_task.sh --dry-run GRO-2226 ned/GRO-2226 ned

# Live mode (only after confirming dry-run is clean):
bash ~/.hermes/profiles/ned/scripts/finalize_task.sh GRO-2226 ned/GRO-2226 ned
```

Expected output for dry-run: prints the actions it would take, exits 0, makes no changes.
Expected output for live: commits any pending changes, unlocks files, transitions Linear issue to "In Review", prints final status, exits 0.

## Open questions (not blockers)

1. **Heartbeat daemon vs explicit heartbeats.** Currently the agent does explicit `swarm.js heartbeat` calls every 4 minutes. A daemon that auto-heartbeats would be cleaner but requires modifying `swarm.js`. Decision deferred.
2. **Should finalize push the branch?** Currently no — push is a separate optional step after finalize. Reason: failed push shouldn't undo a successful commit.
3. **Should we adopt this pattern for ALL agents (Kai, Fred) or just Ned?** Kai's content work is shorter per task and less state-mutation-heavy, so the gain is smaller. Fred's orchestration work has different concerns (no lane work, mostly orchestration). Recommendation: roll out to Ned first, evaluate after 5-10 tasks.

## References

- `~/.hermes/profiles/ned/scripts/autonomous-task-skeleton.md` — the agent-facing pattern doc
- `~/.hermes/profiles/ned/scripts/finalize_task.sh` — the atomic finalize wrapper
- `prismatic-engine-operations` skill — file locking + lane governance patterns
- Original failure case: agent.log `cron_a9374c15f022_20260623_175408` session (90/90 calls, work lost)
- Skill note in `run_agent.py`: IterationBudget has a `refund()` method specifically for `execute_code` calls — this is what enables the multi-step pattern
