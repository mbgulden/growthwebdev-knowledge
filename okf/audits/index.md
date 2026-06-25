---
type: Index
title: Audits
description: Cross-project audits — gap analyses, capability assessments, repo health checks. Findings + recommendations.
resource: okf/audits/index.md
tags: [index, audits]
timestamp: 2026-06-19T11:30:00Z
linear_issue: GRO-2039
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/audits/index.md
last_verified: 2026-06-19
verified_by: kai
status: current
---

# Audits

Cross-project audits. An audit examines a target (a repo, a system, a
process) and produces findings + recommendations. Distinguished from
**reports** by being one-shot investigations rather than recurring
quality measurements.

| Audit | Date | Target |
|---|---|---|
| [AGY Homelab Repo Audit](./agy-audit-homelab-2026-06.md) | 2026-06-15 | `homelab/` |
| [AGY Hermes Agent Manager Audit](./agy-audit-hermes-manager-2026-06.md) | 2026-06-15 | Hermes Agent Manager / Hub |
| [AGY SIAL/ITAD Audit](./agy-audit-sentinel-itad-2026-06.md) | 2026-06-15 | `sentinel-it-asset-logistics/` |
| [GRO-569 Jules Session Monitor Tracker Obsolescence](./ned-gro-569-tracker-obsolescence-2026-06-25.md) | 2026-06-25 | GRO-569 (linear-tracker) — replaced by 3-cron pipeline |
| [GRO-602 Closure (duplicate of GRO-619)](./ned-gro-602-closure-2026-06-25.md) | 2026-06-25 | GRO-602 Backlog — restated GRO-619's task, closed as Done |

## What counts as an "audit"

A structured investigation that:
- Examines a single target (repo, service, process)
- Produces concrete findings with severity ratings
- Closes with prioritized recommendations

Project-specific audits (e.g. "AOT booking-link audit", "SIAL sale
packet audit") live in the project spoke, not here.
