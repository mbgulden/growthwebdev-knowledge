---
type: Index
title: Audits
description: Index of cross-project audits with findings + recommendations.
resource: okf/audits/index.md
tags: [index, audits]
timestamp: 2026-06-23T17:00:00Z
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/audits/index.md
last_verified: 2026-06-23
verified_by: fred
status: current
---

# Audits

Cross-project audits — point-in-time assessments of system state with findings + recommendations.

| Audit | OKF location | When |
|---|---|---|
| **Ned's orchestration audit (2026-06-23)** | [`./orchestration-audit-2026-06-23.md`](./orchestration-audit-2026-06-23.md) | 12 bugs found + 9 anti-pattern rules + 9 Linear follow-ups filed |
| **Ned scan triage 2026-06-27 r1** | [`./ned-scan-triage-2026-06-27-r1.md`](./ned-scan-triage-2026-06-27-r1.md) | 10-item misrouted batch refused (0/10 Ned-lane); subset drift 16→10 from 02:35Z triage; GPU 30h+ down |
| **Ned scan triage 2026-06-27 r2** | [`./ned-scan-triage-2026-06-27-r2.md`](./ned-scan-triage-2026-06-27-r2.md) | Clean SUPPRESS post-r59-fix; script feed identical to r1; broader-API drift is noise; GPU ~32h+ down |
| **Ned scan triage 2026-06-27 r3** | [`./ned-scan-triage-2026-06-27-r3.md`](./ned-scan-triage-2026-06-27-r3.md) | Clean SUPPRESS (3rd consecutive identical feed); 0/10 Ned-lane; r59 rule effective across r1–r3 (3/3 noise-free); GPU ~34h+ down — physical inspection still required |
| [Ned audit 2026-06-14](../reports/ned-audit-2026-06-14.md) | (see reports/) | |
| [Ned audit 2026-06-15](../reports/ned-audit-2026-06-15.md) | (see reports/) | |
| [Ned audit 2026-06-16](../reports/ned-audit-2026-06-16.md) | (see reports/) | |
| [Ned pipeline gap 2026-06-15](../reports/ned-pipeline-gap-2026-06-15.md) | (see reports/) | |
| [Swarm automation audit 2026-06](../reports/swarm-automation-audit-2026-06.md) | (see reports/) | |
| [Journal continuity — AGY crack audit](../reports/journal-continuity-agy-crack-audit.md) | (see reports/) | |
| [Journal continuity — Fred synthesis](../reports/journal-continuity-fred-synthesis.md) | (see reports/) | |
| [Journal continuity — source inventory](../reports/journal-continuity-source-inventory.md) | (see reports/) | |

## How to use

- Each audit has findings + recommendations. Most have a "what to do next" section.
- Recurring audits (the Ned ones) track system state over time.
- The orchestration audit (2026-06-23) drove the PWP process overhaul (GRO-2217 through GRO-2230).
