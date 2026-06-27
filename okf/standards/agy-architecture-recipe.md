---
type: Standard
title: AGY Architecture — The Recipe (regression-tested 2026-06-23)
description: The complete, tested, working architecture for AGY. Every component, every path, every contract. The "magic sauce" that makes AGY work — captured so we stop breaking it. This is the canonical reference: if you're about to change anything AGY-related, read this first.
resource: okf/standards/agy-architecture-recipe.md
tags: [standard, agy, architecture, recipe, recipe, regression-test, sandbox, supervisor, dispatcher, mvp, magic-sauce]
timestamp: 2026-06-23T17:00:00Z
linear_issue: GRO-2237
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/standards/agy-architecture-recipe.md
last_verified: 2026-06-23
verified_by: fred
status: current
---

# AGY Architecture — The Recipe (regression-tested 2026-06-23)

> **STOP.** If you are about to change anything AGY-related, READ THIS FIRST.
> Every regression we've ever had came from changing AGY components without
> understanding the full system. This doc is the contract.

> **North Star reminder.** Every component in this recipe exists to support
> the [Prismatic North Star](../vision/prismatic-north-star.md). AGY is
> Horizon 1 of a five-horizon journey (Coding → Business → Creative →
> Knowledge → Dream). If a change here strengthens the overnight factory,
> ships in. If it weakens it, it does not. See the six permanent principles
> in the North Star — they are binding on every architectural decision.

## TL;DR

```
                       ┌──────────────────────┐
                       │  Linear (source of    │
                       │  truth for tasks)     │
                       └──────────┬───────────┘
                                  │ polls
                       ┌──────────▼───────────┐
                       │  Dispatchers         │  (Ned, Kai, Jules, etc.)
                       │  (write to           │  Cron: every 5-15 min
                       │   /tmp/issue-        │  Run via no_agent
                       │   batches/)          │
                       └──────────┬───────────┘
                                  │ writes
                       ┌──────────▼───────────┐
                       │  /tmp/issue-batches/ │  ← THE QUEUE
                       │  {iid}.txt per task  │
                       └──────────┬───────────┘
                                  │ polls
                       ┌──────────▼───────────┐
                       │  AGY Sandbox         │  Cron: every 5 min
                       │  Supervisor          │  Long-lived process
                       │  (faf8d91da716)      │
                       │  • reads queue       │
                       │  • spawns workers    │
                       │  • heartbeat/mtime   │
                       │  • RESULT.md check   │
                       └──────────┬───────────┘
                                  │ spawns N workers in parallel
              ┌───────────────────┼───────────────────┐
              ▼                   ▼                   ▼
        ┌──────────┐        ┌──────────┐        ┌──────────┐
        │ Worker 1 │        │ Worker 2 │        │ Worker 3 │
        │ agy-bin  │        │ agy-bin  │        │ agy-bin  │
        │ sandbox  │        │ sandbox  │        │ sandbox  │
        │ GRO-X    │        │ GRO-Y    │        │ GRO-Z    │
        └────┬─────┘        └────┬─────┘        └────┬─────┘
             │                   │                   │
             └───────────────────┴───────────────────┘
                                  │
                                  ▼
                          ┌──────────────┐
                          │  RESULT.md   │  ← the "done" contract
                          │  in sandbox  │
                          └──────┬───────┘
                                  │
                                  ▼
                          ┌──────────────┐
                          │  Mark Linear │  ← "Done" state
                          │  issue Done  │
                          └──────────────┘
```

## The Recipe — verified working 2026-06-23

### Component 1: Linear (source of truth)

- Every issue has labels: `agent:fred`, `agent:ned`, `agent:ned-infra`, `agent:ned-code`, `agent:kai`, `agent:kai-content`, `agent:kai-css`, `agent:kai-js`, `agent:agy`, `agent:agy-pro`, etc.
- State: `Todo` → `In Progress` → `Done`
- Description: full task spec (what to do, why, how to verify)

**DO NOT** add tasks via the API without a label. The supervisor filters by label.

### Component 2: Dispatchers (queue producers)

**Location:** `~/.hermes/profiles/orchestrator/scripts/{ned,kai,jules}_delta_dispatcher.py`

**Cron IDs:**
- Ned: `48876764f897` (every ~15 min)
- Kai: `5fe7de2a1d9a` (every ~15 min)
- Jules: `b7996de54e7e` (watchdog)

