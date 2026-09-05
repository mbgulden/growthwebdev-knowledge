---
type: Index
title: Standards
description: Index of cross-project canonical standards.
resource: okf/standards/index.md
tags: [index, standards]
timestamp: 2026-07-29T03:55:00Z
linear_issue: GRO-2039
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/standards/index.md
last_verified: 2026-07-29
verified_by: fred
status: current
---

# Standards

Cross-project canonical standards. Each standard lives in `okf/standards/` and
is referenced by project-specific docs.

| Standard | OKF location | Linear |
|---|---|---|
| Review-loop codification | [`./review-loop-canonical.md`](./review-loop-canonical.md) | GRO-2024 |
| Linear rate-limit codification | [`./linear-rate-limit.md`](./linear-rate-limit.md) | GRO-2008/2010/2020/2034 |
| Webhook security model | [`./webhook-security.md`](./webhook-security.md) | GRO-2057..2062 |
| AGY peer-review standard | [`./agy-peer-review.md`](./agy-peer-review.md) | GRO-2024 |
| Production-grade dispatch | [`./dispatch-production-grade.md`](./dispatch-production-grade.md) | GRO-2057 |
| Event-driven dispatch architecture | [`./dispatch-architecture.md`](./dispatch-architecture.md) | GRO-2047/2048/2050 |
| Prismatic harness coupling taxonomy | [`./prismatic-harness-coupling-taxonomy.md`](./prismatic-harness-coupling-taxonomy.md) | GRO-2039 |
| Prismatic journal-setup independence map | [`./prismatic-independence-map-journal-setup.md`](./prismatic-independence-map-journal-setup.md) | GRO-2039 |
| Agent dispatch architecture (canonical) | [`./agent-dispatch-architecture.md`](./agent-dispatch-architecture.md) | GRO-2047/2048/2050 + the orchestrator process |
| AOT architecture template (the proven reference) | [`./active-oahu-tours-architecture-template.md`](./active-oahu-tours-architecture-template.md) | the reference implementation for any new client site |
| **Prismatic Engine process overhaul** (NEW 2026-06-23) | [`./prismatic-engine-process-overhaul.md`](./prismatic-engine-process-overhaul.md) | 12 bugs + 9 anti-pattern rules from the /yolo session |
| **Cloudflare Access — OKF publisher lockdown** (NEW 2026-06-23) | [`./cloudflare-access-okf-publisher.md`](./cloudflare-access-okf-publisher.md) | 8 hostnames locked + health-check cron + IP update script |
| **PWP ingest spec** | [`./pwp-ingest-spec.md`](./pwp-ingest-spec.md) | GRO-2138 |
| **PWP distill spec** | [`./pwp-distill-spec.md`](./pwp-distill-spec.md) | GRO-2140 |
| **Prismatic Web Plugin — Visual QA Proof Standard** (2026-07-12, current) | [`./pwp-visual-qa-proof-standard.md`](./pwp-visual-qa-proof-standard.md) | GRO-2311 | Portable visual, accessibility, Lighthouse, link, flow, and semantic-image QA proof contract for PWP repos. |
| **Mega-task workflow** (the orchestration process) | [`./mega-task-workflow.md`](./mega-task-workflow.md) | the workflow for "big project" intakes |
| **AGY architecture — The Recipe** (NEW 2026-06-23, regression-tested) | [`./agy-architecture-recipe.md`](./agy-architecture-recipe.md) | GRO-2237 | The canonical AGY reference. Read this BEFORE changing anything AGY. |
| **Ned architecture — The Recipe** (NEW 2026-06-23) | [`./ned-architecture-recipe.md`](./ned-architecture-recipe.md) | GRO-2238 | The canonical Ned reference. |
| **Kai architecture — The Recipe** (NEW 2026-06-23) | [`./kai-architecture-recipe.md`](./kai-architecture-recipe.md) | GRO-2239 | The canonical Kai reference. |
| **UI/UX plan for the PWP** (10 surfaces) | [`./ui-ux-plan.md`](./ui-ux-plan.md) | GRO-2185 |
| **Prismatic staging governance** (2026-07-13, current) | [`./prismatic-staging-governance.md`](./prismatic-staging-governance.md) | GRO-3792 | Governor-only staging branch promotion; repo-local hook precedence; Fred can push `staging`, workers cannot. |
| **Cron alert output contract** (2026-07-13, current) | [`./cron-alert-output-contract.md`](./cron-alert-output-contract.md) | GRO-3792 | Telegram-bound no-agent cron stdout must be empty or complete user-facing Markdown. |
| **Hermes local artifact publisher behind Cloudflare Access** (2026-07-14, current) | [`./hermes-local-artifact-publisher-cloudflare-access.md`](./hermes-local-artifact-publisher-cloudflare-access.md) | GRO-1948 | Durable artifact publishing contract: protected access, secret-scan floor, traceability, retention, and verifier evidence. |
| **OKF worktree reconciliation** (2026-07-15, current) | [`./okf-worktree-reconciliation.md`](./okf-worktree-reconciliation.md) | GRO-3721 | Hidden branch/worktree inventory, extraction, dedupe, quarantine, and cleanup-gate standard. |
| **Prismatic dashboard live proof** (2026-07-15, current) | [`./prismatic-dashboard-live-proof.md`](./prismatic-dashboard-live-proof.md) | GRO-3721 | Live UI/API/browser-console proof contract for dashboard/control-plane claims. |
| **Prismatic Enterprise Governance Scorecard** (2026-07-06, current) | [`./prismatic-enterprise-governance-scorecard.md`](./prismatic-enterprise-governance-scorecard.md) | GRO-3523 | 12-gate enterprise governance rubric aligned with the audit and North Star. |
| **Agent memory governance** (2026-07-18, current) | [`./agent-memory-governance.md`](./agent-memory-governance.md) | none | Selective Hermes profile memory pruning, OKF/skill routing, and future memory write gate. |
| **Cloudflare Pages Direct Uploads deploy pipeline** (2026-07-28, current) | [`./cloudflare-pages-direct-uploads-deploy.md`](./cloudflare-pages-direct-uploads-deploy.md) | none (operator-action for secret) | Canonical pattern for deploying Astro/static sites to CF Pages Direct Uploads projects via GitHub Action + wrangler; replaces manual dashboard deploys. Worked example: mbgulden/sentinelitad.com. |

