# Comprehensive self-build readiness audit pattern

Use this reference when Michael asks whether Prismatic can build itself, whether the dashboard is a control plane, or where merge/runtime validation stands.

## Decision framing

Answer with a split verdict, not a single optimism score:

- **Supervised cap-1 self-build:** viable if exact-task, one-producer, independent review, refreshed exact-head CI, merge, and immutable merge-SHA release closeout are proven.
- **Autonomous self-build / cap increase:** blocked until runtime dispatch, legacy autonomous authority, runtime parity, recovery drills, and clean-room distribution are proven.

## Evidence to gather before judging readiness

1. GitHub `main`, latest merge SHA, immutable release HEAD, and release worktree cleanliness.
2. PR/review/CI policy truth versus Prismatic policy truth; GitHub may not enforce independent review even when George requires it.
3. Running services, PIDs, CWDs, cmdlines, import paths, env files, timers, and non-git daemons.
4. Event bus database identity, max rowid, unprocessed count, consumer cursor value, and source query contract.
5. Dashboard browser proof, actual API endpoints, real-data adapters, dry-run/no-op labels, quota/freshness contradictions, and mobile viewport geometry.
6. Distribution/fresh-install status separately from wheel/build proof.
7. Active producer count, generic dispatch pause/cap state, and any legacy automation with merge/deploy authority.

## High-risk readiness blockers surfaced by this audit class

- A systemd service can be `active/running` while functionally blocked if its cursor/checkpoint is ahead of the database it reads. Verify `cursor <= max(rowid)` against the exact DB identity and the query contract before trusting dispatch readiness.
- A legacy merge/deploy daemon can be harmless only because it is wedged on a missing worktree. Treat enabled non-git daemons containing merge/deploy code as **latent autonomous authority**: do not recreate their missing paths; first get explicit pause/disable authorization, snapshot/hash source and state, then port/package safely.
- A dashboard that renders and shows real rows is not automatically a control plane. Classify each surface as live adapter, stale adapter, dry-run/request ledger, no-op/sandbox, or real side-effect endpoint. Request-ledger controls must not be presented as immediate operational controls.
- Mobile proof requires rendered viewport geometry or screenshots. Static CSS is not enough; a 390px viewport with document `scrollWidth > clientWidth` blocks a global mobile-fix claim.
- Capacity dashboards can be contradictory: `partial_coverage` plus stale snapshots must not be labeled as fresh capacity truth.

## Report shape

For large readiness audits, produce both:

1. a full Markdown audit/source map; and
2. a short execution digest/checklist.

Update durable handoff/control state when a newly verified blocker changes the next slice, but label this as coordination-state editing and run a final ad-hoc consistency verifier after the last edit.

## Recommended readiness sequence

1. Contain legacy merge/deploy authority before repairing missing paths around it.
2. Repair dispatch DB/cursor generation safety with atomic backup, dry-run repair, fail-closed health, dashboard red-state proof, and no-agent/no-Linear-write canary.
3. Converge runtime services from preservation sources into reviewed immutable-release-owned code and unit manifests.
4. Refactor dashboard truth model and mobile layout.
5. Canonicalize promotion evidence around machine-readable manifests.
6. Run one real cap-1 self-build canary through the repaired production consumer.
7. Run stale-worker and rollback/roll-forward drills.
8. Prove distribution/clean-room install.
9. Decide cap 2/3 only after consecutive clean supervised cycles.