**Pattern (the right one, 2026-06-23 fix):**
```python
def invoke_agy(issues: list) -> bool:
    """Write task specs to /tmp/issue-batches/ for the AGY supervisor to pick up."""
    batches_dir = Path("/tmp/issue-batches")
    batches_dir.mkdir(parents=True, exist_ok=True)
    for i in issues:
        iid = i["identifier"]
        task_content = f"""WORKDIR: prismatic

WORK ON {iid}: {i['title']}

=== ISSUE DESCRIPTION ===

{i.get('description', '') or ''}

=== EXECUTION CONTRACT ===

1. Make a feature branch off main: `git checkout -b feature/{iid.lower()}`
2. Do the work in that branch
3. Run any tests/builds
4. Commit: `[AGENT] {title} (#{iid})`
5. Push and open a PR
6. Write RESULT.md in the sandbox per the MANDATORY FINISH PROTOCOL
7. Mark the Linear issue Done
"""
        task_path = batches_dir / f"{iid}.txt"
        task_path.write_text(task_content, encoding="utf-8")
    return True
```

**DO NOT:**
- ❌ Invoke `agy` as a single subprocess with a 5-min timeout (guaranteed to fail for 20+ issues)
- ❌ Use `--print-timeout` less than 1h (AGY needs time to think)
- ❌ Use a model name that doesn't exist (e.g. "Claude Sonnet 4.6 (Thinking)" — silently falls back to gemini-3.5-flash-medium)

**DO:**
- ✅ Use `Gemini 3.5 Flash (High)` (or similar real AGY model)
- ✅ Pass `--add-dir` for the workspace
- ✅ Use `Gemini 3.1 Pro (High)` for synthesis tasks (longer context)

### Component 3: The Queue (`/tmp/issue-batches/`)

**This is the contract between dispatchers and the supervisor.** Both must agree on:
- File location: `/tmp/issue-batches/{iid}.txt`
- File format: `WORKDIR: <dir>` on line 1, then task content
- Worker dir lookup: looks for `WORKDIR: prismatic` → resolves to `/home/ubuntu/work/prismatic-engine`

**File is auto-cleaned** by the supervisor after the task is consumed.

### Component 4: AGY Sandbox Supervisor (queue consumer)

**Location:** `~/.hermes/profiles/orchestrator/scripts/agy_sandbox_event_supervisor.py`
**Cron:** `faf8d91da716` (every 5 min, long-lived)

**The supervisor:**
1. Polls Linear every 90s for `agent:agy*` issues in Todo/Backlog
2. Reads `/tmp/issue-batches/{iid}.txt` for each task (or falls back to default spec)
3. Creates a sandbox at `/tmp/agy_sandboxes/{iid}/` (cloned from the workdir)
4. Spawns a worker thread that runs `agy-bin` with the MANDATORY FINISH PROTOCOL prompt
5. Heartbeat every 60s: checks sandbox file mtime (not transcript — that doesn't grow in --print mode)
6. RESULT.md post-condition: if AGY says DONE but no RESULT.md, downgrade to MissingResult
7. Marks Linear Done when RESULT.md is present + worker exited 0

**The MANDATORY FINISH PROTOCOL (in the prompt to AGY):**
```
**MANDATORY FINISH PROTOCOL:**
1. Before saying 'DONE', you MUST write a complete summary to `/tmp/agy_sandboxes/{iid}/RESULT.md`
   (use the Write tool — do NOT just print to stdout).
2. The RESULT.md must include: what you did, files changed, test results (if any),
   commit hashes, and any follow-ups.
3. Only AFTER the Write tool confirms RESULT.md was saved, output
   `DONE: {iid} <one-line summary>` as the LAST line.
4. If you cannot save RESULT.md (e.g. permission error), output
   `ERROR: {iid} <reason>` instead — do NOT say DONE without the file.
```

### Component 5: Workers (individual task executors)

**Location:** spawned in the supervisor's worker pool
**Process:** `agy-bin --dangerously-skip-permissions --print ...`

**Key flags (don't change these without testing):**
- `--dangerously-skip-permissions` — required for autonomous operation
- `--print` — output mode (vs interactive)
- `--print-timeout 24h0m0s` — give AGY time to think
- `--sandbox` — sandbox AGY's operations
- `--add-dir /tmp/agy_sandboxes/{iid}` — sandbox directory
- `--model gemini-3.5-flash-high` — model name (display name doesn't matter, real model is always the same)

## The "magic sauce" — what makes it work

1. **Separation of concerns** — dispatcher queues, supervisor consumes, workers execute. Nobody tries to do all three.

2. **Event-driven scaling** — workers pick up tasks from a `Queue` and replace themselves. New tasks are immediately picked up by any idle worker.

3. **mtime-based heartbeat** — file system is the heartbeat. Sandbox file mtime tells you if work is happening. (Transcript.jsonl doesn't grow in --print mode, so checking transcript is wrong.)

4. **RESULT.md post-condition** — AGY can't "cheat" by saying DONE without writing the file. The post-condition check downgrades false positives to MissingResult.

5. **Dynamic timeout** — workers get 1h cap with roof-raise if they're making progress. Real AGY work takes 5-30 min, not 5 min. The 5-min hard cap was the regression.

## Regression log — every AGY breakage ever

| Date | What broke | Why | Fix | How to detect |
|---|---|---|---|---|
| 2026-06-22 | supervisor returning HTTP 400 | `orderBy: priority` invalid enum | `orderBy: createdAt` (commit f930288) | Linear HTTP 400 in supervisor log |
| 2026-06-23 (AM) | agents returning [SILENT] | dispatchers using `state.type: ["todo", "inProgress"]` (wrong enum) | `["unstarted", "started", "backlog"]` (commits 28c4ae5, 3fdfa57) | dispatcher log shows "[SILENT]" with no work found |
| 2026-06-23 (AM) | AGY model name silent fallback | "Claude Sonnet 4.6 (Thinking)" doesn't exist, silently falls back | Use real model name "Gemini 3.5 Flash (High)" | workers exit 0 but produce nothing |
| 2026-06-23 (AM) | 5-min timeout killing real work | subprocess.run(timeout=300) in dispatchers | Removed — dispatchers now write to /tmp/issue-batches/ | dispatcher log shows "AGY timed out after 5 min" |
| 2026-06-23 (AM) | 23 issues stuck In Progress | workers died but Linear was never reset | Reset to Todo + write to issue-batches/ | Linear shows 20+ In Progress with no recent activity |
| 2026-06-23 (PM) | workers' transcript.jsonl not growing | --print mode doesn't write to transcript | Switch heartbeat to file mtime | supervisor "5 min stagnation" warning with 0 transcript growth |
| 2026-06-23 (PM) | AGY says DONE without writing RESULT.md | no post-condition check | Add post-condition, downgrade to MissingResult | DONE without RESULT.md → log + retry |

**The pattern:** every regression was a **re-implementation of something that was already working** in a different layer.

## Recipe for adding a new agent lane

1. **Create the dispatcher script** at `~/.hermes/profiles/orchestrator/scripts/{newagent}_delta_dispatcher.py`
2. **Use the standard pattern** (copy from `ned_delta_dispatcher.py`)
3. **Register the cron** in `~/.hermes/profiles/orchestrator/cron/jobs.json` with a 5-15 min schedule
4. **Use the AGY labels** that the supervisor already watches (don't add new label types without updating the supervisor config)
5. **Test the dispatcher** with `python3 {newagent}_delta_dispatcher.py` and verify it writes to `/tmp/issue-batches/`
6. **Verify the supervisor picks up** the tasks on its next 90s poll

## Recipe for fixing AGY when it breaks

**Step 1: Diagnose.** Check the supervisor log:
```bash
tail -100 ~/.hermes/profiles/orchestrator/cron/output/faf8d91da716/$(ls -t ~/.hermes/profiles/orchestrator/cron/output/faf8d91da716/ | head -1)
```
Look for: HTTP 400? Timeout? "fetched 0 issues"? "stagnation warning"?

**Step 2: Check the worker.** Is the worker process running?
```bash
ps -ef | grep "agy-bin" | grep -v grep
```
No workers = supervisor is broken. Some workers = workers might be hung.

**Step 3: Check the queue.** Are there task specs in `/tmp/issue-batches/`?
```bash
ls /tmp/issue-batches/
```
Empty queue = dispatchers aren't writing. Full queue = dispatchers are writing but supervisor isn't consuming.

**Step 4: Match the symptom to the regression log above.**

**Step 5: Apply the fix. NEVER re-implement — find the existing component that's broken and patch it.**

## Regression test suite (run before any AGY change)

```bash
# 1. Dispatcher writes to queue
python3 ~/.hermes/profiles/orchestrator/scripts/ned_delta_dispatcher.py
# → expect: "[NED-DISPATCH] Wrote N task specs to /tmp/issue-batches"

# 2. Supervisor picks up within 90s
# (start supervisor if not running)
bash ~/.hermes/profiles/orchestrator/scripts/agy_sandbox_event_supervisor_cron.sh
# → expect: "[watchdog] polling Linear every 90s" then "[queue] + GRO-XXX" within 90s

# 3. Worker spawns within 10s of queue add
# → expect: "[worker-N] picked up GRO-XXX" then "[GRO-XXX] launching AGY in sandbox GRO-XXX"

# 4. Heartbeat signals fire
# → expect: "[GRO-XXX] 🟢 2-min signal: healthy — sandbox activity recent"

# 5. RESULT.md is written before DONE
# → expect: /tmp/agy_sandboxes/GRO-XXX/RESULT.md exists with content

# 6. Linear marked Done
# → expect: GRO-XXX state = "Done" with comment from supervisor

# 7. Sandbox auto-cleaned
# → expect: /tmp/agy_sandboxes/GRO-XXX/ removed after task done
```

If any of these fail, **stop and read this doc again** before changing anything.

## Change log

- 2026-06-23 17:00 UTC: Initial doc. AGY architecture regression-tested + documented. The recipe is captured.
