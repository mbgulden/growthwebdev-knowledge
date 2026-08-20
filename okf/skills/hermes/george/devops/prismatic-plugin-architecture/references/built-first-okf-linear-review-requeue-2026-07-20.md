# Built-first OKF → Linear → agent-bus review/requeue program pattern (2026-07-20)

Use when Michael asks George to convert a Prismatic master plan into OKF docs, Linear epics/tasks, assigned-agent batches, and ongoing personal review.

## Trigger

Michael asks to “build the complete plan as OKF reference docs,” create Linear epics/child tasks, assign batches to Fred/Kai/AGY, and personally review completed tasks.

## Durable pattern

1. **Load current Prismatic context and preserve first.** Read the current handoff and relevant OKF/dashboard/agent-bus docs. Treat existing source/runtime/dashboard work as assets to preserve, not as greenfield gaps.
2. **Create a built-first OKF reference set before dispatch.** Include:
   - `built-first-master-plan.md`
   - `built-asset-preservation-map.md`
   - `built-first-program-ledger.md`
   - `agent-review-requeue-contract.md`
   - `always-on-execution-operations.md`
   - README/evidence-map pointers.
3. **Use a real Linear hierarchy, not a flat task dump.** Create epics by wave and child tasks with explicit OKF block:
   - Objective
   - Key Result
   - Function
   - Evidence
   - Promotion Decision
   Every child should default to paused until dependency-safe.
4. **Verify Linear mutations by re-querying.** Check identifiers, parent IDs, project, labels, and state after creation. Mutation success alone is not enough.
5. **Preflight AGY before bulk routing.** If AGY cannot authenticate or produce a one-task canary with result/writeback proof, keep AGY bulk paused and create a blocker issue. Do not reinterpret AGY auth/setup failure as work completion.
6. **Use Fred/Kai bandaid only under bounded concurrency.** While AGY is blocked, dispatch at most one Fred and one Kai filesystem-bus task concurrently, with exact Telegram handles in bus/mirror prompts and `requires_program_review=true`.
7. **Separate deterministic packet audit from substantive George review.** Bus/audit shape checks are not acceptance. George must inspect RESULT.md, prompt/context, artifacts, branch/diff/logs/source/runtime/browser proof as appropriate.
8. **Accept only PASS.** `PARTIAL`, `FAIL`, or `BLOCKED` must not unlock dependents. Create/update a narrow repair child under the same epic, preserve useful artifacts, and place the repair before dependent work.
9. **Snapshot before changing autopacer state/config.** Archive JSON/state/config with hashes, patch narrowly, validate JSON/Python, run the autopacer once, and verify active inbox/claimed/outbox state.
10. **Install durable monitors carefully.** A silent-on-no-change `no_agent=True` monitor can emit one-sentence progress. A separate local reviewer job can inspect completed queue items and requeue repairs. Cron scripts must be profile-relative names under the profile scripts path, not absolute paths.

## Review decision template

```text
COMMAND=<fresh bounded verifier / grouped source-runtime-browser proof>
RESULT=<PASS|PARTIAL|FAIL|BLOCKED>
LOG=/tmp/george-built-first-<issue>-review.log
SCOPE=<exact task scope>
AD_HOC_OR_CANONICAL=<ad-hoc targeted|canonical suite>
NOT_CLAIMING=<merge/deploy/restart/full-suite/etc.>
MARKER=<task marker>
```

Write the durable decision to:

```text
/home/ubuntu/prismatic-agent-bus/program-reviews/<agent>/<task_id>/GEORGE_REVIEW.md
```

Mirror the compact decision into Linear. Only PASS may mark the child done and unlock the immediate dependency-safe next task.

## Pitfalls

- Do not create all tasks as `dispatch:ready`; staged dependency order is part of the product.
- Do not let monitor percentages claim 100% when new backlog layers were added; update denominator/sections.
- Do not treat a public dashboard/API probe, CI result, or deterministic packet-shape audit as canonical full-suite proof.
- Do not merge/deploy/restart/delete/clean worktrees or close PRs from this coordination lane without explicit authorization.
- Do not expose tokens when writing Linear/API helper scripts; clean helper scripts after successful runs.
- Do not rely on absolute cron script paths; Hermes cron wants profile-relative script names.

## Session-specific artifacts observed

The 2026-07-20 run created a built-first OKF branch/worktree, verified a 7-epic/45-child Linear hierarchy, discovered AGY auth was blocked, dispatched one Fred and one Kai bandaid task via filesystem bus, accepted Fred’s runtime map after independent proof, rejected Kai’s dashboard map as PARTIAL, created a repair child, and installed separate monitor/reviewer cron jobs. Keep this as a pattern, not a stale state claim.
