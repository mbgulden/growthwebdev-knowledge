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
| [Ned Scan-Triage 2026-06-27 r54](./ned-scan-triage-2026-06-27-r54.md) | 2026-06-27 | Prismatic Engine scanner backlog (54th redundant feed) |
| [Ned Scan-Triage 2026-06-27 r55](./ned-scan-triage-2026-06-27-r55.md) | 2026-06-27 | Prismatic Engine scanner backlog (55th redundant feed; 3 fresh triages posted to GRO-543/542/538) |
| [Ned Scan-Triage 2026-06-27 r56](./ned-scan-triage-2026-06-27-r56.md) | 2026-06-27 | Prismatic Engine scanner backlog (56th redundant feed; 0 fresh triages, GRO-567/564 cross 24h boundary per one-shot escalation rule) |
| [Ned Scan-Triage 2026-06-27 r57](./ned-scan-triage-2026-06-27-r57.md) | 2026-06-27 | Prismatic Engine scanner backlog (57th redundant feed; 0 fresh triages, identical 10-item batch to r55/r56, GPU node ~26.7h down carry-over) |
| [Ned Scan-Triage 2026-06-27 r58](./ned-scan-triage-2026-06-27-r58.md) | 2026-06-27 | Prismatic Engine scanner backlog (58th redundant feed; probe-drift-scope vs script-feed-scope (r46 pitfall re-applied), SUPPRESS verdict, GPU node ~28h+ down on both interfaces, GRO-565 ~12.3 days past IRS deadline) |
| [Ned Scan-Triage 2026-06-27 r59](./ned-scan-triage-2026-06-27-r59.md) | 2026-06-27 | Prismatic Engine scanner backlog (59th redundant feed; r46 pitfall re-applied — probe POST_FRESH_TRIAGE on broader-API drift, but script-feed identical to r58 → corrected SUPPRESS, drift-delta comment posted in-error on anchor before sanity-check, GPU node ~27.4h down) |
| [Ned Scan-Triage 2026-06-27 r60](./ned-scan-triage-2026-06-27-r60.md) | 2026-06-27 | Prismatic Engine scanner backlog (60th redundant feed; SUPPRESS verdict, identical 10-item script feed across r58/r59/r60, r46 pitfall caught on first inspection (avoided r59's error), GPU node ~27.7h down, GRO-565 ~12.5 days past IRS deadline) |

## What counts as an "audit"

A structured investigation that:
- Examines a single target (repo, service, process)
- Produces concrete findings with severity ratings
- Closes with prioritized recommendations

Project-specific audits (e.g. "AOT booking-link audit", "SIAL sale
packet audit") live in the project spoke, not here.