## What counts as a "standard"

A standard is a cross-project invariant: if you don't follow it, you break
something shared. Examples:

- The review loop (Worker → AGY peer review → Fred verify → Done).
- The LinearBudget gate (every Linear GraphQL call goes through `check_and_consume`).

A standard is *not* a project-specific runbook or architecture decision.
Those go in project `okf/` or `okf/decisions/` respectively.


| **Swarm Coordination Protocol** (2026-07-18, repaired legacy record) | [`./swarm-coordination-protocol.md`](./swarm-coordination-protocol.md) | n/a | Multi-agent active-work, checkpoint, and URL-verification protocol. |
| **Swarm lockfile dual-format spec + sweeper detector discipline** (2026-09-05, current) | [`./swarm-lockfile-dual-format-spec.md`](./swarm-lockfile-dual-format-spec.md) | n/a | swarm_locks.json dict-lease + legacy-list format contract, swarm.js CLI spec, and the rule that alert detectors must never count prose/error output (2026-09-05 phantom stale-locks false-red). |
| **claim-work active registry spec** (2026-07-18, repaired legacy record) | [`./claim-work-spec.md`](./claim-work-spec.md) | n/a | Shared active-work registry spec. |
| **Subagent checkpoint monitor spec** (2026-07-18, repaired legacy record) | [`./subagent-checkpoint-monitor-spec.md`](./subagent-checkpoint-monitor-spec.md) | n/a | Subagent checkpoint monitoring/loss-prevention spec. |
| **URL verification spec** (2026-07-18, repaired legacy record) | [`./url-verification-spec.md`](./url-verification-spec.md) | n/a | URL verification and false-success prevention spec. |
| Hermes Agent Session-Handoff Discipline | [`./hermes-session-handoff-discipline.md`](./hermes-session-handoff-discipline.md) | n/a |
| Hermes Agent Proactive-Execution Discipline | [`./hermes-proactive-execution-discipline.md`](./hermes-proactive-execution-discipline.md) | n/a |
| Hermes Mechanism Probe Recipe | [`./hermes-mechanism-probe-recipe.md`](./hermes-mechanism-probe-recipe.md) | n/a |
| Hermes Agent Projector-Aware Communication Discipline | [`./hermes-projector-aware-communication-discipline.md`](./hermes-projector-aware-communication-discipline.md) | n/a |
| Hermes Agent Verifier-as-Deliverable Discipline | [`./hermes-verifier-as-deliverable-discipline.md`](./hermes-verifier-as-deliverable-discipline.md) | n/a | Verifier ships with the artifact. Four named verifiers promoted to skills. Counter tracks % pre-written. |
| Hermes Agent Next-Action Truth-Source Discipline | [`./hermes-next-action-truth-source-discipline.md`](./hermes-next-action-truth-source-discipline.md) | n/a | Linear is the source; project-registry.json is the cache; chat is downstream. Mutation contract + weekly reconciler. |
| Hermes Agent Memory vs. Skills Boundary Discipline | [`./hermes-memory-skills-boundary-discipline.md`](./hermes-memory-skills-boundary-discipline.md) | n/a | Memory=preferences/facts; skills=procedures; micro-skills=single recipes (1 page max). Applied across all profiles. |
| Hermes Agent Runtime Requirements — Minimum-Viable Surface | [`./hermes-runtime-requirements.md`](./hermes-runtime-requirements.md) | n/a |
