---
name: factory-code-audit
description: Pattern for auditing factory-shipped code when integrating with autonomous agent work. Use when factory reports a task Done but code isn't in main/deploy-fresh, or when merging autonomous work into a quality pipeline.
---

# Factory Code Audit — When Autonomous Work Doesn't Match Linear State

## When to use

Use this pattern when:
- Linear shows a task as Done but `git log <main-branch>` doesn't show the code
- A factory branch (`agent:*/*` or `feature/*`) has work that wasn't merged
- You discover 20+ tasks marked Done but deploy-fresh is unchanged
- You're integrating autonomous agent output into a quality pipeline

This pattern was discovered during Phase 2 / Gap 7 audit on 2026-06-28.

## The core problem

The factory runs in autonomous mode and marks Linear tasks Done when the worker reports completion. **But "worker reports Done" ≠ "code merged to deploy-fresh"**.

Result: Linear state lies about progress. The team thinks Phase 2 is 80% done when it's actually ~5%.

## Detection signals

Look for these red flags:

```bash
# Red flag 1: Many tasks in Done state, but no recent merges
gh pr list --repo mbgulden/prismatic-engine --state all --limit 20

# Red flag 2: Factory branches exist but aren't merged
git branch -a | grep -E "agent:|feature/"

# Red flag 3: Diff between main and recent factory branches is large
git diff deploy-fresh..agent/<branch> --stat
```

If 2+ red flags fire → audit.

## The 4-step audit pattern

### Step 1: Survey what the factory shipped

```bash
# Get all recently-active factory branches
git log --all --oneline --since="3 days ago" | grep -E "\[Ned\]|\[Fred\]|\[AGY\]"

# Check which branches have new code (vs just triage notes)
for branch in $(git branch -a | grep -E "ned/|fred/|agy/" | head -10); do
  echo "=== $branch ==="
  git log "$branch" --oneline -5
done
```

### Step 2: Verify Linear state vs code state

```bash
# Get all Phase X tasks in Done state
# (use the Linear API script from /tmp/phase2_state.sh pattern)

# For each "Done" task, check if its branch was merged
```

If **20+ tasks are Done but no code merged** → confirm the false-Done pattern.

### Step 3: Document findings in `okf/operations/<scope>-audit.md`

Include:
- **What was found**: specific bugs, missing code, false Done states
- **Severity table**: critical/high/medium/low for each issue
- **Process issues**: how the factory's automation misbehaved
- **Action items**: what to fix and who owns it

Example: `okf/operations/factory-audit-phase2-gap7.md`

### Step 4: Fix the false-Done tasks

```python
# Script: reopen false-Done tasks
import os, json
from urllib.request import Request, urlopen

LINEAR_API_KEY = os.environ["LINEAR_API_KEY"]

# Get Todo state ID
states = gql("{ workflowStates(filter: {name: {eq: \"Todo\"}}) { nodes { id } } }")
todo_id = states["data"]["workflowStates"]["nodes"][0]["id"]

# Reopen each false-Done task
for task_id in false_done_ids:
    mutation = """mutation($id: String!, $input: IssueUpdateInput!) {
        issueUpdate(id: $id, input: $input) { success }
    }"""
    gql(mutation, {"id": task_id, "input": {
        "stateId": todo_id,
        "labelIds": [...task_labels, dispatch_ready_id]
    }})
    
    # Post comment explaining
    gql("""mutation($issueId: String!, $body: String!) {
        commentCreate(input: {issueId: $issueId, body: $body}) { success }
    }""", {
        "issueId": task_id,
        "body": "♻️ Reopened from Done — per factory audit. ..."
    })
```

## Factory behavior audit findings (2026-06-28)

### Process Issue A: False-Done tasks
- **Symptom**: Linear says Done, code not in deploy-fresh
- **Cause**: Automation marks Done on worker report, not on PR merge
- **Fix**: Reopened 20 false-Done tasks in Phase 2 batch
- **Prevention**: Add a Linear webhook on PR merge → only transition to Done then

### Process Issue B: Lane ownership
- **Symptom**: Factory code in wrong directory (e.g. tests/ when in scripts/ lane)
- **Cause**: Pre-push hook catches it but task was already marked Done
- **Fix**: Pre-push hook enforces lane on push (works correctly)
- **Prevention**: None needed — hook is working

### Process Issue C: Plan execution drift
- **Symptom**: 80% Done reported, 5% actually shipped
- **Cause**: Same as Issue A
- **Fix**: Audit regularly; don't trust "Done" alone

## Audit output template

```markdown
# Factory Code Audit — <scope>

**Date:** YYYY-MM-DD
**Auditor:** Fred (orchestrator)
**Scope:** <what you audited>
**Method:** <how you audited>

## Files Audited

### 1. <file> (<N> lines, <state>)

**Status:** <overall assessment>

**Issues found:**
| # | Severity | Location | Finding |
|---|----------|----------|---------|
| 1 | HIGH | line:N | <finding> |

**Strengths:**
- <strength>

## Audit Verdict

**Overall:** <summary>

**Action items:**
- <item 1>
- <item 2>

## Honest Caveats

1. <what you didn't check>
2. <assumptions made>
```

## Honest caveats

1. Audits are point-in-time snapshots — factory state changes continuously
2. I can only audit code I've seen — there may be more branches I missed
3. Reopening tasks may collide with active factory workers — they could mark them Done again before the audit fix takes effect
4. The audit doesn't prevent future false-Done patterns — only the Linear webhook on PR merge would do that

## Examples

- `okf/operations/factory-audit-phase2-gap7.md` — Phase 2 audit (20 false-Done reopened)

## Related skills

- `peer-review-before-merge` — for getting code reviewed before merge
- `autonomous-execution-discipline` — for not stopping to ask what to do