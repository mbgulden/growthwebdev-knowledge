---
type: Report
title: Prismatic Personal MCP + Journal Portability Package — Next Steps (2026-09-12)
description: Consolidated report on the portable benefits package: journal cron setup (swarmcron tick daemon), personal MCP servers (journal, okf, hd), and what it takes to make all of it work from any LLM chat regardless of harness or platform. Documents what's live, what's portable, what's still harness-coupled, and the exact next steps to close the gap.
tags: [report, prismatic, mcp, journal, cron, swarmcron, portability, llm-chat, platform-agnostic]
status: current
owner: fred
last_verified: 2026-09-12
verified_by: fred
related:
  - audits/prismatic-cron-runner-status-audit-2026-09-12.md
  - audits/journal-system-and-mcp-audit-2026-08-21.md
  - integrations/journal-mcp.md
  - standards/prismatic-independence-map-journal-setup.md
  - standards/cron-alert-output-contract.md
linear_issue: null
git_path: okf/reports/prismatic-portability-package-next-steps-2026-09-12.md
---

# Prismatic Personal MCP + Journal Portability Package — Next Steps

**Author:** Fred · **Date:** 2026-09-12 · **Scope:** The full "personal stack" that makes Michael's journal, OKF knowledge base, and HD data queryable from **any** LLM chat — whether that chat is Hermes (any profile), Claude Desktop, Cursor, Windsurf, a web UI, or a custom client.

---

## 1. What's live today (2026-09-12)

### MCP Servers (read/query surfaces)

| Server | Pattern | Auth | Harness-agnostic? | Registered on |
|---|---|---|---|---|
| `journal` | stdio (hermes-agent venv) | none (local) | ✅ Yes | kai, george, orchestrator |
| `okf` | HTTP :8910 (systemd, bearer) | bearer token | ✅ Yes | all 6 active profiles |
| `hd` | stdio | none | ✅ Yes | all 6 active profiles |
| `gdrive` | stdio (SA key) | service account | ✅ Yes | orchestrator |

All four MCP servers are **harness-agnostic**. They expose standard MCP stdio or HTTP interfaces with no Hermes-specific imports. Any MCP-compatible client can register them.

### Journal Collection Pipeline

| Component | Status | Portable? |
|---|---|---|
| `prismatic-journal-snapshot` CLI | ✅ Live (shebang fixed) | ✅ Pure Python, stdlib + swarmlock |
| `prismatic.journal` module (collector) | ✅ Live | ✅ No harness imports |
| Journal MCP server | ✅ Live | ✅ Stdio, no harness deps |
| Journal corpus | ✅ Live (96 index days) | ✅ File-based, any reader |
| SwarmCron tick daemon | ✅ Live (systemd, 30s tick) | ✅ Python 3.10+, zero external deps |
| SwarmCron store (tasks.json) | ✅ Live | ✅ JSON, any scheduler can read |

### Cron Scheduling (dual-system during switchover)

| System | What it runs | Status |
|---|---|---|
| Hermes native cron (gateway) | All 6 journal jobs + ~30 other jobs | ✅ Live (is_job_runnable fix applied) |
| SwarmCron tick daemon | `journal-snapshot` (hourly) | ✅ Live (first task) |
| Stability monitor | 6h check, silent-when-clean | ✅ Live (cron job, agent-mode) |

### Key Fixes Applied (2026-09-12)

1. `is_job_runnable` backported to hermes-agent-fork `cron/jobs.py` (302 tests pass)
2. `CronSchedulerRegistrationError` backported to `cron/scheduler.py`
3. `prismatic-journal-snapshot` shebang fixed (system python → venv python)
4. SwarmCron installed (v0.3.0, editable) in hermes-agent venv
5. `swarmcron_tick.py` daemon built + `swarmcron-tick.service` systemd unit
6. Journal snapshot registered as swarmcron task, verified end-to-end
7. Gateway restarted with all fixes loaded

---

## 2. What's portable vs. what's still harness-coupled

### The Portable Core (works from any LLM chat, any platform)

These components have **zero harness dependency**. A user on Claude Desktop,
Cursor, a web UI, or any custom MCP client gets the full benefit:

