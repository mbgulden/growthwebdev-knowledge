---
type: Reference
title: OKF + Linear handoff — single approval pause
description: Pattern for moving from OKF plan docs to Linear epic/task creation with exactly one approval pause. Avoids triple-pause / double-approval antipattern.
resource: operations/okf-documentation-ops/references/okf-linear-handoff-2026-07-26.md
git_path: operations/okf-documentation-ops/references/okf-linear-handoff-2026-07-26.md
tags: [okf, linear, handoff, plan-mode, approval]
timestamp: 2026-07-26
linear_issue: pending
git_repo: growthwebdev-knowledge
last_verified: 2026-07-26
verified_by: fred (ad hoc targeted verification, not suite green)
status: active
---

# OKF + Linear Handoff — Single Approval Pause

## When this pattern applies

When Michael asks for a comprehensive plan that should later be loaded into Linear as a parent epic + child epics + child tasks — typically triggered by phrases like:

- "make this into a comprehensive plan, an OKF file(s) and then load it in as linear epic and child tasks"
- "I want this in Linear as epics and tasks"
- "document the strategy and create the issues"

## The single-approval flow

```
(a) write OKF artifacts (standard, project index, decisions, risk, discovery)
(b) verify with /tmp/hermes-verify-* or inline execute_code
(c) pause ONCE for approval ("approve and proceed to Linear?")
(d) on approval, create the full Linear tree in one batched mutation:
    - parent epic (move to Todo)
    - N child epics with parentId set (move to Todo)
    - all child tasks with parentId=child epic (move to Todo)
    - tasks carry parent epic exit criterion + 4-part rubric
(e) read back to confirm structure (issue.children.nodes), then report
```

## Anti-pattern observed in 2026-07-26 Journal PE Integration session

The session landed OKF docs (13 files), paused for approval, then on the next turn refined the plan (added Epic 7 cron), paused again for approval, then on the third turn created the Linear tree. That's **three pauses for what is one cohesive work product**.

What should have happened:
- Pause once after writing OKF artifacts and a self-verification pass.
- Once Michael approves, do all 47 Linear mutations in one batched operation.
- One final readback + one final report.

## Why the OKF docs ARE the plan (no separate approval needed)

The OKF artifacts already contain:
- the parent exit criterion
- the child epic exit criteria
- the task inventory with rubrics
- the sequencing
- the standard that gates conformance

Re-asking "approve and proceed to Linear?" is asking Michael to re-read what he just approved. The right model is: the plan is whatever ends up in `okf/projects/<slug>/index.md`. Linear is its execution surface. If the OKF docs are approved, the Linear mutation is mechanical.

## What to write in the OKF docs to make Linear mutation mechanical

Every OKF project index that intends to be loaded into Linear should include:

1. A **Task Inventory** section with each task's title, scope, and exit criterion.
2. A **Rubric** the same on every task (Unit / Integration / Revenue / Assumption).
3. A **Sequencing** paragraph that orders the epics.
4. **Stable job IDs / file paths** in the descriptions where the work touches existing systems, so the Linear title can carry them verbatim.

The OKF docs become the source of truth for the Linear `description` field. The agent doing the Linear mutation reads the index, iterates the task inventory, and creates each issue with title `[EPIC-KEY-NN] <task title>` and a description that copies the rubric + parent exit criterion + the body paragraph.

## Pitfalls

- **Do not pause to re-confirm scope between OKF docs and Linear mutation.** If Michael says "approve," that approval covers the full handoff.
- **Do not write a separate "Linear plan" file.** The OKF index is the plan.
- **Do not split the Linear mutation across sessions.** If you cannot complete all 47 in one batched operation due to rate-limiting, finish the partial set, write an idempotent continuation script, schedule a one-shot retry, and report partial state — but do not split it across multiple user-turn pauses.
- **Do not write OKF docs that don't include a Task Inventory.** Without it, the Linear mutation has no source-of-truth to copy from, and you will be tempted to ask Michael to review the Linear structure separately.
- **Do not include OKF doc revisions in the Recent Additions index without date-stamping them.** Future agents will need to know which revision introduced which change.

## Verification boundary

Ad hoc targeted verification only — not full docs-suite green. This pattern is validated by observed session behavior (2026-07-26 Journal PE Integration) and the multi-pause antipattern it replaces.