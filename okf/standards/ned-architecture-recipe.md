---
type: Standard
title: Ned Architecture — The Recipe (regression-tested 2026-06-23)
description: The complete, tested, working architecture for the Ned agent. Lane governance, dispatcher pattern, what Ned owns vs. what AGY owns, when to add new issues, when to file follow-ups.
resource: okf/standards/ned-architecture-recipe.md
tags: [standard, ned, architecture, recipe, regression-test, dispatcher, lane-governance, infra]
timestamp: 2026-06-23T17:00:00Z
linear_issue: GRO-2238
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/standards/ned-architecture-recipe.md
last_verified: 2026-06-23
verified_by: fred
status: current
---

# Ned Architecture — The Recipe (regression-tested 2026-06-23)

> **STOP.** If you are about to change anything Ned-related, READ THIS FIRST.

> **North Star reminder.** Ned owns the infra and governance lane. Every
> dispatcher Ned touches exists to support the [Prismatic North Star](../vision/prismatic-north-star.md).
> The five horizons (Coding → Business → Creative → Knowledge → Dream) all
> need infra that runs without Michael. Permanent principles #1 ("engine
> must run without you") and #4 ("governance is not optional") are binding
> on every Ned decision.

## TL;DR

Ned handles **infrastructure + code execution** tasks. Three labels: `agent:ned`, `agent:ned-infra`, `agent:ned-code`. One dispatcher, one supervisor, one pattern.

## What Ned owns

| Label | Scope |
|---|---|
| `agent:ned` | General infra tasks, code review, automation workflows, deployment |
| `agent:ned-infra` | Pure infrastructure: DNS, Cloudflare config, CF Pages deploys, environment setup |
| `agent:ned-code` | Code-level work: refactors, bug fixes, scripts, integrations |

## What Ned does NOT own

- Content writing (→ Kai)
- Design system / CSS / JS (→ Kai)
- Visual assets (→ AGY)
- Architecture / research (→ AGY)

If a Ned issue turns out to be one of those, re-label it and explain in the comment.

## The Recipe

### Component 1: Ned dispatcher

**Location:** `~/.hermes/profiles/orchestrator/scripts/ned_delta_dispatcher.py`
**Cron:** `48876764f897` (every 15 min)
**Run mode:** `no_agent` (script runs, no LLM in the dispatcher)

**Pattern (the right one, post-2026-06-23 fix):**
```python
def invoke_agy(issues: list) -> bool:
    """Write task specs to /tmp/issue-batches/ for the AGY supervisor to pick up."""
    # ... same pattern as the AGY recipe ...
```

The dispatcher **does NOT invoke AGY directly** — it writes to the queue.

### Component 2: Jules for review

Ned review issues (`agent:ned-review` label) are routed to Jules CLI:
```python
def invoke_jules_for_review(issues: list) -> bool:
    """For agent:ned-review issues, pipe to Jules CLI instead."""
```

### Component 3: Ned agent identity

| Property | Value |
|---|---|
| Agent UUID | `6e0400c9-fc04-4868-86e3-f3156821f413` |
| Default workdir | `prismatic` |
| Branch prefix | `ned/` |
| Linear label | `agent:ned` (or `agent:ned-infra`, `agent:ned-code`) |

### Component 4: Lane governance

Ned respects the lane governance installed in each repo:
- `PRISMATIC_ENGINE.yaml` defines what each agent can write to
- The pre-push hook validates the branch + paths before push
- Direct pushes to main are blocked
- Only Fred (staging_governor) can push to deploy-fresh

## Regression log — every Ned breakage

| Date | What broke | Why | Fix |
|---|---|---|---|
| 2026-06-22 | Ned dispatcher returning [SILENT] | `state.type: ["todo", "inProgress"]` invalid enum | `["unstarted", "started", "backlog"]` (commit 3fdfa57) |
| 2026-06-23 (AM) | Ned couldn't find ANY issues | Same enum bug | Same fix |
| 2026-06-23 (PM) | Ned dispatcher timing out on 5-min batch invoke | Subprocess.run(timeout=300) for 20+ issues | Write to /tmp/issue-batches/ instead (commit e0b3b8a) |
| 2026-06-23 (PM) | Ned's lane governance missing from 3 repos | No PRISMATIC_ENGINE.yaml in hd-platform, growthwebdev-knowledge, agentic-swarm-ops | Installed (commits 9460ebd, 874206c5) |

## Recipe for adding a new Ned sub-lane (e.g. agent:ned-test)

1. **Add the label to the AGY supervisor's watch list** (in `agy_sandbox_event_supervisor.py` ~line 419):
   ```python
   labels = [
       "agent:agy",
       "agent:ned",
       "agent:ned-test",  # new
       # ...
   ]
   ```
2. **Update the Ned dispatcher's filter** (`fetch_ned_issues()` in `ned_delta_dispatcher.py`):
   ```python
   QUERY_OPEN_NED_ISSUES = """
   query {
     team(id: "GRO") {
       issues(
         filter: {
           state: { type: { in: ["unstarted", "started", "backlog"] } }
           labels: { name: { in: ["agent:ned", "agent:ned-infra", "agent:ned-code", "agent:ned-test"] } }
         }
       ) { ... }
     }
   }
   """
   ```
3. **Add the label to Linear** (via API or UI)
4. **Test**: file an issue with the new label, verify the dispatcher picks it up

## Recipe for fixing Ned when it breaks

**Step 1: Diagnose.** Check the dispatcher log:
```bash
tail -50 ~/.hermes/profiles/orchestrator/cron/output/48876764f897/$(ls -t ~/.hermes/profiles/orchestrator/cron/output/48876764f897/ | head -1)
```
Look for: "[SILENT]"? "AGY timed out"? "0 issues found"?

**Step 2: Match symptom to regression log.**

**Step 3: Apply the fix. NEVER re-implement — find the existing component that's broken and patch it.**

## Change log

- 2026-06-23 17:00 UTC: Initial doc. Ned architecture regression-tested + documented.
