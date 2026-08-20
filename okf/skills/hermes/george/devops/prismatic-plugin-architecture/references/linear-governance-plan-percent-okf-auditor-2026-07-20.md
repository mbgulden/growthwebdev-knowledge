# Linear governance plan + percent/OKF auditor pattern — 2026-07-20

## Context

After a live dashboard bandaid, Michael asked George to have Kai and Fred execute all plans, create Linear epics/child tasks, recalculate percentage completions, and keep OKF updated as agents merge, with an auditor AO packet.

## Durable pattern

Use this when a Prismatic governance/dashboard bandaid or audit turns into an execution program:

1. **Create real Linear structure only when authorized.** Michael explicitly authorized Linear side effects in this session. Otherwise produce a draft plan/artifact only.
2. **Create class-level epics, not a flat task dump.** Useful epic split:
   - Durable dashboard bandaid closeout.
   - PE Core agent governance and assigned-agent dispatch.
   - OKF evidence ledger + percent recalculation.
   - Branch/worktree preservation + cleanup runway.
   - Dashboard UI completion + portable visual QA.
3. **Every child issue gets an OKF block.** Include Objective, Key Result, Function, Evidence, and Promotion Decision; default promotion decision is `needs_approval` until George audit passes and Michael authorizes real side effects.
4. **Label and parent verification is mandatory.** After GraphQL creation, re-query the project and verify identifiers, parent identifiers, project, and labels. If any issue has stale/wrong labels, repair via `issueUpdate` with the full `labelIds` set. Do not trust the mutation response alone.
5. **Extend the filesystem governance backlog from Linear markers.** Append only the next safe Kai/Fred markers, clear stale `complete` flags, and run the autopacer once. Do not bulk dispatch.
6. **Recalculate percent denominator after adding work.** The monitor must not keep showing 100% after new layers are added. Count `PASS` as complete; show `PARTIAL` as partial/moving, not done. Include new sections in the denominator.
7. **Auditor AO packet.** If Michael says “make the auditor make the AO” and the meaning is ambiguous, state the assumption in the artifact. In this session AO was interpreted as `auditor acceptance-output packet`: audit status, OKF delta, percent delta, proof links, non-claims, and next promotion decision.

## Useful proof shape

```text
COMMAND=create Linear epics/children + extend Kai/Fred governance backlog + clear stale completion flags + run autopacer + recalc OKF/percent monitor + verify issue hierarchy/labels
RESULT=PASS
LOG=/tmp/prismatic-linear-okf-dispatch-verify.log
SCOPE=Prismatic governance dashboard durable closeout, PE Core assigned-agent governance, OKF/auditor percent tracking, cleanup/visual QA runway
AD_HOC_OR_CANONICAL=ad-hoc targeted
NOT_CLAIMING=merge/deploy/production restart/canonical suite/full OKF repo hook/auto-merge/destructive branch cleanup
MARKER=LINEAR_PRISMATIC_GOVERNANCE_EPICS_CREATED_OK
```

## Pitfalls

- Do not put future/dependent tasks all into uncontrolled execution. Linear can hold the whole plan, but Kai/Fred bus execution should remain one lane item at a time.
- Do not mark a section 100% if a marker is `PARTIAL`; count only `PASS` as done and expose partial separately.
- Do not run destructive branch/worktree cleanup from a planning issue. Prepare a reversible dry-run packet and wait for explicit authorization.
- Do not silently interpret ambiguous abbreviations like `AO`; make the assumption explicit in the report.
