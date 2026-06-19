---
type: Index
title: Reports
description: Time-stamped reports — audits, incident post-mortems, operational snapshots, and recurring quality measurements.
resource: okf/reports/index.md
tags: [index, reports]
timestamp: 2026-06-19T11:30:00Z
linear_issue: GRO-2039
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/reports/index.md
last_verified: 2026-06-19
verified_by: kai
status: current
---

# Reports

Time-stamped reports. The interesting property of a report is **when it
was made** — its conclusions have a context that may be outdated. Each
report frontmatter carries its `timestamp` and `status` (current /
superseded).

## Compression quality (Ned / Hermes)

| Report | Date | Status |
|---|---|---|
| [Ned Compression Audit 2026-06-14](./ned-audit-2026-06-14.md) | 2026-06-14 | superseded |
| [Ned Compression Audit 2026-06-15](./ned-audit-2026-06-15.md) | 2026-06-15 | superseded |
| [Ned Compression Audit 2026-06-16](./ned-audit-2026-06-16.md) | 2026-06-16 | current |
| [Ned Pipeline Gap Analysis](./ned-pipeline-gap-2026-06-15.md) | 2026-06-15 | current |
| [Compression Improvement Plan](./compression-improvement-plan-2026-06-18.md) | 2026-06-18 | current |
| [Compression Quality Report](./compression-quality-2026-06-18.md) | 2026-06-18 | current |

## Journal-continuity audit

| Report | Date | Status |
|---|---|---|
| [AGY Crack Audit](./journal-continuity-agy-crack-audit.md) | 2026-06-19 | current |
| [Fred Synthesis](./journal-continuity-fred-synthesis.md) | 2026-06-19 | current |
| [Source Inventory (phase 1 shim-smoke)](./journal-continuity-source-inventory.md) | 2026-06-18 | current |

## Swarm operations

| Report | Date | Status |
|---|---|---|
| [Swarm Automation Audit](./swarm-automation-audit-2026-06.md) | 2026-06-12 | current |
| [Triage Report — Latest Snapshot](./triage-latest.md) | (rolling) | superseded weekly |

## Incident reports

| Report | Date | Status |
|---|---|---|
| [Ubersuggest MCP Setup & Recovery](./ubersuggest-mcp-setup-and-recovery-2026-06-19.md) | 2026-06-19 | current |

## Conventions

- One report per file. Naming: `<topic>-<date>.md` (e.g.
  `ned-audit-2026-06-16.md`).
- Superseded reports stay in the bundle with `status: superseded` in
  frontmatter — never delete history, but the index above marks which is
  canonical for any given date.
- The Ned audit `-2`, `-3`, `.slim` variants are NOT preserved here; only
  the canonical (latest non-versioned) snapshot per date.