```
┌─────────────────────────────────────────────────────────────┐
│  ANY LLM CHAT (Hermes, Claude, Cursor, Web, Custom)        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ journal  │  │   okf    │  │    hd    │  │ gdrive   │   │
│  │   MCP    │  │   MCP    │  │   MCP    │  │   MCP    │   │
│  │ (stdio)  │  │ (HTTP)   │  │ (stdio)  │  │ (stdio)  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       │              │              │              │        │
│  ┌────▼──────────────▼──────────────▼──────────────▼────┐  │
│  │              LOCAL FILE SYSTEM / API                  │  │
│  │  ~/work/Hermes-Research/journals/  (journal corpus)  │  │
│  │  ~/work/growthwebdev-knowledge/okf/  (OKF docs)     │  │
│  │  HD Engine API (localhost:8000)                     │  │
│  │  Google Drive (via SA key)                          │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

**What this means for Michael:** He can open any LLM chat (his phone's
Hermes Telegram, a desktop Claude session, a web-based AI, a custom script)
and the agent can query "what happened today in the journal," "search OKF
for the Linear rate limit standard," "pull Michael's HD chart," or "read
this Google Doc" — without the agent knowing anything about Hermes profiles,
gateways, or cron jobs.

### What's still harness-coupled (Hermes-specific plumbing)

| Component | Why it's coupled | Portable equivalent |
|---|---|---|
| Hermes native cron (jobs.json) | Per-profile, gateway-managed | SwarmCron tick daemon (any Python host) |
| Journal recap (agent-mode, LLM) | Needs an LLM agent to synthesize | Any LLM with the journal MCP + a prompt |
| Weekly rollup (agent-mode, LLM) | Same | Same |
| Monthly continuity audit (no_agent) | Script + env vars (LINEAR_API_KEY) | Pure script, any cron system |
| Becca personal journal | Profile-specific paths | Separate swarmcron tasks |
| Stability monitor (agent-mode) | Needs LLM for judgment | Could be no_agent script (deterministic) |
| Telegram delivery | Hermes gateway + bot token | Any webhook / notification system |

**The key insight:** The *read surface* (MCP) is already fully portable. The
*write/schedule surface* (cron) is what was harness-coupled. The swarmcron
tick daemon breaks that coupling — it's a standalone Python process that can
run on any machine, with no Hermes gateway required.

---

## 3. The "Personal MCP Setup" — what the user actually needs

For Michael (or anyone) to get the full benefit package in any LLM chat, they
need:

### Step 1: The MCP servers (read/query)

| What | How | Effort |
|---|---|---|
| Journal MCP | 3-line config block in any MCP client | 30 sec |
| OKF MCP | systemd service + bearer token (already running) | 0 (already live) |
| HD MCP | 2-line config block | 15 sec |
| gDrive MCP | SA key + 3-line config | 1 min |

**Total: ~2 minutes of config per new harness.** The servers are already
running. The MCP interface is standard. No code changes needed.

### Step 2: The journal corpus (the data)

The corpus at `~/work/Hermes-Research/journals/` is maintained by:
- Hourly snapshot (swarmcron daemon or Hermes cron)
- Daily recap (LLM agent, 23:59 UTC)
- Weekly rollup (LLM agent, Sun 10:00)

**For a new harness:** The user just needs the MCP registered (Step 1). The
corpus is already being maintained by the swarmcron daemon on the primary
machine. No additional setup needed.

### Step 3: The cron/scheduling (the automation)

| If the user has... | They need... |
|---|---|
| Hermes (any profile) | Native cron jobs (already set up) |
| A bare Python host | `pip install swarmcron` + `swarmcron-tick.py` + systemd unit |
| A cloud VM | Same as bare Python + a process manager (tmux, systemd, supervisor) |
| No host | The swarmcron daemon runs on the primary machine; other hosts just read via MCP |

**The swarmcron tick daemon is the portable cron.** It's a single Python file
(280 lines), zero external dependencies beyond swarmcron itself (which is also
zero-dependency). It can run anywhere Python 3.10+ runs.

### Step 4: The LLM agent (for recap/rollup synthesis)

The daily recap and weekly rollup need an LLM to synthesize the inbox
snapshots into a coherent narrative. This is the one component that
**cannot** be reduced to a pure script — it needs a language model.

**Options:**
1. **Hermes agent-mode cron** (current): The gateway spawns an agent with a
   prompt. Works, but requires a running Hermes gateway.
2. **Any LLM API call**: A script that reads the inbox + event index, calls
   an LLM API (OpenAI, DeepSeek, local Qwen, etc.), and writes the recap.
   This is the **most portable** option — it works from any machine with
   API access.
3. **Manual**: The user (or any agent) can trigger the recap on demand via
   the journal MCP + a prompt. No cron needed.

**Recommendation:** Option 2 (API call script) for the recap, run by the
swarmcron daemon. This makes the entire journal pipeline — snapshot, recap,
rollup — a single portable Python process with no LLM harness dependency.

---

## 4. Next Steps (ordered by impact/effort)

### Now (this week) — ~2 hours

| # | Task | Effort | Impact |
|---|---|---|---|
| 1 | **Verify journal recap fires tonight** (23:59 UTC, first run with is_job_runnable fix) | 0 (automatic) | Proves the agent-mode cron path works |
| 2 | **Wait for 5 stability checks** (swarmcron monitor, every 6h) | 0 (automatic) | Gives confidence for snapshot switchover |
| 3 | **Pause Hermes native snapshot job** (when 5 clean cycles confirmed) | 1 min | Eliminates redundant double-firing |
| 4 | **Register journal MCP on remaining profiles** (fred, ned, autobot) | 15 min | Full swarm coverage for journal queries |

### This month — ~1-2 days

| # | Task | Effort | Impact |
|---|---|---|---|
| 5 | **Build `prismatic-journal-recap` CLI** — script that reads inbox + index, calls LLM API, writes daily recap. Register as swarmcron task (23:59 UTC). | 3-4 hrs | Makes recap portable (no Hermes gateway needed) |
| 6 | **Build `prismatic-journal-weekly` CLI** — same pattern for weekly rollup. | 2 hrs | Same |
| 7 | **Move monthly continuity audit to swarmcron** — pure script, no LLM needed. | 1 hr | One fewer Hermes native cron job |
| 8 | **Decommission remaining Hermes native journal cron jobs** (after 5+ stability checks for each) | 30 min | Single source of truth for journal scheduling |
| 9 | **Document the "new harness" onboarding** — a single OKF doc: "How to get the full personal MCP + journal stack in any LLM chat in < 5 minutes." | 1 hr | The "whole package" benefit, documented |

### This quarter — ~1-2 weeks

| # | Task | Effort | Impact |
|---|---|---|---|
| 10 | **Phase 4: Bridge swarmcron ↔ prismatic authority** — build the adapter that translates swarmcron fires into prismatic `run_once()` calls. | 4-6 hrs | Full execution authority (receipts, idempotency, collision detection) for all cron runs |
| 11 | **Phase 5: Migrate remaining journal jobs** (Becca snapshot/recap/morning-briefing) to swarmcron. | 2-3 hrs | Full journal pipeline on the portable scheduler |
| 12 | **Phase 6: Generalize** — migrate non-journal Hermes native cron jobs to swarmcron (health checks, golden thread review, state sync). | 4-8 hrs | The portable cron runner becomes the *default* scheduler, not just for journal |
| 13 | **PE SQLite migration (GRO-4189)** — replace file-based journal with SQLite. Absorbs the legacy index dedupe gap (G2 from the 08-21 audit). | 1-2 days | Single source of truth, queryable, no file juggling |
| 14 | **Dashboard integration** — Logs → Journals tab in the PE dashboard. | 1-2 days | Visual surface for the journal, not just agent queries |

---

## 5. The "Whole Package" — what the user gets

When all of the above is complete, the user has:

### In ANY LLM chat (Hermes, Claude, Cursor, Web, Custom):

| Capability | MCP | Latency |
|---|---|---|
| "What happened today?" | `journal_latest()` | <1s |
| "Search the journal for X" | `journal_search("X")` | <1s |
| "Read last week's recap" | `journal_read("2026-09-05")` | <1s |
| "Is the journal healthy?" | `journal_freshness()` | <1s |
| "What's the Linear rate limit standard?" | OKF search + read | <1s |
| "Pull my HD chart for Aug 25" | HD MCP | <2s |
| "Read this Google Doc" | gDrive MCP | <2s |

### On the primary machine (automatic, no user action):

| Job | Scheduler | Cadence |
|---|---|---|
| Journal snapshot | swarmcron daemon | hourly |
| Journal recap (LLM) | swarmcron daemon | daily 23:59 UTC |
| Weekly rollup (LLM) | swarmcron daemon | Sun 10:00 |
| Monthly continuity audit | swarmcron daemon | 1st of month 09:00 |
| Becca journal (snapshot/recap) | swarmcron daemon | hourly / daily |
| Stability monitor | swarmcron daemon (or Hermes cron) | every 6h |
| Golden Thread review | swarmcron daemon | daily 17:00 UTC |
| Health check | swarmcron daemon | every 5 min |

### What the user does NOT need:

- ❌ A Hermes gateway running (the swarmcron daemon is standalone)
- ❌ Hermes profiles (the MCP is harness-agnostic)
- ❌ A specific LLM provider (the recap script can call any LLM API)
- ❌ A specific OS (Python 3.10+, any platform)
- ❌ A specific IDE or client (any MCP-compatible tool)

---

## 6. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| SwarmCron daemon crashes | Low (systemd restart) | Journal snapshots stop for ~10s | `Restart=on-failure`, `RestartSec=10` |
| LLM API for recap is down | Medium | Daily recap delayed | Retry with backoff; next-day catch-up |
| Journal corpus grows too large | Low (96 days = ~15MB) | Slow MCP queries | Retention policy (90d or 400d — Michael's decision) |
| MCP server process dies | Low (stdio, per-connection) | That harness loses journal access | Other harnesses unaffected; restart on next query |
| SwarmCron ↔ prismatic authority bridge has bugs | Medium | Receipts not recorded | Phase 4 is isolated; falls back to swarmcron-only receipts |
| OKF MCP bearer token expires | Low (SA key, no expiry) | OKF queries fail | Monitor via stability check |

---

## 7. Decision Points for Michael

| # | Decision | Default if no response | Deadline |
|---|---|---|---|
| 1 | Retention: 90 days (disk-light) or 400 days (full year)? | 400 days (~70 MB/month, trivial on this box) | Before Phase 6 |
| 2 | LLM for recap: which API? (OpenAI, DeepSeek, local Qwen, OpenRouter?) | DeepSeek (already configured, cost-effective) | Before Phase 5 |
| 3 | Switchover snapshot: wait for 5 clean cycles or do it now? | Wait (stability monitor is tracking) | Next 24-48h |
| 4 | Becca journal: migrate to swarmcron or leave on Hermes? | Migrate (same pattern) | Phase 5 |

---

## 8. Key Files and Paths

| Component | Path |
|---|---|
| Journal MCP server | `/home/ubuntu/work/journal-mcp-server/server.py` |
| Journal corpus | `~/work/Hermes-Research/journals/` |
| SwarmCron package | `/home/ubuntu/Github/swarmcron/` (v0.3.0, editable) |
| SwarmCron tick daemon | `/home/ubuntu/work/swarmcron-tick/swarmcron_tick.py` |
| SwarmCron systemd unit | `~/.config/systemd/user/swarmcron-tick.service` |
| SwarmCron store | `~/.hermes/profiles/orchestrator/home/.swarmcron/tasks.json` |
| SwarmCron log | `~/.local/logs/swarmcron/tick.log` |
| Stability check script | `~/.hermes/profiles/orchestrator/scripts/swarmcron-stability-check.py` |
| Prismatic cron runner | `/home/ubuntu/work/prismatic-engine/prismatic/cron_runner.py` |
| Prismatic cron authority | `/home/ubuntu/work/prismatic-engine/prismatic/cron_authority.py` |
| Prismatic cron receipts | `/home/ubuntu/work/prismatic-engine/prismatic/cron_receipts/` |
| OKF MCP service | `okf-mcp.service` (systemd, :8910) |
| OKF knowledge base | `~/work/growthwebdev-knowledge/okf/` |
| Cron audit (today) | `okf/audits/prismatic-cron-runner-status-audit-2026-09-12.md` |
| Journal MCP doc (updated) | `okf/integrations/journal-mcp.md` |
| Independence map | `okf/standards/prismatic-independence-map-journal-setup.md` |

---

*All timestamps UTC. This report is the single source of truth for the
portability package's current state and next steps. Re-run the audit after
each phase completion.*
