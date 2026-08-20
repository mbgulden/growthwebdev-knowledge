# PE foundation runway after recovery — 2026-07-27

## Trigger

Use this reference when Michael asks whether PE is ready for new foundational Linear tasks after an emergency dashboard/control-plane recovery, or when the team is drifting into one-off repair tickets without an approved target architecture/UX plan.

## Lesson

After production is healthy and the immediate emergency repair is accepted, the trajectory should shift from recovery-driven to foundation-driven. Do not keep feeding PE isolated “repair the next broken seam” prompts unless a live blocker exists. Define the machine and target operator experience first; then use verification to prove implementation matches them.

Keep the governance guardrails:

- event-driven admission only;
- writer/producer cap 1 until proven safe to raise;
- exact task binding and clean worktrees;
- independent exact-head review;
- immutable release proof;
- merge/deploy authorization separated from source acceptance.

Change the sequencing:

- do not create one-off UI nitpick tasks before an approved UX baseline;
- do not sequence from stale handoff history mixed into current state;
- avoid new wrappers, proof schemas, or manual dispatch ceremony when convergence onto the canonical run state machine is the real need;
- populate a Linear foundation project, but put only one issue at a time into Ready/In Progress.

## Recommended PE Foundation 1.0 sequence

1. **Current-State Architecture and Source-of-Truth ADR**
   - Map canonical run state, event admission, producer supervision, independent review, artifact provenance, dashboard projections, merge/release/deploy boundaries, and legacy duplicate state.
   - Deliver an approved architecture ADR and deletion/convergence list.
   - No product rewrite or deployment.

2. **Dashboard Operator UX Master Plan and Approved Baseline**
   - Define operator jobs, information architecture, first-ten-seconds overview, navigation/drill-down model, observe/investigate/approve/cancel/review/recover workflows, desktop/mobile targets, and loading/empty/stale/error/sample states.
   - Audit existing/prior dashboard assets as KEEP / RECONNECT / REFINE / CONSOLIDATE / REMOVE.
   - Preserve good Fred/dashboard adapters; do not invent another shell.
   - Michael approval is the gate before implementation.

3. **Canonical Run Lifecycle Convergence Audit and Repair**
   - Ensure one canonical record owns admitted, claimed, running, review_pending, accepted, repair_required, rejected/cancelled.
   - Supervisor finalizes terminal runs automatically; dashboard projects from that state; status calls cannot downgrade reviewed states; exact-slot cleanup remains fail-closed.

4. **Dashboard-Native Task Control Workflow**
   - Implement approved task admission/status/cancel/review/repair/accept projection and cap-slot visibility.
   - No Linear polling, Telegram polling, generic dispatcher loop, or direct AGY launch.

5. **Artifact and Provenance Contract v1**
   - Standardize artifact ID/type/MIME, producing run, exact commit/tree, input/output lineage, hashes, storage location, review/acceptance status, export rules, and dashboard drill-down.
   - Consolidate existing contracts rather than creating another proof schema.

6. **Plugin SDK and Installed-Distribution Contract v1**
   - Lock manifest, capabilities, connections, MCP/service bridge, API/dashboard hooks, artifact types, policy gates, enable/disable semantics, duplicate/unknown-plugin fail-closed behavior, clean-room wheel and sdist discovery.
   - Goal: removable, deeply integrated plugins; not source-checkout-only demos.

7. **Fresh-Host Install, Recovery, and Rollback Drill**
   - Prove non-editable installed distribution, runtime config injection, state restoration, immutable release activation, rollback, dashboard/event health, and no hidden mutable source checkout dependency.
   - This is the foundation before raising producer concurrency.

## Reporting packet

When summarizing this decision, use Michael’s Prismatic report order:

1. Problem
2. Changed/recommended trajectory
3. Why it matters
4. State/proof
5. Next move
6. IDs/hashes/logs

Compact marker:

```text
RESULT=PASS
SCOPE=post-recovery PE trajectory and foundation runway
AD_HOC_OR_CANONICAL=read-only coordination assessment
NOT_CLAIMING=Linear issues created, cap increase, merge/deploy, GitHub CI green
MARKER=PE_FOUNDATION_PROGRAM_READY
```
