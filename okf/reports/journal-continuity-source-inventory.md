---
type: Report
title: Journal-Continuity Source Inventory (Phase 1 Shim-Smoke)
description: Canonical source inventory for journal-continuity work (phase 1 shim-smoke run). Supersedes initial and phase1-smoke versions.
resource: https://files.growthwebdev.com/raw/hermes-research-reports/journal-continuity-audit/phase1-shim-smoke/source-inventory.md
tags: [report, continuity, inventory, phase1]
timestamp: 2026-06-19T10:52:02Z
linear_issue: null
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/reports/journal-continuity-source-inventory.md
last_verified: 2026-06-19
verified_by: kai
status: current
migrated_from: https://files.growthwebdev.com/raw/hermes-research-reports/journal-continuity-audit/phase1-shim-smoke/source-inventory.md
---

# Journal Continuity Audit Source Inventory — phase1-shim-smoke

Generated: 2026-06-18T06:31:00.097301+00:00

## Coverage
- Dated journals: 13 — https://hermes.growthwebdev.com/artifacts/raw/published/Hermes-Research/journals/2026/06/03.md → https://hermes.growthwebdev.com/artifacts/raw/published/Hermes-Research/journals/2026/06/18.md
- Inbox journals: 14 — https://hermes.growthwebdev.com/artifacts/raw/published/Hermes-Research/journals/inbox/2026-06-03.md → https://hermes.growthwebdev.com/artifacts/raw/published/Hermes-Research/journals/inbox/2026-06-16.md
- Weekly rollups: 2 — https://hermes.growthwebdev.com/artifacts/raw/published/Hermes-Research/journals/weekly/2026-W23.md → https://hermes.growthwebdev.com/artifacts/raw/published/Hermes-Research/journals/weekly/2026-W24.md
- Event indexes: 14 — https://hermes.growthwebdev.com/artifacts/raw/published/Hermes-Research/journals/.index/events-2026-06-03.json → https://hermes.growthwebdev.com/artifacts/raw/published/Hermes-Research/journals/.index/events-2026-06-16.json
- Session files: 11141 — oldest 2026-05-23T07:14:41.756992+00:00 → newest 2026-06-18T06:27:32.030531+00:00

## Relevant cron jobs
- `ce3dd849ede5` — Hermes daily journal snapshot — enabled=True — schedule=every 60m — last=ok — deliver=local — script=journal_snapshot.py
- `d25bf7cc1712` — Hermes daily journal recap — enabled=True — schedule=59 23 * * * — last=ok — deliver=origin — script=None
- `2d5d2f3b02e9` — Morning Briefing — enabled=True — schedule=0 8 * * * — last=ok — deliver=origin — script=None
- `054c987cca7f` — Golden Thread Daily Digest — enabled=True — schedule=0 9 * * * — last=error — deliver=telegram:8190664947 — script=None
- `b7996de54e7e` — Golden Thread Cross-Project Sync — enabled=True — schedule=0 10 * * * — last=ok — deliver=telegram:8190664947 — script=None
- `593cfd88f6fe` — Becca Journal Recap — enabled=True — schedule=59 23 * * * — last=ok — deliver=local — script=None
- `e3af8ef96088` — Becca Morning Briefing — enabled=True — schedule=0 8 * * * — last=ok — deliver=local — script=None
- `df2767acde25` — Becca Journal Snapshot — enabled=True — schedule=0 * * * * — last=ok — deliver=local — script=becca-journal-snapshot.sh
- `63b5dd0ddf98` — Memory Grooming Report — enabled=True — schedule=15 0 * * * — last=ok — deliver=local — script=memory_grooming.py
- `0ce73bbeee4e` — Nightly Autonomous Backlog Worker — enabled=True — schedule=0 4 * * * — last=error — deliver=origin — script=nightly_backlog_delta.py
- `7f5fff8702bc` — Weekly Journal Rollup — enabled=True — schedule=0 10 * * 0 — last=ok — deliver=telegram:8190664947 — script=None
- `0db3cc8a9c40` — AGY Golden Thread Project Review — enabled=True — schedule=0 6,18 * * * — last=ok — deliver=origin — script=agy_golden_thread_delta.py
- `19d229701147` — Daily Golden Thread Research → Strategy → Execution Pipeline — enabled=True — schedule=0 19 * * * — last=ok — deliver=telegram:8190664947 — script=None
- `500749c7949d` — AGY Watchdog — Stuck Detection — enabled=True — schedule=every 5m — last=ok — deliver=local — script=None
- `bff6acfc1f41` — GitHub PR Monitor — open PRs → AGY review pipeline — enabled=True — schedule=0 */4 * * * — last=ok — deliver=origin — script=github_pr_monitor.py
- `e5b153bd08ae` — AGY Resource Monitor — CPU/RAM/Load alerts — enabled=True — schedule=every 5m — last=ok — deliver=local — script=agy_resource_monitor.py
- `d8660aee2fb0` — AGY OAuth Auto-Refresh — every 45min — enabled=True — schedule=every 45m — last=ok — deliver=local — script=agy_oauth_refresh.py
- `2f2da24ba5e3` — 🔮 Second Witness — AGY Prismatic review terminal — enabled=True — schedule=every 30m — last=ok — deliver=local — script=second_witness_agy_proxy.py
- `bee0bd82f2cb` — 🎯 Jules CLI & AGY Milestone Watch — GRO-1589/1590 branches + GRO-1593 review — enabled=True — schedule=every 5m — last=ok — deliver=telegram:8190664947 — script=milestone_watch.sh
- `e59739502d22` — 👀 Comment Trigger Monitor — auto-create AGY tasks from follow-ups — enabled=True — schedule=every 1m — last=ok — deliver=telegram:8190664947 — script=comment_trigger_monitor.py
- `faf8d91da716` — AGY Sandbox Supervisor — event-driven organic scaling — enabled=True — schedule=every 15m — last=error — deliver=local — script=agy_sandbox_event_supervisor_cron.sh
- `eb82b536113c` — Monthly Journal Continuity Audit — enabled=True — schedule=0 9 1 * * — last=None — deliver=local — script=monthly_journal_continuity_audit.py

## Audit instruction
Read this inventory and the plan/sequence docs. Then inspect the listed journals/event indexes only. If a finding requires raw session proof, identify the exact date/session candidate instead of opening all sessions.

Write the crack-audit report to:
- `https://hermes.growthwebdev.com/artifacts/raw/hermes-research-reports/journal-continuity-audit/phase1-shim-smoke/agy-crack-audit.md`
