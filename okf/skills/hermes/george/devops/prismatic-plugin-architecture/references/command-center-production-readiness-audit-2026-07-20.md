# Command Center production-readiness audit pattern — 2026-07-20

Use this when Michael asks for a complete Prismatic Engine architectural + UI Command Center production-readiness audit before comparing external reports or creating a Linear master plan.

## Audit planes

Audit all four planes before scoring:

1. **Doctrine/docs** — `docs/north-star.md`, `docs/dashboard-primary-touchpoint.md`, `docs/okf-evidence-map.md`, release/security/public docs, current George handoff.
2. **Source architecture/tests/routes** — Gateway routes, dashboard fetch targets, plugin governance/jobs/artifacts/policy, completed-work integration modules, assigned-agent dispatcher paths, CI workflow scope, stale in-package tests.
3. **Durable runtime/deployment** — systemd `WorkingDirectory`, runtime checkout SHA/status, dirty/untracked source, service units/timers, state-store layout, backup/restore proof, local route/API probes.
4. **Public/operator UI proof** — public routes, browser DOM/console/network, desktop and mobile screenshots/geometry, dashboard tab hydration, public-vs-local API parity, auth exposure boundaries.

Do not average these into a friendly score when any P0 is open. Hosted/public Command Center readiness is `BLOCKED` if public operational APIs are unauthenticated, production source is dirty/untracked, production services depend on mutable dev checkouts, canonical CI scope is failing, or dashboard browser hydration has expected 404s.

## Required P0 checks

- Public Gateway/dashboard auth boundary: CORS is not authentication. Check anonymous access to stateful/read-mutation operational APIs and require a hosted authorization marker before production claims.
- Runtime source durability: durable checkout must be clean and deployed behavior reproducible from a known commit/tag. Preserve dirty runtime diff before reset/cleanup.
- Service durability: every production service/timer should run from the durable runtime checkout, not `/home/ubuntu/work/prismatic-engine` or other mutable multi-agent worktrees.
- Canonical CI scope: run the same unit-test scope as `.github/workflows/test.yml`, and separately check unrestricted collection for orphan in-package tests.
- Dashboard API hydration: inventory all dashboard `fetch()` targets and prove public route parity; expected 404s are dashboard production blockers.
- Browser/mobile proof: use rendered desktop and mobile evidence, not only static CSS/script checks. Watch for horizontal overflow and huge eager-rendered sections.
- State/recovery: inventory SQLite/JSON stores, duplicate state roots, backup timers, and restore/move-machine proof.
- Assigned-agent truth: distinguish resolver/queue markers from live completed result writeback rows; do not claim `ASSIGNED_AGENT_RESULT_WRITEBACK_OK` from a dispatched row with empty result/writeback fields.

## Command Center UI scoring lens

The dashboard is not production-ready just because many governance cards render. Score it as a command center:

```text
What needs attention?
Why?
What decision is required?
What evidence supports it?
What safe action can I take?
What changed afterward?
```

Implementation proof-chain cards should collapse into decision objects and timeline/detail drawers. Default Home should show attention queue, blocked/running/recent decisions, degraded systems, and evidence awaiting review. Huge raw implementation sections, eager Workspace Tree rendering, subtle new cards, and unlabeled no-op/dry-run controls are blockers or release gaps depending on severity.

## Useful closure markers

```text
HOSTED_GATEWAY_AUTHORIZATION_BOUNDARY_OK
CLEAN_DURABLE_RUNTIME_SOURCE_OK
ALL_PRODUCTION_SERVICES_DURABLE_CHECKOUT_OK
CANONICAL_CI_UNIT_SCOPE_GREEN_OK
NO_ORPHAN_TEST_COLLECTION_OK
DASHBOARD_PUBLIC_API_HYDRATION_ZERO_404_OK
WORKSPACE_TREE_BOUNDED_RENDERING_OK
COMMAND_CENTER_MOBILE_VISUAL_QA_OK
CANONICAL_AGENT_GOVERNANCE_READ_MODEL_OK
ASSIGNED_AGENT_RESULT_WRITEBACK_PROVEN_OK
AGY_COMPLETED_WORK_INTEGRATION_GATE_OK
CANONICAL_STATE_DIRECTORY_CONTRACT_OK
BACKUP_RESTORE_MOVE_MACHINE_PROOF_OK
DASHBOARD_VISIBLE_GOLDEN_FLOW_OK
```

## Master-plan epic shape after audit reconciliation

After comparing George/Gemini/etc. reports, create a finding-to-Linear coverage matrix before mutating Linear. Good epic classes:

1. Audit reconciliation and evidence ledger.
2. Hosted security boundary.
3. Durable production source and services.
4. Canonical verification and release integrity.
5. Public dashboard API contract.
6. Operator-first Command Center IA.
7. Workspace/mobile scale.
8. Canonical agent governance and completed-work integration.
9. State, backup, and recovery.
10. Dashboard-primary Golden Flow.
11. North Star ecosystem expansion after P0 foundations.

Do not dispatch Fred and Kai against the same broad blob. Typical split:

```text
Fred → DASHBOARD_PUBLIC_API_HYDRATION_ZERO_404_OK
Kai  → ASSIGNED_AGENT_RESULT_WRITEBACK_PROVEN_OK
George → PRISMATIC_MASTER_AUDIT_COVERAGE_OK
```

## Tool-budget / delivery pitfall

A complete audit can consume the platform's tool-call iteration budget before the final file write. Avoid losing the downloadable deliverable:

1. Create a working report file early after the first evidence pass.
2. Append/update sections incrementally instead of waiting until the end.
3. Keep a short execution digest file separate from the full appendix.
4. Before deeper optional probes, verify the files already exist and contain the latest status/evidence/boundary/next-action skeleton.
5. If the tool budget is exhausted, final chat can still deliver verified `MEDIA:` files rather than only a pasted summary.

Never claim a downloadable `.md` exists unless it was actually written and verified.
