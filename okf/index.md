---
type: Index
title: growthwebdev-knowledge — Master Index
description: Master listing of all OKF concepts in the growthwebdev knowledge hub.
resource: https://github.com/mbgulden/growthwebdev-knowledge
tags: [index, hub, okf]
timestamp: 2026-06-19T11:15:00Z
linear_issue: GRO-2039
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/index.md
last_verified: 2026-06-23
verified_by: fred
status: current
---

# growthwebdev-knowledge — Master Index

This bundle indexes cross-project standards and points to per-project docs in
spoke repositories.

## Current enterprise governance

- [Prismatic OKF hub-and-spoke map](./decisions/prismatic-okf-hub-and-spoke-map.md) — decision record for hub canonical docs plus repo-local breadcrumb map.
- [OKF worktree reconciliation](./standards/okf-worktree-reconciliation.md) — hidden branch/worktree inventory and cleanup-gate standard.
- [Prismatic dashboard live proof](./standards/prismatic-dashboard-live-proof.md) — live UI/API/browser-console proof standard for Prismatic control-plane claims.
- [Prismatic enterprise governance scorecard](./standards/prismatic-enterprise-governance-scorecard.md) — 12-gate enterprise governance rubric for dashboard/control-plane trust.
- [Prismatic staging governance](./standards/prismatic-staging-governance.md) — governor-only `staging` promotion rule and repo-local hook precedence.
- [Cron alert output contract](./standards/cron-alert-output-contract.md) — no-agent Telegram cron stdout must be empty or user-facing.
- [Agent memory governance](./standards/agent-memory-governance.md) — selective Hermes profile memory pruning, OKF/skill routing, and future memory write gate.
- [OKF Source-of-Truth Reconciliation — 2026-07-18](./reports/okf-ssot-reconciliation-2026-07-18.md) — branch/worktree source map, Agent Memory canonicalization, and cleanup gates.
- [Prismatic enterprise governance audit — 2026-07-06](./audits/prismatic-enterprise-governance-audit-2026-07-06.md) — production-grade governance baseline and Linear closeout tree.
- [PWP visual QA proof standard](./standards/pwp-visual-qa-proof-standard.md) — proof-backed browser/accessibility/performance/link/flow standard for PWP repos.

## Current project closeouts

- [Prismatic Engine canonical project index](./projects/prismatic-engine/index.md) — governance/dashboard, dispatcher, Tier 7, OKF drift/recovery, and source-provenance records.
- [Prismatic Governance Dashboard Ingestion Queue repair closeout — 2026-07-14](./projects/prismatic-engine/ingestion-queue-repair-2026-07-14.md) — durable queue ledger, `/api/gateway` aliases, mutation controls, audit timeline, browser/API proof, and drainer caveat.
- [HDE Stripe staging launch closeout — 2026-07-13](./projects/human-design-engine/staging-stripe-launch-2026-07-13.md) — revenue-gate staging bundle, verification boundary, and remaining launch proof.
- [OpenHumanDesignMCP release hardening closeout — 2026-07-13](./projects/open-human-design-mcp/release-hardening-2026-07-13.md) — Dependabot/Ned/Fred handoff PR cleanup and stale-work closure.

## Sections

- [Standards](./standards/index.md) — Cross-project canonical standards
- [Projects](./projects/index.md) — Per-project index docs (pointing at spokes)
- [Decisions](./decisions/index.md) — Architecture decision records
- [Integrations](./integrations/index.md) — External tool integrations (MCP servers, SaaS APIs)
- [Research](./research/index.md) — Cross-project reference research
- [Reports](./reports/index.md) — Time-stamped reports (audits, post-mortems, snapshots)
- [Audits](./audits/index.md) — Cross-project audits with findings + recommendations
- [Sessions](./sessions/index.md) — /yolo session summaries (point-in-time snapshots of major work)
- [Playbooks](./playbooks/index.md) — Step-by-step operational procedures
- [Plugins](./plugins/index.md) — Prismatic Engine plugin reports (81 docs across 6 plugin domains)

## What is OKF?

OKF (Open Knowledge Format) is a vendor-neutral spec for representing knowledge
as plain markdown files with YAML frontmatter. See
[SPEC.md](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md).

Our frontmatter extensions: `linear_issue`, `git_repo`, `git_path`, `last_verified`,
`verified_by`, `status`.

## Maintenance

- Hub `index.md` files: hand-maintained for now. Tier 5c may add a generator.
- Spoke docs: project repos own their own `okf/`. Hub indexes point at them.
- Sync: when a spoke doc moves or is deprecated, update the per-project index here.


## Selectively promoted legacy OKF records

- [Prismatic Web Plugin selective promotion](./projects/prismatic-web-plugin.md) — repaired PWP process/decision docs from PRs #3/#8.
- [Dispatcher fix incident — 2026-06-23](./incidents/2026-06-23-dispatcher-fix.md) — repaired dispatcher package from PR #5; credential-adjacent webhook-chain doc excluded.
- [GRO-2934 deploy-fresh unintegrated-work audit](./audits/gro-2934-deploy-fresh-unintegrated-work.md) — OKF deploy-fresh false-positive audit from PR #12.
- [Swarm Coordination Protocol](./standards/swarm-coordination-protocol.md) — repaired coordination standard from PR #12.
