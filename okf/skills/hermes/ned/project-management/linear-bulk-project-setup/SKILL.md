---
name: linear-bulk-project-setup
description: Create or verify comprehensive Linear epic/child-issue trees from a source plan. Use for master plans that must become phased Linear work, especially when the user asks to be comprehensive, avoid gaps, prioritize, and wait for explicit build initiation.
---

# Linear Bulk Project Setup

Use this skill when a document/master plan needs to become a full Linear project tree: phased epics, child issues, priorities, labels, parent-child links, and a final completeness proof.

## Core principle

Bulk Linear setup is a **data mutation job with verification**, not a planning summary. Do not report completion until the Linear tree exists and has been re-read from Linear.

## Required workflow

1. **Read the source plan.** Extract an explicit manifest before mutating Linear:
   - phase/epic title,
   - child issue titles,
   - child count per phase,
   - priorities,
   - owner/agent labels,
   - dependencies or execution order,
   - build/dispatch policy.
2. **Preflight Linear.** Query workspace/team/project/states/labels and existing issues. Reuse exact-title matches. Avoid duplicates.
3. **Create parents first.** Create all phase epics before child tasks so every child can use `parentId`.
4. **Create children idempotently.** Exact-title lookup before every `issueCreate`. Deduplicate `labelIds`; Linear rejects duplicate label IDs.
5. **Assign work to the actual intended owner.** When creating Linear work that *you* intend to execute, assign it to Fred/orchestrator or yourself (Ned) as appropriate — do **not** default to `agent:agy`. Use `agent:agy` only when the task is explicitly a sandbox delegation for AGY, not as a generic “someone should do this” label. If the task is a Ned/Fred handoff, label it `agent:ned` or the correct Fred/orchestrator label and keep the description clear about who should act.
6. **Respect build gates.** If the user says they will initiate the build process later, keep issues in `Todo` and do **not** add `dispatch:ready`.
7. **Forwarded-doc execution trees must carry source context into Linear.** If Michael forwards a `.md` master prompt and asks for epics/tasks that Ned will systematically execute, every created epic/task should reference the forwarded document path/name plus any fixed source SHA / target repo / safety constraints that define the work boundary.
8. **If planning and execution are both requested, execute the first safe tranche immediately after verification.** Do not stop at “tree created” when the user says “once planned, start executing.” Re-read Linear, identify dependency-safe first children, do real repo/API/doc work, then update Linear state/comments with evidence. Keep human-auth blockers in `In Progress` only when there is an active next action and the blocker is named.
9. **Normalize after creation.** Existing automation may move/labeled newly-created issues immediately. Re-query and remove accidental `dispatch:ready` or reset state if the build is gated.
10. **Verify from Linear.** Final proof must come from fresh Linear query results, not local script intent.

### 7a. Ned systematic-execution labeling rule
When the user wants Ned to work the tree systematically:
- label every created issue with `agent:ned`;
- add project/domain labels such as `plugin:pwp` when applicable;
- keep the initial state in `Todo` unless the user explicitly asked you to start execution immediately;
- do **not** bulk-apply `dispatch:ready` just because the tree is complete.

Pitfall: a comprehensive execution tree with missing source-doc context or missing `agent:ned` labeling forces re-triage later and breaks systematic autonomous pickup.

## Verification checklist

- Expected number of epics exists.
- Expected number of child issues exists.
- Every phase parent exists exactly once.
- Every phase has the expected child count.
- Every child has the correct parent.
- Required project/plugin/agent labels exist.
- Owner/agent label matches the intended executor: Fred/orchestrator or Ned for work you plan to do, `agent:agy` only for explicit AGY sandbox delegation.
- No unwanted `dispatch:ready` when build is not yet approved.
- State matches the intended staging state, usually `Todo`.
- Final reply includes links to parent epics and notes any caveat honestly.

## Rate-limit-safe behavior

Linear may return rate-limit failures as HTTP 400 with `RATELIMITED` in the body. If this happens mid-run:

1. Stop pretending the job is complete.
2. Report verified partial counts.
3. Save an idempotent resume script that exact-title checks before creating.
4. Schedule a one-shot retry after the reset window if appropriate.
5. Run a final normalization/verification pass after the retry.

## Common pitfalls

- `labelIds` must be unique.
- Search results can be partial; verify by phase titles and parent/child counts.
- **Linear GraphQL label discovery is team-scoped.** `Query.labels` is not a valid field in this workspace. Read labels from `issue.team.labels`, and request enough pages when available. If a needed agent label is omitted by pagination, read the labels (including IDs) from an existing issue already assigned to that agent rather than guessing an ID.
- Automation can race newly-created tasks and move them out of the desired staging state.
- A local script's success is not proof; Linear readback is proof.
- Do not mark work build-ready if the user explicitly said they will initiate the build.

### Pitfall: scope-correction must propagate to Linear when the source plan came from a stale handoff (2026-08-04)

