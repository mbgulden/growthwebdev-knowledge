---
type: Standard
title: Subagent checkpoint monitor spec
description: Specification for subagent checkpoint monitoring and loss-prevention in multi-agent work. Repaired from old-format PR #12 standard.
resource: okf/standards/subagent-checkpoint-monitor-spec.md
tags: [standard, subagent, checkpoint, monitoring, swarm]
timestamp: 2026-07-18T00:00:00Z
linear_issue: null
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/standards/subagent-checkpoint-monitor-spec.md
last_verified: 2026-07-18
verified_by: fred
status: current
---

# Subagent Commit Checkpoint Monitor

**File:** `~/.hermes/profiles/orchestrator/scripts/subagent_checkpoint_monitor.py`
**Status:** v1 shipped 2026-06-29
**Trigger:** Gap 10 subagent lost 50KB of code when its 50-tool-call budget hit
before it could commit anything. This script prevents that class of loss.

## What It Does

A wrapper around any git-based subagent (AGY, delegated subagent, manual run) that
enforces commit cadence:

| Trigger | Action |
|---|---|
| Modified files >= N (default 5) | WIP commit |
| Last commit older than N seconds (default 600) AND dirty | WIP commit |
| Tool-call budget >= 75% AND dirty | WIP commit (force before exhaustion) |

WIP commits use `[WIP-auto-checkpoint] <timestamp> <reason>` message format
so they're easy to filter and squash before merge.

## Usage

**One-shot check (before declaring "DONE"):**

```bash
python3 subagent_checkpoint_monitor.py \
    --workspace /home/ubuntu/work/prismatic-engine \
    --max-tool-calls 50 \
    --current-tool-call 47
# Exit 0 = clean
# Exit 1 = WIP committed
# Exit 2 = dirty + exhausted budget (LOSING WORK — investigate)
```

**Daemon mode (running alongside an agent):**

```bash
python3 subagent_checkpoint_monitor.py \
    --workspace /home/ubuntu/work/prismatic-engine \
    --daemon --interval 60 \
    --commit-every 5
```

**Integration with `delegate_task` and `launch_agy_with_artifact.py`:**

Both launchers should call this script:
1. Before declaring the subagent "DONE" → exit 0 means work is preserved
2. On every 10th tool call → quick check, no overhead
3. When budget crosses 50% → switch to daemon mode for the remaining budget

## Exit Codes

| Code | Meaning | Action |
|---|---|---|
| 0 | Clean worktree | OK to declare DONE |
| 1 | WIP auto-committed | OK to declare DONE (work preserved) |
| 2 | Dirty + budget exhausted | DO NOT declare DONE — investigate |
| 3 | Invalid args / not a git repo | Fix config, retry |

## Test It

```bash
cd /tmp && rm -rf test-repo && mkdir test-repo && cd test-repo
git init -q
echo "x" > a.txt
python3 subagent_checkpoint_monitor.py --workspace . --commit-every 3 --max-tool-age-sec 999
# Should report 1 modified file, no WIP needed
```

## Related

- `okf/standards/subagent-task-framing.md` — prompt template that includes
  "commit every 2-3 files" as a requirement
- `~/.hermes/profiles/orchestrator/skills/subagent-task-framing/` — same content as skill
