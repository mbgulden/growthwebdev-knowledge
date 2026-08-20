# Model audit reconciliation + control-center audit pattern (2026-07-20)

Use this when Michael provides Gemini/Claude/other-model Prismatic audit docs and asks George to reconcile them into a master plan, especially alongside a dashboard/control-center audit.

## Core lesson

Treat external model audits as **claims to reconcile**, not evidence. Retrieve/export the source docs, preserve hashes, then verify every concrete module/route/security/performance claim against live repo/runtime/browser proof before carrying it into Linear or agent prompts.

A model report can contain useful themes while still being low-trust as a codebase audit. Common contamination signals from the Gemini Prismatic audit session:

- module maps point at non-existent paths such as `app/routers/*` or imagined `prismatic/core/event_bus.py` while the live repo uses different surfaces;
- API routes are invented or prefix-mismatched;
- illustrative snippets are presented as static findings without file/line citations;
- benchmark numbers are given without commands, logs, sample sizes, or environment;
- citations point at unrelated projects with the same/similar name;
- proposed admin controls include placeholder auth or host-level actions before the public auth boundary is closed.

## Reconciliation workflow

1. **Acquire source docs read-only**
   - Export Google Docs via public text/export URL when possible.
   - Save under `reports/sources/`.
   - Record SHA-256 for each source export.
   - State non-claims: not proving authorship, Drive ordering, or private modified time unless separately verified.

2. **Classify trust before planning**
   - Split each report into: verified findings, directionally useful themes, unproven claims, contradicted claims, and unsafe proposals.
   - Do not copy invented classes/routes into task titles as facts.
   - Convert useful themes into real-system language and closure gates.

3. **Run a fresh real-system control-center audit**
   - Public browser render: desktop + mobile screenshots, page/viewport size, overflow, console/resource errors, accessibility semantics.
   - Public route probes for dashboard APIs and local/public parity.
   - Static dashboard inventory: fetch targets, POST controls, no-op/dry-run labels, buttons, scripts/CLI entrypoints.
   - Runtime proof: systemd unit state + `WorkingDirectory` + runtime/dev git cleanliness.
   - Header/auth proof: anonymous access behavior, CSP/HSTS/security headers.
   - Keep POST controls read-only unless Michael explicitly authorizes mutation.

4. **Classify dashboard controls**
   - Real mutations.
   - Read-only visibility.
   - Dry-run/preview/intent-record controls.
   - Accepted no-ops that must be relabeled or implemented.
   - Broken public controls.
   - Missing normal no-CLI operator flows.

5. **Produce two deliverables**
   - Full report with source provenance, trust assessment, reconciliation matrix, UI/control audit, epics, proof receipts, non-claims.
   - Short execution digest with the decision, P0s, exact next sequence, and file list.
   - Verify both artifacts for required headings, line counts, secret-pattern absence, source hashes, and JSON parse when rendered audit data exists.

## P0 findings to look for in this class of audit

- Unauthenticated public operator dashboard/API surfaces.
- Webhook handlers that fail open when a signature header or signing secret is missing.
- Dashboard simulator/demo controls posting to real production webhook/action endpoints.
- Runtime dirty/detached checkout or services using mutable dev worktrees.
- Public/local route mismatches for existing dashboard adapters.
- Real mutation buttons mixed with dry-run/no-op controls without visible boundary.
- Workspace/source preview overexposure.
- Mobile command-center overflow or giant multi-row navigation.

## Recommended closure-gate sequence

Prefer this order unless live evidence says otherwise:

```text
PUBLIC_OPERATOR_AUTHORIZATION_BOUNDARY_OK
→ CLEAN_PINNED_PRODUCTION_RUNTIME_OK
→ DASHBOARD_PUBLIC_ADAPTER_PARITY_OK
→ OPERATOR_HOME_AND_NAVIGATION_OK
→ DASHBOARD_PLUGIN_GOLDEN_FLOW_OK
→ AGY_COMPLETED_WORK_INTEGRATION_GATE_OK
→ GOVERNED_DASHBOARD_ACTION_BROKER_OK
→ PRISMATIC_BACKUP_RESTORE_DRILL_OK
→ GOVERNED_RUNTIME_INTERVENTION_OK
→ MEASURED_EVENTING_AND_LATENCY_BUDGET_OK
→ TARGETED_EXECUTION_BOUNDARY_REVIEW_OK
→ CANONICAL_PRODUCTION_EVIDENCE_LEDGER_OK
```

Do **not** prioritize imagined WebSocket DAGs, universal 100 ms telemetry, cgroup kill switches, or seccomp policy editing before auth, clean runtime, existing dashboard route repair, and normal operator Golden Flow are real.

## Report proof packet

```text
COMMAND=<source export + browser/render/API/runtime/static inventory summary>
RESULT=<PASS|PARTIAL|BLOCKED>
LOG=<full report path + digest path + proof logs>
SCOPE=model-audit reconciliation + public dashboard/control-center audit
AD_HOC_OR_CANONICAL=ad-hoc targeted reconciliation/browser audit
NOT_CLAIMING=production readiness, canonical suite green, authenticated safety, external side effects, POST-control success
MARKER=PRISMATIC_CONTROL_CENTER_NO_CLI_READINESS_BLOCKED
```

## Pitfalls

- Do not call an external model audit “newest” or “authoritative” unless Drive metadata/API access actually proved ordering and authorship.
- Do not treat Google Docs source retrieval as permission to mutate Linear/GitHub or dispatch agents.
- Do not let a large master report be the only handoff; Michael also needs a short execution digest.
- Do not test real POST-backed dashboard controls while claiming the audit is read-only.
- Do not conflate local route 200, public route 200, browser hydration, and production-ready operator workflow.
