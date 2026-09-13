---
type: Audit
title: Prismatic Portability Package — Status & Next Steps (2026-09-12)
description: Consolidated status of the portable benefits package: journal cron (swarmcron tick daemon), personal MCP servers (journal, okf, hd, gdrive), and the path to making all of it work from any LLM chat regardless of harness or platform.
tags: [audit, prismatic, mcp, journal, cron, swarmcron, portability, llm-chat, platform-agnostic]
status: current
owner: fred
last_verified: 2026-09-12
verified_by: fred
linear_issue: null
git_path: okf/audits/prismatic-portability-package-status-2026-09-12.md
related:
  - audits/prismatic-cron-runner-status-audit-2026-09-12.md
  - audits/journal-system-and-mcp-audit-2026-08-21.md
  - integrations/journal-mcp.md
  - standards/prismatic-independence-map-journal-setup.md
---

This document is the **operational status + next-steps report** for the
Prismatic portability package. The full report (with diagrams, risk
register, and decision points) is at:

**`okf/reports/prismatic-portability-package-next-steps-2026-09-12.md`**

(that file is in the `reports/` directory which is outside the current
lane governance scope — it will be moved to the correct location when the
lane config is updated to include `reports/` and `integrations/` for
multi-file PRs.)

## Summary

**What's live (2026-09-12):**
- 4 MCP servers (journal, okf, hd, gdrive) — all harness-agnostic
- Journal corpus: 96 index days, hourly snapshots, daily recaps
- SwarmCron tick daemon: running (systemd, 30s tick, 46MB RSS)
- Journal snapshot: registered as swarmcron task, verified end-to-end
- Stability monitor: 6h cron job, silent-when-clean
- 2 backports to hermes-agent-fork (is_job_runnable, CronSchedulerRegistrationError)

**What's portable:**
- All 4 MCP servers (any MCP client can register)
- Journal corpus (file-based, any reader)
- SwarmCron daemon (any Python 3.10+ host)
- prismatic-journal-snapshot CLI (pure Python)

**What's still harness-coupled:**
- Journal recap/rollup (needs LLM agent — can be made portable via API call script)
- Hermes native cron (being replaced by swarmcron)
- Telegram delivery (Hermes gateway specific)

**Next steps (ordered):**
1. Verify journal recap fires tonight (23:59 UTC)
2. Wait for 5 stability checks → pause Hermes native snapshot job
3. Register journal MCP on remaining profiles (fred, ned, autobot)
4. Build `prismatic-journal-recap` CLI (LLM API call, swarmcron task)
5. Bridge swarmcron ↔ prismatic authority (Phase 4)
6. Migrate remaining journal jobs to swarmcron
7. Generalize to all cron jobs

**Decision points for Michael:**
- Retention: 90d vs 400d
- LLM for recap: which API?
- Switchover timing: wait for 5 cycles or now?

## Key Files

| Component | Path |
|---|---|
| Full portability report | `okf/reports/prismatic-portability-package-next-steps-2026-09-12.md` |
| Cron runner audit | `okf/audits/prismatic-cron-runner-status-audit-2026-09-12.md` |
| Journal MCP doc | `okf/integrations/journal-mcp.md` |
| SwarmCron tick daemon | `/home/ubuntu/work/swarmcron-tick/swarmcron_tick.py` |
| SwarmCron store | `~/.hermes/profiles/orchestrator/home/.swarmcron/tasks.json` |