If the user-driven plan that produced the Linear tree was itself built from a stale system-reminder handoff, the very first child issue's description may bake in wrong scope. In the 2026-08-04 Ned branch triage, the system reminder said "5 repos" but the on-disk `state/current.json` and live state both said 32. The Linear description for GRO-4463 (first child, "Enumerate ned/* branches + worktrees across 5 repos") was wrong from creation.

**Rule: detect scope mismatches before any child work begins, and correct them with one `issueUpdate` on the affected issue's description + a posted comment naming the correction.** Specifically:

1. After creating the Linear tree, before starting any child work, re-read `state/current.json` on disk AND scan the live filesystem for `state/triage/*`, `state/reports/*`, and prior-session artifacts. Compare the plan-derived scope (in the issue descriptions) against what you actually found on disk.
2. If a mismatch exists, update the affected issue description immediately. The 255-char description limit forces brevity, but a single sentence like *"Scope corrected: 32 repos under /home/ubuntu/work, not 5. Re-run scan against existing 2026-07-31 packet (326 active + 1,398 closed-task refs), verify, fill gaps, output state/triage/raw-branches.json."* is enough.
3. Post a comment on the corrected issue with the full reasoning (the comment body has no length limit and is the audit trail). The comment should name the source of the staleness, the actual scope found on disk, and the action taken.
4. The umbrella issue's description is usually correct (it generalizes over children) but verify — if it's wrong, update it too.

Anti-pattern: detecting the scope mismatch, fixing the local plan, but leaving the Linear issue's wrong-scope description in place. Future agents who read Linear first will trust the issue description and repeat the wrong scope.

## Blocking-chain + umbrella pattern (resume-safe multi-step workstreams)

When the user wants a multi-step workstream broken into Linear tasks **and** explicitly wants to be able to start/stop and resume cleanly (e.g. "make a linear task series so we can start and stop if we need to or if you get interrupted"), use this shape instead of plain epic-and-children:

**Shape:**
1. **One umbrella issue** — the project-as-task. Title: "Triage & merge all Ned branches" (etc.). State: Todo. Assignee: the executor (you, not a label). The umbrella represents "this whole effort is done."
2. **N children, one per plan step**, each with a verb-noun title and a Done-when clause in the description. Each child's Done-when clause MUST be verifiable from the Linear description alone (no external state needed).
3. **Blocking relations form a chain**: child[i] blocks child[i+1], so the only legal execution order is the one the chain enforces.
4. **All children block the umbrella**, so the umbrella cannot be marked Done until every step is Done.
5. **The source-of-truth manifest** lives in repo state (e.g. `state/triage/<topic>.md`), not in Linear. Linear holds the *dispatch* state; the manifest holds the *work* state. On resume, the manifest is the resume point — read it, then update Linear to match.

**Why this shape works:**
- Stop/start at any step boundary is safe: the next session reads the manifest and the first non-Done child in the chain, with no human context needed.
- Linear's blocking graph visually communicates the order to anyone reading the project.
- The umbrella issue is the "is this effort closed?" question; children are the "which step is open?" question. Two answers, two surfaces.
- The chain + umbrella combination makes "skip ahead" impossible without editing Linear — which is the desired safety.

**Critical pitfall — the `blocks` relation direction.** See `linear-api-operations`'s pitfalls section for the full trap. Quick reminder: with `issueRelationCreate`, `issueId` is the one doing the blocking. To wire "step N blocks step N+1", the call is:
```graphql
issueRelationCreate(input: {
  issueId: "<step_N+1_id>",       # the LATER step
  relatedIssueId: "<step_N_id>",  # the EARLIER step
  type: "blocks",
})
```
You will get this wrong the first time. Verify by reading back the LATER step's `inverseRelations` — it must list the EARLIER step. If the LATER step shows the EARLIER step in its own `relations` instead, the direction is backwards; delete the relation by UUID and recreate.

**Worked example from 2026-08-04:** Created a "Ned Branch Triage & Merge" project with 9 issues: GRO-4462 (umbrella) + GRO-4463..GRO-4470 (8 children in execution order). Wired 7 chain relations (4463 blocks 4464 ... 4469 blocks 4470) plus 8 umbrella-blockers (each child blocks the umbrella). Total 15 relations. See `references/2026-08-ned-branch-triage-linear-setup.md` for the full transcript including the mistake-and-fix iteration.

## References

- `references/2026-08-ned-branch-triage-linear-setup.md` — resume-safe multi-step workstream pattern (1 umbrella + N children in chain). Includes the mistake-and-fix on `issueRelationCreate` direction, the verification recipe, and why the chain + manifest combination is what makes start/stop actually safe.
- `references/2026-07-pwp-extraction-linear-load.md` — forwarded Markdown prompt → Linear execution-tree pattern: preserve doc path/SHA in every issue, label the whole tree `agent:ned`, keep tasks in `Todo`, and verify via paginated readback.
- `references/pwp-theme-linear-bulk-creation-20260709.md` — concrete PWP Theme 10-epic / 53-child issue creation pattern, including Linear rate-limit recovery and post-create normalization.
- `references/hde-green-state-plan-and-execute-2026-07-18.md` — HDE example for comprehensive green-state epics plus immediate first-tranche execution, Linear progress comments, and OAuth blocker handling.