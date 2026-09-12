---
type: Integration
title: Journal MCP — Prismatic Journal Corpus Query Server
description: Stdio MCP server (5 read-only tools) over the canonical Prismatic journal corpus at ~/work/Hermes-Research/journals — makes the swarm-wide daily/weekly journals and the daily event index queryable by any agent. Same pattern as okf-mcp.
resource: /home/ubuntu/work/journal-mcp-server/server.py
tags: [mcp, journal, prismatic-engine, hermes, query, stdio]
timestamp: 2026-08-20T14:30:00Z
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/integrations/journal-mcp.md
linear_issue: null
last_verified: 2026-08-21
verified_by: kai
status: current
auth_method: none (local stdio, read-only)
---

# Journal MCP — Prismatic Journal Corpus Query Server

## What it is

A stdio MCP server exposing the **canonical Prismatic journal corpus** to any Hermes
agent as 5 read-only tools. Same architecture as `okf-mcp-server` (stdio subprocess,
hermes-agent pipx venv, no credentials, local reads only).

It does NOT write to the journal, does NOT alter the collector, and does NOT serve
the dashboard. It is the **read/query surface** for the corpus that the Prismatic
journal collector (cron) already maintains.

## Corpus it reads (do not move without updating the server)

Root: `/home/ubuntu/work/Hermes-Research/journals`

| Path | What | Notes |
|---|---|---|
| `<year>/<month>/<day>.md` | Daily swarm recap (all agents) | Covers 00:00–06:00 UTC + evening addendum. Sections: Memo, Work Completed, Key Events, Decisions Made, Errors & Issues, Cron Fleet, Sources & Links, Blockers, Follow-ups. |
| `weekly/<YYYY>-Www.md` | Weekly rollup | ISO week. |
| `.index/events-<YYYY-MM-DD>.json` | Daily normalized event index | `cron_run` / `log_error` / `restart` events with idempotency keys, job names, timestamps. |
| `inbox/<YYYY-MM-DD>.md` | Hourly collector snapshots | Raw-ish; lower value than the recap. |
| `.quarantine/` | Malformed/timestamp-less lines | Noisy; not exposed by MCP by design. |
| `latest.md` / `latest-weekly.md` | Symlinks to newest | |

Swarm-wide by design: one corpus covering all profiles (kai, fred, george, ned,
autobot, orchestrator, …). **Becca's personal HD journal is separate and private** at
`~/work/next-step-becca/journals/` and is intentionally NOT in this corpus.

## Tools

| Tool | Args | Returns |
|---|---|---|
| `journal_latest` | — | Latest daily recap, full markdown (60KB cap). |
| `journal_read` | `date` = `YYYY-MM-DD` or `YYYY-Www` | Full markdown for that entry (60KB cap). |
| `journal_list` | `limit=30` | Available daily + weekly dates, newest first. |
| `journal_search` | `query`, `limit=10` | AND-keyword search across recap markdown + event-index summaries, ranked hits with snippets. |
| `journal_freshness` | — | Collector health: last index day, last recap day, index gaps (last 14d), corpus size. |

## Usage

Registered per-profile in `mcp_servers.journal` (stdio). As of 2026-08-21 it is live in
**kai** and **george** profiles; registration for the remaining profiles is tracked as gap
G4 in `okf/audits/journal-system-and-mcp-audit-2026-08-21.md`. Verify live:

```
# direct smoke (no gateway needed)
cd /home/ubuntu/work/journal-mcp-server && \
  /home/ubuntu/.local/share/pipx/venvs/hermes-agent/bin/python -c "
import server; print(server.journal_freshness())"

# in-session: call journal_freshness() first to confirm the collector is current,
# then journal_search() to locate an entry, then journal_read() for the full text.
```

**Discipline:** always call `journal_freshness()` before treating journal content as
*current*. A stale collector (index gaps, old `last_daily_recap`) means the corpus may
not reflect today — say so rather than presenting old content as live state.

## Ownership / non-goals

- **Owns:** the read/query contract over the corpus.
- **Does not own:** collection (Prismatic journal collector cron), the dashboard
  Logs→Journals UI (GRO-4189/4190, paused), retention policy, quarantine classification.
- **Next step (PE side, Fred):** PR #382 build-gate fix + GRO-4189 read API so the
  dashboard consumes the same corpus. The MCP is the agent-side surface until then.

## Known corpus wounds (inherited, not fixed by this MCP)

- Legacy index (pre-incremental, ~before 07-09) has no stable dedupe keys — history, not evidence.
- Quarantine is a noisy dump (~5 MB, mostly non-timestamped log lines).
- Retention ambiguity: code prunes 90 days, governance says 400.
- Oversized pre-fix recap artifacts (daily 672 KB / weekly 2.7 MB) retained as backups.

See `okf/reports/journal-continuity-agy-crack-audit.md` and the 2026-07-23
continuity audit + unification plan (orchestrator deliveries) for the full remediation.

## Related

- [Hermes Memory vs Skills Boundary Discipline](../standards/hermes-memory-skills-boundary-discipline.md) — where the journal sits in the memory/skills/OKF split (the journal = the evidence layer).
- [Prismatic Journal-Setup Independence Map](../standards/prismatic-independence-map-journal-setup.md)
- [OKF MCP](../standards/okf-skill-hub.md) — the sibling read-only MCP this copies its pattern from.
- [Journal System & MCP — End-to-End Audit (2026-08-21)](../audits/journal-system-and-mcp-audit-2026-08-21.md) — live-verified system audit; 9 gaps with fill steps (retention G1 needs Michael's 90d-vs-400d decision).
